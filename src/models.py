"""
Job data models using Pydantic.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JobListing(BaseModel):
    """Represents a single job listing scraped from any platform."""
    id: str = Field(description="Unique identifier")
    title: str
    company: str
    location: str = ""
    salary: str = ""
    experience: str = ""
    description: str = ""
    skills: list[str] = Field(default_factory=list)
    url: str = ""
    platform: str = Field(description="Source platform: linkedin, naukri, indeed, etc.")
    posted_date: str = ""
    job_type: str = ""  # Full-time, Part-time, Internship, Contract
    scraped_at: datetime = Field(default_factory=datetime.now)
    match_score: float = 0.0  # AI-computed match score 0-100

    def short_str(self) -> str:
        return f"[{self.platform}] {self.title} @ {self.company} ({self.location})"


class ApplicationRecord(BaseModel):
    """Tracks a job application."""
    job_id: str
    job_title: str
    company: str
    platform: str
    url: str
    status: str = "pending"  # pending, applied, rejected, interview, offer
    applied_at: Optional[datetime] = None
    notes: str = ""
    cover_letter: str = ""
    match_score: float = 0.0


class SearchQuery(BaseModel):
    """Parameters for a job search."""
    roles: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    experience: str = "fresher"
    job_type: str = "full-time"
    posted_within: str = "7d"  # 24h, 3d, 7d, 14d, 30d
    platforms: list[str] = Field(
        default_factory=lambda: ["linkedin", "indeed", "naukri", "glassdoor", "internshala"]
    )
    max_results_per_platform: int = 20


class MatchAnalysis(BaseModel):
    """AI-generated match analysis between profile and job."""
    score: float = Field(ge=0, le=100, description="Match percentage 0-100")
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendation: str = ""
    tailored_summary: str = ""
    cover_letter: str = ""
