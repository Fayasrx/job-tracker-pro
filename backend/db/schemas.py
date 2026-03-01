"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


# ─── Job Schemas ──────────────────────────────────────────────────────────────

class JobBase(BaseModel):
    title: str
    company: str
    location: str = ""
    description: str = ""
    url: str
    platform: str
    job_type: str = ""
    experience_level: str = ""
    salary_range: str = ""
    skills_required: str = "[]"
    posted_date: str = ""
    match_score: float = 0.0
    match_analysis: str = "{}"
    is_saved: bool = False
    company_logo_url: str = ""


class JobCreate(JobBase):
    id: str


class JobOut(JobBase):
    id: str
    scraped_at: Optional[datetime] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class JobListOut(BaseModel):
    jobs: list[JobOut]
    total: int
    page: int
    per_page: int


# ─── Application Schemas ──────────────────────────────────────────────────────

class ApplicationCreate(BaseModel):
    job_id: str
    status: str = "saved"
    notes: str = ""
    follow_up_date: Optional[datetime] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    cover_letter: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class ApplicationOut(BaseModel):
    id: str
    job_id: str
    status: str
    applied_date: Optional[datetime] = None
    cover_letter: str = ""
    notes: str = ""
    follow_up_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Joined job info
    job_title: Optional[str] = None
    job_company: Optional[str] = None
    job_url: Optional[str] = None
    job_platform: Optional[str] = None
    job_location: Optional[str] = None
    job_match_score: Optional[float] = None
    job_logo: Optional[str] = None

    model_config = {"from_attributes": True}


class ApplicationHistoryOut(BaseModel):
    id: int
    application_id: str
    old_status: Optional[str] = None
    new_status: str
    changed_at: Optional[datetime] = None
    note: str = ""

    model_config = {"from_attributes": True}


# ─── Notification Schemas ─────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    data: str = "{}"
    is_read: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NotificationListOut(BaseModel):
    notifications: list[NotificationOut]
    unread_count: int
    total: int


# ─── Company Schemas ──────────────────────────────────────────────────────────

class CompanyTrackRequest(BaseModel):
    name: str
    domain: str = ""
    notify: bool = True


class CompanyUpdate(BaseModel):
    notify: Optional[bool] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    domain: str = ""
    notify: bool = True
    last_checked: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Cover Letter Schemas ─────────────────────────────────────────────────────

class CoverLetterOut(BaseModel):
    id: str
    job_id: str
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CoverLetterUpdate(BaseModel):
    content: str


# ─── Analytics Schemas ────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_jobs_today: int
    total_jobs: int
    avg_match_score: float
    applications_this_week: int
    pending_responses: int
    interviews_scheduled: int
    top_matches: list[dict]
    funnel: dict
    recent_activity: list[dict]


# ─── Profile Schemas ──────────────────────────────────────────────────────────

class ProfileOut(BaseModel):
    data: dict


# ─── Search Schemas ───────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    roles: Optional[list[str]] = None
    locations: Optional[list[str]] = None
    platforms: Optional[list[str]] = None
    experience: str = "fresher"
    max_per_platform: int = 10
