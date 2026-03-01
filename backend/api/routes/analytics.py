"""
Analytics API routes — dashboard stats + trends.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.analytics_service import get_dashboard_stats
from backend.db import crud

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard_stats(db)


@router.get("/weekly")
def weekly_report(db: Session = Depends(get_db)):
    app_stats = crud.get_application_stats(db)
    scan_logs = crud.get_recent_scan_logs(db, limit=7)
    return {
        "applications": app_stats,
        "scan_history": [
            {
                "platform": s.platform,
                "jobs_found": s.jobs_found,
                "new_jobs": s.new_jobs,
                "status": s.status,
                "started_at": s.started_at,
            }
            for s in scan_logs
        ],
    }
