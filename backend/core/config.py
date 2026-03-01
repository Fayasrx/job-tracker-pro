"""
Backend configuration â€” extends the existing src/config.py approach.
Loads all settings from the root .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load from root .env
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


class BackendConfig:
    # Paths
    ROOT_DIR: Path = ROOT_DIR
    DATA_DIR: Path = ROOT_DIR / "data"
    PROFILE_PATH: Path = ROOT_DIR / "data" / "profile.json"
    DB_PATH: Path = ROOT_DIR / "data" / "job_tracker.db"

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Database
    @property
    def DATABASE_URL(self) -> str:
        url = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/data/job_tracker.db")
        # On Render: if /data not mounted, fall back to project-relative path
        if url == "sqlite:////data/job_tracker.db":
            url = f"sqlite:///{ROOT_DIR}/data/job_tracker.db"
        return url

    # Server
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Always include localhost; also read from env for production (e.g. Vercel URL)."""
        origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
        defaults = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
        return list(set(origins + defaults))

    # Job search prefs
    JOB_ROLES: list[str] = [r.strip() for r in os.getenv("JOB_ROLES", "AI/ML Engineer,Python Developer").split(",")]
    JOB_LOCATIONS: list[str] = [loc.strip() for loc in os.getenv("JOB_LOCATIONS", "Remote,Bangalore").split(",")]
    EXPERIENCE_LEVEL: str = os.getenv("EXPERIENCE_LEVEL", "fresher")

    # Scheduler times (HH:MM)
    DAILY_SCAN_TIME: str = os.getenv("DAILY_SCAN_TIME", "06:00")
    DIGEST_TIME: str = os.getenv("DIGEST_TIME", "09:00")

    # User info
    USER_NAME: str = os.getenv("USER_NAME", "")
    USER_EMAIL: str = os.getenv("USER_EMAIL", "")


settings = BackendConfig()
