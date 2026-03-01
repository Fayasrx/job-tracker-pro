"""
Configuration module for Job Application MCP Server.
Loads settings from .env and provides typed config access.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)


class Config:
    """Central configuration for the MCP server."""

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # User Profile
    USER_NAME: str = os.getenv("USER_NAME", "")
    USER_EMAIL: str = os.getenv("USER_EMAIL", "")
    USER_PHONE: str = os.getenv("USER_PHONE", "")
    USER_LOCATION: str = os.getenv("USER_LOCATION", "India")

    # Job Preferences
    JOB_ROLES: list[str] = [
        r.strip() for r in os.getenv("JOB_ROLES", "Software Engineer").split(",")
    ]
    JOB_LOCATIONS: list[str] = [
        l.strip() for l in os.getenv("JOB_LOCATIONS", "Remote").split(",")
    ]
    EXPERIENCE_LEVEL: str = os.getenv("EXPERIENCE_LEVEL", "fresher")
    EXPECTED_SALARY: str = os.getenv("EXPECTED_SALARY", "")

    # Resume
    RESUME_PATH: str = os.getenv("RESUME_PATH", "")

    # Platform credentials
    LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD", "")
    NAUKRI_EMAIL: str = os.getenv("NAUKRI_EMAIL", "")
    NAUKRI_PASSWORD: str = os.getenv("NAUKRI_PASSWORD", "")
    INTERNSHALA_EMAIL: str = os.getenv("INTERNSHALA_EMAIL", "")
    INTERNSHALA_PASSWORD: str = os.getenv("INTERNSHALA_PASSWORD", "")

    # Server
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8080"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()
