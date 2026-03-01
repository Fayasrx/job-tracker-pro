"""
Analytics service — dashboard stats, funnel, activity feed.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.db.models import Job, Application, Notification, ScanLog
from backend.db import crud


def get_dashboard_stats(db: Session) -> dict:
    """Compute all dashboard stats in one pass."""
    total_jobs = db.query(Job).filter(Job.is_active == True).count()
    today_jobs = crud.count_jobs_today(db)
    avg_score = crud.get_avg_match_score(db)
    top_matches = crud.get_top_matches(db, limit=5)

    # Application funnel
    app_stats = crud.get_application_stats(db)

    # Applications this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    apps_this_week = (
        db.query(Application)
        .filter(Application.applied_date >= week_ago)
        .count()
    )
    pending = (
        db.query(Application)
        .filter(Application.status.in_(["applied", "in_review"]))
        .count()
    )
    interviews = (
        db.query(Application)
        .filter(Application.status == "interview")
        .count()
    )

    # Recent activity (last 10 notifications)
    recent_notifs = (
        db.query(Notification)
        .order_by(desc(Notification.created_at))
        .limit(10)
        .all()
    )
    activity = [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in recent_notifs
    ]

    return {
        "total_jobs_today": today_jobs,
        "total_jobs": total_jobs,
        "avg_match_score": avg_score,
        "applications_this_week": apps_this_week,
        "pending_responses": pending,
        "interviews_scheduled": interviews,
        "top_matches": [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "platform": j.platform,
                "match_score": j.match_score,
                "company_logo_url": j.company_logo_url,
                "url": j.url,
            }
            for j in top_matches
        ],
        "funnel": {
            "found": total_jobs,
            "saved": app_stats.get("saved", 0),
            "applied": app_stats.get("applied", 0),
            "interview": app_stats.get("interview", 0),
            "offer": app_stats.get("offer", 0),
        },
        "recent_activity": activity,
    }
