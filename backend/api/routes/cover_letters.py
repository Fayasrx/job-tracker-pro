"""
Cover Letters API routes — generate with Gemini + CRUD.
"""

import json
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import get_db
from backend.db import crud, schemas

ROOT = Path(__file__).parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

router = APIRouter(prefix="/cover-letters", tags=["cover-letters"])


class GenerateRequest(BaseModel):
    job_id: str


@router.post("/generate")
async def generate_cover_letter(req: GenerateRequest, db: Session = Depends(get_db)):
    """Generate a cover letter for a job using Gemini AI."""
    job_row = crud.get_job(db, req.job_id)
    if not job_row:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if one already exists
    existing = crud.get_cover_letter_by_job(db, req.job_id)
    if existing:
        return {"id": existing.id, "content": existing.content, "cached": True}

    from src.ai_matcher import GeminiMatcher
    from src.models import JobListing

    skills = json.loads(job_row.skills_required) if job_row.skills_required else []
    job = JobListing(
        id=job_row.id, title=job_row.title, company=job_row.company,
        location=job_row.location, description=job_row.description,
        url=job_row.url, platform=job_row.platform,
        skills=skills, job_type=job_row.job_type,
    )

    matcher = GeminiMatcher()
    content = await matcher.generate_cover_letter(job)
    cl = crud.create_cover_letter(db, req.job_id, content)
    return {"id": cl.id, "content": content, "cached": False}


@router.get("")
def list_cover_letters(db: Session = Depends(get_db)):
    cls = crud.get_cover_letters(db)
    result = []
    for c in cls:
        job = crud.get_job(db, c.job_id)
        result.append({
            "id": c.id, "job_id": c.job_id, "content": c.content,
            "created_at": c.created_at, "updated_at": c.updated_at,
            "job_title": job.title if job else "Unknown",
            "job_company": job.company if job else "Unknown",
        })
    return result


@router.get("/{cl_id}")
def get_cover_letter(cl_id: str, db: Session = Depends(get_db)):
    cl = crud.get_cover_letter(db, cl_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return cl


@router.put("/{cl_id}")
def update_cover_letter(cl_id: str, req: schemas.CoverLetterUpdate, db: Session = Depends(get_db)):
    cl = crud.update_cover_letter(db, cl_id, req.content)
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return cl


@router.delete("/{cl_id}")
def delete_cover_letter(cl_id: str, db: Session = Depends(get_db)):
    if not crud.delete_cover_letter(db, cl_id):
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}
