"""
Job service — wraps the existing src/engine.py to search, score, and persist jobs.
"""

import json
import uuid
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db import crud
from backend.services import notification_service

# Ensure root src/ is importable
ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def run_job_scan(
    db: Session,
    roles: list[str] = None,
    locations: list[str] = None,
    platforms: list[str] = None,
    max_per_platform: int = 10,
) -> dict:
    """Run a full job scan using the existing JobEngine and persist results."""
    from src.engine import JobEngine

    scan_start = datetime.utcnow()
    log = crud.create_scan_log(
        db,
        platform="all",
        jobs_found=0,
        new_jobs=0,
        started_at=scan_start,
        status="running",
    )

    try:
        engine = JobEngine()
        jobs = await engine.search_jobs(
            roles=roles or settings.JOB_ROLES,
            locations=locations or settings.JOB_LOCATIONS,
            platforms=platforms,
            max_per_platform=max_per_platform,
        )

        new_count = 0
        high_matches = []

        for job in jobs:
            # Score with Gemini
            try:
                analysis = await engine.matcher.analyze_match(job)
                match_score = analysis.score
                match_analysis = json.dumps({
                    "matching_skills": analysis.matching_skills,
                    "missing_skills": analysis.missing_skills,
                    "recommendation": analysis.recommendation,
                    "tailored_summary": analysis.tailored_summary,
                })
            except Exception:
                match_score = 0.0
                match_analysis = "{}"

            # Build company logo URL
            domain = _guess_domain(job.company)
            logo_url = f"https://logo.clearbit.com/{domain}" if domain else ""

            job_data = {
                "id": job.id if hasattr(job, "id") else str(uuid.uuid4()),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "url": job.url,
                "platform": job.platform,
                "job_type": job.job_type,
                "experience_level": getattr(job, "experience", ""),
                "salary_range": getattr(job, "salary", ""),
                "skills_required": json.dumps(job.skills if job.skills else []),
                "posted_date": job.posted_date,
                "scraped_at": datetime.utcnow(),
                "match_score": match_score,
                "match_analysis": match_analysis,
                "company_logo_url": logo_url,
            }

            existing = crud.get_job(db, job_data["id"])
            if not existing:
                new_count += 1
            crud.upsert_job(db, job_data)

            if match_score >= 85:
                high_matches.append({"title": job.title, "company": job.company, "score": match_score})

        # Update scan log
        log.jobs_found = len(jobs)
        log.new_jobs = new_count
        log.completed_at = datetime.utcnow()
        log.status = "success"
        db.commit()

        # Create notification
        if new_count > 0:
            msg = f"{new_count} new jobs found across all platforms."
            await notification_service.notify(
                db, "new_jobs", f"🆕 {new_count} New Jobs Found", msg,
                {"new_count": new_count, "high_matches": high_matches}
            )
        if high_matches:
            top = high_matches[0]
            await notification_service.notify(
                db, "high_match",
                f"🎯 High Match! {top['score']:.0f}% — {top['title']}",
                f"{top['title']} at {top['company']}",
                top,
            )

        await engine.close()
        return {"status": "success", "jobs_found": len(jobs), "new_jobs": new_count}

    except Exception as e:
        log.status = "failed"
        log.completed_at = datetime.utcnow()
        db.commit()
        return {"status": "failed", "error": str(e)}


def _guess_domain(company: str) -> str:
    """Guess the company domain for logo lookup."""
    clean = company.lower().strip()
    # Remove common suffixes
    for suffix in [" inc", " ltd", " llc", " pvt", " technologies", " solutions", " services", " systems"]:
        clean = clean.replace(suffix, "")
    clean = clean.strip().replace(" ", "").replace(",", "")
    if clean:
        return f"{clean}.com"
    return ""
