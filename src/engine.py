"""
Job search engine that orchestrates all platform scrapers.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import JobListing, SearchQuery, ApplicationRecord
from .scrapers.linkedin import LinkedInScraper
from .scrapers.indeed import IndeedScraper
from .scrapers.glassdoor import GlassdoorScraper
from .scrapers.naukri import NaukriScraper
from .scrapers.internshala import InternshalaScraper
from .ai_matcher import GeminiMatcher
from .utils.logger import log


SCRAPER_MAP = {
    "linkedin": LinkedInScraper,
    "indeed": IndeedScraper,
    "glassdoor": GlassdoorScraper,
    "naukri": NaukriScraper,
    "internshala": InternshalaScraper,
}

DATA_DIR = Path(__file__).parent.parent / "data"


class JobEngine:
    """Central engine for searching, matching, and tracking jobs."""

    def __init__(self):
        self.matcher = GeminiMatcher()
        self._scrapers = {}
        self._jobs_cache: dict[str, JobListing] = {}
        self._applications: list[ApplicationRecord] = []
        self._load_applications()

    def _get_scraper(self, platform: str):
        if platform not in self._scrapers:
            cls = SCRAPER_MAP.get(platform)
            if cls:
                self._scrapers[platform] = cls()
        return self._scrapers.get(platform)

    async def search_jobs(
        self,
        roles: list[str] = None,
        locations: list[str] = None,
        platforms: list[str] = None,
        experience: str = "fresher",
        posted_within: str = "7d",
        max_per_platform: int = 15,
    ) -> list[JobListing]:
        """Search for jobs across multiple platforms concurrently."""

        query = SearchQuery(
            roles=roles or ["AI ML Engineer", "Python Developer"],
            locations=locations or ["Remote", "Bangalore"],
            experience=experience,
            posted_within=posted_within,
            platforms=platforms or list(SCRAPER_MAP.keys()),
            max_results_per_platform=max_per_platform,
        )

        log.info(f"Searching {len(query.platforms)} platforms for {query.roles} in {query.locations}")

        tasks = []
        for platform in query.platforms:
            scraper = self._get_scraper(platform)
            if scraper:
                tasks.append(self._safe_search(scraper, query))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_jobs = []
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                log.error(f"Search error: {result}")

        # Deduplicate by title+company
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job.title.lower().strip()}_{job.company.lower().strip()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        # Cache results
        for job in unique_jobs:
            self._jobs_cache[job.id] = job

        # Save to file
        self._save_jobs(unique_jobs)

        log.info(f"Found {len(unique_jobs)} unique jobs across all platforms")
        return unique_jobs

    async def _safe_search(self, scraper, query: SearchQuery) -> list[JobListing]:
        """Run scraper search with error handling."""
        try:
            return await scraper.search(query)
        except Exception as e:
            log.error(f"[{scraper.PLATFORM}] Search failed: {e}")
            return []

    async def analyze_job(self, job_id: str) -> dict:
        """Analyze a specific job's match with the user's profile."""
        job = self._jobs_cache.get(job_id)
        if not job:
            return {"error": f"Job {job_id} not found in cache. Search first."}

        analysis = await self.matcher.analyze_match(job)
        job.match_score = analysis.score

        return {
            "job": job.short_str(),
            "url": job.url,
            "match_score": analysis.score,
            "matching_skills": analysis.matching_skills,
            "missing_skills": analysis.missing_skills,
            "recommendation": analysis.recommendation,
            "tailored_summary": analysis.tailored_summary,
        }

    async def analyze_all_jobs(self, min_score: float = 0) -> list[dict]:
        """Analyze all cached jobs and rank by match score."""
        if not self._jobs_cache:
            return [{"error": "No jobs in cache. Run search_jobs first."}]

        results = []
        for job_id, job in self._jobs_cache.items():
            analysis = await self.matcher.analyze_match(job)
            job.match_score = analysis.score
            if analysis.score >= min_score:
                results.append({
                    "job_id": job_id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "platform": job.platform,
                    "url": job.url,
                    "match_score": analysis.score,
                    "recommendation": analysis.recommendation,
                })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

    async def get_cover_letter(self, job_id: str) -> str:
        """Generate a cover letter for a specific job."""
        job = self._jobs_cache.get(job_id)
        if not job:
            return f"Job {job_id} not found. Search first."
        return await self.matcher.generate_cover_letter(job)

    async def get_resume_tips(self, job_id: str) -> str:
        """Get resume improvement suggestions for a specific job."""
        job = self._jobs_cache.get(job_id)
        if not job:
            return f"Job {job_id} not found. Search first."
        return await self.matcher.suggest_resume_improvements(job)

    def track_application(self, job_id: str, status: str = "applied", notes: str = "") -> dict:
        """Record a job application."""
        job = self._jobs_cache.get(job_id)
        if not job:
            return {"error": f"Job {job_id} not found."}

        record = ApplicationRecord(
            job_id=job_id,
            job_title=job.title,
            company=job.company,
            platform=job.platform,
            url=job.url,
            status=status,
            applied_at=datetime.now(),
            notes=notes,
            match_score=job.match_score,
        )
        self._applications.append(record)
        self._save_applications()

        return {
            "message": f"Tracked: {job.title} @ {job.company} [{status}]",
            "total_applications": len(self._applications),
        }

    def get_application_stats(self) -> dict:
        """Get application tracking statistics."""
        if not self._applications:
            return {"total": 0, "message": "No applications tracked yet."}

        stats = {
            "total": len(self._applications),
            "by_status": {},
            "by_platform": {},
            "recent": [],
        }

        for app in self._applications:
            stats["by_status"][app.status] = stats["by_status"].get(app.status, 0) + 1
            stats["by_platform"][app.platform] = stats["by_platform"].get(app.platform, 0) + 1

        for app in sorted(self._applications, key=lambda a: a.applied_at or datetime.min, reverse=True)[:10]:
            stats["recent"].append({
                "title": app.job_title,
                "company": app.company,
                "status": app.status,
                "platform": app.platform,
                "date": str(app.applied_at)[:10] if app.applied_at else "N/A",
            })

        return stats

    def list_cached_jobs(self, platform: str = None) -> list[dict]:
        """List all cached jobs, optionally filtered by platform."""
        jobs = list(self._jobs_cache.values())
        if platform:
            jobs = [j for j in jobs if j.platform == platform]

        return [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "platform": j.platform,
                "url": j.url,
                "match_score": j.match_score,
            }
            for j in jobs
        ]

    def _save_jobs(self, jobs: list[JobListing]):
        """Save job listings to JSON file."""
        path = DATA_DIR / "jobs_cache.json"
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = [j.model_dump(mode="json") for j in jobs]
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def _save_applications(self):
        """Save application records to JSON."""
        path = DATA_DIR / "applications.json"
        data = [a.model_dump(mode="json") for a in self._applications]
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def _load_applications(self):
        """Load saved application records."""
        path = DATA_DIR / "applications.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self._applications = [ApplicationRecord(**d) for d in data]
                log.info(f"Loaded {len(self._applications)} saved applications")
            except Exception as e:
                log.warning(f"Could not load applications: {e}")

    async def close(self):
        """Close all scraper connections."""
        for scraper in self._scrapers.values():
            await scraper.close()
