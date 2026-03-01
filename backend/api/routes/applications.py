"""
Applications API routes — CRUD + Kanban status transitions.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.db import crud, schemas

router = APIRouter(prefix="/applications", tags=["applications"])


def _enrich_application(app, db: Session) -> dict:
    """Join job info onto application response."""
    job = crud.get_job(db, app.job_id) if app.job_id else None
    return {
        "id": app.id,
        "job_id": app.job_id,
        "status": app.status,
        "applied_date": app.applied_date,
        "cover_letter": app.cover_letter,
        "notes": app.notes,
        "follow_up_date": app.follow_up_date,
        "created_at": app.created_at,
        "updated_at": app.updated_at,
        "job_title": job.title if job else "Unknown",
        "job_company": job.company if job else "Unknown",
        "job_url": job.url if job else "",
        "job_platform": job.platform if job else "",
        "job_location": job.location if job else "",
        "job_match_score": job.match_score if job else 0,
        "job_logo": job.company_logo_url if job else "",
    }


@router.get("")
def list_applications(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    apps, total = crud.get_applications(db, status=status, page=page, per_page=per_page)
    return {
        "applications": [_enrich_application(a, db) for a in apps],
        "total": total,
        "page": page,
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_application_stats(db)


@router.post("")
def create_application(req: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    # Check job exists
    job = crud.get_job(db, req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Avoid duplicate
    existing = crud.get_application_by_job(db, req.job_id)
    if existing:
        return _enrich_application(existing, db)
    app = crud.create_application(db, req.job_id, req.status, req.notes)
    return _enrich_application(app, db)


@router.get("/{app_id}")
def get_application(app_id: str, db: Session = Depends(get_db)):
    app = crud.get_application(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return _enrich_application(app, db)


@router.patch("/{app_id}")
def update_application(app_id: str, req: schemas.ApplicationUpdate, db: Session = Depends(get_db)):
    updates = req.model_dump(exclude_none=True)
    app = crud.update_application(db, app_id, updates)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return _enrich_application(app, db)


@router.delete("/{app_id}")
def delete_application(app_id: str, db: Session = Depends(get_db)):
    if not crud.delete_application(db, app_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted"}


@router.get("/{app_id}/timeline")
def get_timeline(app_id: str, db: Session = Depends(get_db)):
    history = crud.get_application_history(db, app_id)
    return [
        {
            "id": h.id,
            "old_status": h.old_status,
            "new_status": h.new_status,
            "changed_at": h.changed_at,
            "note": h.note,
        }
        for h in history
    ]
