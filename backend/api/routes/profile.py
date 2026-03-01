"""
Profile API routes — read/write data/profile.json and AI resume tips.
"""

import json
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROFILE_PATH = ROOT / "data" / "profile.json"

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileUpdateRequest(BaseModel):
    data: dict


@router.get("")
def get_profile():
    if not PROFILE_PATH.exists():
        raise HTTPException(status_code=404, detail="Profile not found")
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


@router.put("")
def update_profile(req: ProfileUpdateRequest):
    PROFILE_PATH.write_text(json.dumps(req.data, indent=2), encoding="utf-8")
    return {"message": "Profile updated"}


@router.post("/resume-tips")
async def resume_tips(job_id: str):
    """Get AI-powered resume tips for a specific job."""
    from backend.core.database import SessionLocal
    from backend.db import crud as db_crud
    from src.ai_matcher import GeminiMatcher
    from src.models import JobListing

    db = SessionLocal()
    try:
        job_row = db_crud.get_job(db, job_id)
        if not job_row:
            raise HTTPException(status_code=404, detail="Job not found")
        # Build a JobListing from the DB row
        skills = json.loads(job_row.skills_required) if job_row.skills_required else []
        job = JobListing(
            id=job_row.id, title=job_row.title, company=job_row.company,
            location=job_row.location, description=job_row.description,
            url=job_row.url, platform=job_row.platform,
            skills=skills, job_type=job_row.job_type,
        )
        matcher = GeminiMatcher()
        tips = await matcher.suggest_resume_improvements(job)
        return {"tips": tips}
    finally:
        db.close()
