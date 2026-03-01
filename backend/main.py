"""
FastAPI application entry point for Job Tracker Pro.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure root dir is importable (for src/ modules)
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.config import settings
from backend.core.database import init_db, SessionLocal
from backend.core.scheduler import start_scheduler, stop_scheduler
from backend.core.seeder import seed_mock_data

# Routes
from backend.api.routes.jobs import router as jobs_router
from backend.api.routes.applications import router as apps_router
from backend.api.routes.notifications import router as notifs_router, ws_router
from backend.api.routes.companies import router as companies_router
from backend.api.routes.profile import router as profile_router
from backend.api.routes.cover_letters import router as cover_letters_router
from backend.api.routes.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    init_db()
    db = SessionLocal()
    try:
        seed_mock_data(db)
    finally:
        db.close()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Job Tracker Pro API",
    description="AI-powered job tracking and application management",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(jobs_router, prefix=API_PREFIX)
app.include_router(apps_router, prefix=API_PREFIX)
app.include_router(notifs_router, prefix=API_PREFIX)
app.include_router(companies_router, prefix=API_PREFIX)
app.include_router(profile_router, prefix=API_PREFIX)
app.include_router(cover_letters_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)

# WebSocket (no /api prefix)
app.include_router(ws_router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/settings")
def get_settings():
    return {
        "gemini_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here"),
        "daily_scan_time": settings.DAILY_SCAN_TIME,
        "digest_time": settings.DIGEST_TIME,
        "job_roles": settings.JOB_ROLES,
        "job_locations": settings.JOB_LOCATIONS,
        "experience_level": settings.EXPERIENCE_LEVEL,
    }
