"""
CRUD operations for all database models.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from backend.db.models import (
    Job, Application, ApplicationHistory,
    TrackedCompany, Notification, CoverLetter, ScanLog
)


# ─── Jobs ──────────────────────────────────────────────────────────────────────

def get_jobs(
    db: Session,
    platform: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    min_score: float = 0,
    max_score: float = 100,
    sort_by: str = "match_score",
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Job], int]:
    q = db.query(Job).filter(Job.is_active == True)
    if platform and platform != "all":
        q = q.filter(Job.platform == platform.lower())
    if location and location != "all":
        q = q.filter(Job.location.ilike(f"%{location}%"))
    if search:
        q = q.filter(
            or_(Job.title.ilike(f"%{search}%"), Job.company.ilike(f"%{search}%"))
        )
    q = q.filter(and_(Job.match_score >= min_score, Job.match_score <= max_score))
    sort_col = {
        "match_score": Job.match_score,
        "scraped_at": Job.scraped_at,
        "company": Job.company,
    }.get(sort_by, Job.match_score)
    total = q.count()
    jobs = q.order_by(desc(sort_col)).offset((page - 1) * per_page).limit(per_page).all()
    return jobs, total


def get_job(db: Session, job_id: str) -> Optional[Job]:
    return db.query(Job).filter(Job.id == job_id).first()


def upsert_job(db: Session, job_data: dict) -> Job:
    """Insert or update a job (deduplicate by URL)."""
    existing = db.query(Job).filter(Job.url == job_data["url"]).first()
    if existing:
        for k, v in job_data.items():
            if k != "id":
                setattr(existing, k, v)
        db.commit()
        return existing
    job = Job(**job_data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def save_job(db: Session, job_id: str, saved: bool) -> Optional[Job]:
    job = get_job(db, job_id)
    if job:
        job.is_saved = saved
        db.commit()
    return job


def count_jobs_today(db: Session) -> int:
    today = datetime.utcnow().date()
    return db.query(Job).filter(func.date(Job.scraped_at) == today).count()


def get_top_matches(db: Session, limit: int = 5) -> list[Job]:
    return (
        db.query(Job)
        .filter(Job.is_active == True, Job.match_score > 0)
        .order_by(desc(Job.match_score))
        .limit(limit)
        .all()
    )


def get_avg_match_score(db: Session) -> float:
    result = db.query(func.avg(Job.match_score)).filter(Job.match_score > 0).scalar()
    return round(result or 0.0, 1)


# ─── Applications ──────────────────────────────────────────────────────────────

def get_applications(
    db: Session,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[Application], int]:
    q = db.query(Application)
    if status:
        q = q.filter(Application.status == status)
    total = q.count()
    apps = q.order_by(desc(Application.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    return apps, total


def get_application(db: Session, app_id: str) -> Optional[Application]:
    return db.query(Application).filter(Application.id == app_id).first()


def get_application_by_job(db: Session, job_id: str) -> Optional[Application]:
    return db.query(Application).filter(Application.job_id == job_id).first()


def create_application(db: Session, job_id: str, status: str = "saved", notes: str = "") -> Application:
    app = Application(
        id=str(uuid.uuid4()),
        job_id=job_id,
        status=status,
        notes=notes,
        applied_date=datetime.utcnow() if status == "applied" else None,
    )
    db.add(app)
    # Record history
    hist = ApplicationHistory(application_id=app.id, old_status=None, new_status=status)
    db.add(hist)
    db.commit()
    db.refresh(app)
    return app


def update_application(db: Session, app_id: str, updates: dict) -> Optional[Application]:
    app = get_application(db, app_id)
    if not app:
        return None
    old_status = app.status
    for k, v in updates.items():
        if v is not None:
            setattr(app, k, v)
    app.updated_at = datetime.utcnow()
    if "status" in updates and updates["status"] != old_status:
        if updates["status"] == "applied":
            app.applied_date = datetime.utcnow()
        hist = ApplicationHistory(
            application_id=app_id,
            old_status=old_status,
            new_status=updates["status"],
        )
        db.add(hist)
    db.commit()
    db.refresh(app)
    return app


def delete_application(db: Session, app_id: str) -> bool:
    app = get_application(db, app_id)
    if not app:
        return False
    db.query(ApplicationHistory).filter(ApplicationHistory.application_id == app_id).delete()
    db.delete(app)
    db.commit()
    return True


def get_application_history(db: Session, app_id: str) -> list[ApplicationHistory]:
    return (
        db.query(ApplicationHistory)
        .filter(ApplicationHistory.application_id == app_id)
        .order_by(ApplicationHistory.changed_at)
        .all()
    )


def get_application_stats(db: Session) -> dict:
    statuses = ["saved", "applied", "in_review", "interview", "offer", "rejected"]
    stats = {}
    for s in statuses:
        stats[s] = db.query(Application).filter(Application.status == s).count()
    week_ago = datetime.utcnow() - timedelta(days=7)
    stats["applied_this_week"] = (
        db.query(Application)
        .filter(Application.applied_date >= week_ago)
        .count()
    )
    return stats


# ─── Notifications ────────────────────────────────────────────────────────────

def get_notifications(
    db: Session, page: int = 1, per_page: int = 20
) -> tuple[list[Notification], int]:
    total = db.query(Notification).count()
    notifs = (
        db.query(Notification)
        .order_by(desc(Notification.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return notifs, total


def get_unread_count(db: Session) -> int:
    return db.query(Notification).filter(Notification.is_read == False).count()


def create_notification(
    db: Session, type: str, title: str, message: str, data: dict = None
) -> Notification:
    n = Notification(
        type=type,
        title=title,
        message=message,
        data=json.dumps(data or {}),
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def mark_notification_read(db: Session, notif_id: int) -> Optional[Notification]:
    n = db.query(Notification).filter(Notification.id == notif_id).first()
    if n:
        n.is_read = True
        db.commit()
    return n


def mark_all_read(db: Session):
    db.query(Notification).filter(Notification.is_read == False).update({"is_read": True})
    db.commit()


def delete_notification(db: Session, notif_id: int) -> bool:
    n = db.query(Notification).filter(Notification.id == notif_id).first()
    if n:
        db.delete(n)
        db.commit()
        return True
    return False


# ─── Tracked Companies ────────────────────────────────────────────────────────

def get_tracked_companies(db: Session) -> list[TrackedCompany]:
    return db.query(TrackedCompany).order_by(TrackedCompany.name).all()


def track_company(db: Session, name: str, domain: str = "", notify: bool = True) -> TrackedCompany:
    existing = db.query(TrackedCompany).filter(TrackedCompany.name == name).first()
    if existing:
        return existing
    company = TrackedCompany(name=name, domain=domain, notify=notify)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def untrack_company(db: Session, company_id: int) -> bool:
    c = db.query(TrackedCompany).filter(TrackedCompany.id == company_id).first()
    if c:
        db.delete(c)
        db.commit()
        return True
    return False


def update_company(db: Session, company_id: int, updates: dict) -> Optional[TrackedCompany]:
    c = db.query(TrackedCompany).filter(TrackedCompany.id == company_id).first()
    if c:
        for k, v in updates.items():
            if v is not None:
                setattr(c, k, v)
        db.commit()
    return c


# ─── Cover Letters ────────────────────────────────────────────────────────────

def get_cover_letters(db: Session) -> list[CoverLetter]:
    return db.query(CoverLetter).order_by(desc(CoverLetter.created_at)).all()


def get_cover_letter(db: Session, cl_id: str) -> Optional[CoverLetter]:
    return db.query(CoverLetter).filter(CoverLetter.id == cl_id).first()


def get_cover_letter_by_job(db: Session, job_id: str) -> Optional[CoverLetter]:
    return db.query(CoverLetter).filter(CoverLetter.job_id == job_id).first()


def create_cover_letter(db: Session, job_id: str, content: str) -> CoverLetter:
    cl = CoverLetter(id=str(uuid.uuid4()), job_id=job_id, content=content)
    db.add(cl)
    db.commit()
    db.refresh(cl)
    return cl


def update_cover_letter(db: Session, cl_id: str, content: str) -> Optional[CoverLetter]:
    cl = get_cover_letter(db, cl_id)
    if cl:
        cl.content = content
        cl.updated_at = datetime.utcnow()
        db.commit()
    return cl


def delete_cover_letter(db: Session, cl_id: str) -> bool:
    cl = get_cover_letter(db, cl_id)
    if cl:
        db.delete(cl)
        db.commit()
        return True
    return False


# ─── Scan Logs ────────────────────────────────────────────────────────────────

def create_scan_log(db: Session, **kwargs) -> ScanLog:
    log = ScanLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_recent_scan_logs(db: Session, limit: int = 10) -> list[ScanLog]:
    return (
        db.query(ScanLog)
        .order_by(desc(ScanLog.started_at))
        .limit(limit)
        .all()
    )
