"""
APScheduler setup — daily job scans, digest notifications, follow-up reminders, cleanup.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.core.config import settings

log = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def _run_async(coro):
    """Run an async function from a sync scheduler job."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)
    finally:
        loop.close()


def daily_scan_job():
    """Daily full scan of all platforms."""
    log.info("[Scheduler] Starting daily job scan...")
    from backend.core.database import SessionLocal
    from backend.services.job_service import run_job_scan

    db = SessionLocal()
    try:
        result = _run_async(run_job_scan(db))  # type: ignore
        log.info(f"[Scheduler] Daily scan complete: {result}")
    except Exception as e:
        log.error(f"[Scheduler] Daily scan failed: {e}")
    finally:
        db.close()


def daily_digest_job():
    """Send daily digest notification."""
    log.info("[Scheduler] Sending daily digest...")
    from backend.core.database import SessionLocal
    from backend.db import crud
    from backend.services.notification_service import notify

    db = SessionLocal()
    try:
        today_count = crud.count_jobs_today(db)
        avg = crud.get_avg_match_score(db)
        top = crud.get_top_matches(db, limit=3)
        high_matches = [j for j in top if j.match_score >= 80]
        msg = f"Found {today_count} jobs today. Avg match: {avg:.0f}%. {len(high_matches)} high-match jobs!"
        _run_async(
            notify(db, "daily_digest", "📊 Daily Job Digest", msg,
                   {"today_count": today_count, "avg": avg})
        )
    except Exception as e:
        log.error(f"[Scheduler] Digest failed: {e}")
    finally:
        db.close()


def follow_up_reminder_job():
    """Remind about applications that need follow-up."""
    log.info("[Scheduler] Checking follow-up reminders...")
    from backend.core.database import SessionLocal
    from backend.db.models import Application
    from backend.services.notification_service import notify
    from sqlalchemy import and_

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        # Applications applied 7+ days ago, still in applied/in_review
        cutoff = now - timedelta(days=7)
        apps = (
            db.query(Application)
            .filter(
                and_(
                    Application.applied_date <= cutoff,
                    Application.status.in_(["applied", "in_review"]),
                )
            )
            .limit(5)
            .all()
        )
        for app in apps:
            from backend.db.models import Job
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if job:
                _run_async(
                    notify(
                        db, "follow_up",
                        "⏰ Follow-up Reminder",
                        f"You applied to {job.title} at {job.company} 7+ days ago. Consider following up!",
                        {"application_id": app.id, "job_id": job.id},
                    )
                )
    except Exception as e:
        log.error(f"[Scheduler] Follow-up check failed: {e}")
    finally:
        db.close()


def cleanup_old_jobs_job():
    """Remove jobs older than 30 days."""
    log.info("[Scheduler] Cleaning up old jobs...")
    from backend.core.database import SessionLocal
    from backend.db.models import Job

    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        deleted = db.query(Job).filter(Job.scraped_at < cutoff, Job.is_saved == False).delete()
        db.commit()
        log.info(f"[Scheduler] Cleaned up {deleted} old jobs")
    except Exception as e:
        log.error(f"[Scheduler] Cleanup failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Register all jobs and start the scheduler."""
    # Parse scan time
    scan_h, scan_m = settings.DAILY_SCAN_TIME.split(":")
    digest_h, digest_m = settings.DIGEST_TIME.split(":")

    scheduler.add_job(
        daily_scan_job, CronTrigger(hour=int(scan_h), minute=int(scan_m)),
        id="daily_scan", replace_existing=True,
    )
    scheduler.add_job(
        daily_digest_job, CronTrigger(hour=int(digest_h), minute=int(digest_m)),
        id="daily_digest", replace_existing=True,
    )
    scheduler.add_job(
        follow_up_reminder_job, CronTrigger(hour=10, minute=0),
        id="follow_up_reminder", replace_existing=True,
    )
    scheduler.add_job(
        cleanup_old_jobs_job, CronTrigger(day_of_week="sun", hour=0, minute=0),
        id="cleanup_old_jobs", replace_existing=True,
    )

    scheduler.start()
    log.info("[Scheduler] Started — daily scan at %s, digest at %s", settings.DAILY_SCAN_TIME, settings.DIGEST_TIME)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
