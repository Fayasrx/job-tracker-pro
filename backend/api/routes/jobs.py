"""
Jobs API routes.
"""

import json
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.db import crud, schemas
from backend.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=schemas.JobListOut)
def list_jobs(
    platform: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_score: float = Query(0),
    max_score: float = Query(100),
    sort_by: str = Query("match_score"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    jobs, total = crud.get_jobs(
        db, platform=platform, location=location, search=search,
        min_score=min_score, max_score=max_score, sort_by=sort_by,
        page=page, per_page=per_page,
    )
    return {"jobs": jobs, "total": total, "page": page, "per_page": per_page}


@router.get("/daily-digest")
def daily_digest(db: Session = Depends(get_db)):
    """Get today's job summary."""
    today_count = crud.count_jobs_today(db)
    top = crud.get_top_matches(db, limit=5)
    return {
        "today_count": today_count,
        "avg_score": crud.get_avg_match_score(db),
        "top_matches": [
            {"id": j.id, "title": j.title, "company": j.company,
             "match_score": j.match_score, "url": j.url}
            for j in top
        ],
    }


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/search")
async def search_jobs(
    request: schemas.SearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger a new job scan (runs in background)."""
    background_tasks.add_task(
        _run_scan_sync, request.roles, request.locations,
        request.platforms, request.max_per_platform
    )
    return {"message": "Job scan started in background. Check notifications for updates."}


async def _run_scan_sync(roles, locations, platforms, max_per):
    """Helper to run async scan from background task."""
    from backend.core.database import SessionLocal
    db = SessionLocal()
    try:
        await job_service.run_job_scan(db, roles=roles, locations=locations,
                                        platforms=platforms, max_per_platform=max_per)
    finally:
        db.close()


@router.post("/{job_id}/save")
def save_job(job_id: str, db: Session = Depends(get_db)):
    job = crud.save_job(db, job_id, True)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job saved"}


@router.delete("/{job_id}/save")
def unsave_job(job_id: str, db: Session = Depends(get_db)):
    job = crud.save_job(db, job_id, False)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job unsaved"}
