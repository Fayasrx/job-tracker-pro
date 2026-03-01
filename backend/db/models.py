"""
SQLAlchemy ORM models for the Job Tracker Pro database.
"""

from datetime import datetime
from sqlalchemy import (
    Boolean, Column, Float, ForeignKey, Integer, String, Text, DateTime
)
from backend.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, default="")
    description = Column(Text, default="")
    url = Column(String, nullable=False, unique=True)
    platform = Column(String, nullable=False)  # linkedin/indeed/glassdoor/naukri/internshala
    job_type = Column(String, default="")  # full-time/internship/contract
    experience_level = Column(String, default="")
    salary_range = Column(String, default="")
    skills_required = Column(Text, default="[]")  # JSON array string
    posted_date = Column(String, default="")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    match_score = Column(Float, default=0.0)
    match_analysis = Column(Text, default="{}")  # JSON from Gemini
    is_saved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    company_logo_url = Column(String, default="")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    status = Column(String, default="saved")  # saved/applied/in_review/interview/offer/rejected
    applied_date = Column(DateTime, nullable=True)
    cover_letter = Column(Text, default="")
    notes = Column(Text, default="")
    follow_up_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApplicationHistory(Base):
    __tablename__ = "application_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    note = Column(Text, default="")


class TrackedCompany(Base):
    __tablename__ = "tracked_companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    domain = Column(String, default="")
    notify = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)  # new_jobs/high_match/daily_digest/company_update/follow_up/weekly_report
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text, default="{}")  # JSON payload
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String, default="all")
    jobs_found = Column(Integer, default=0)
    new_jobs = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="success")  # success/failed/partial
