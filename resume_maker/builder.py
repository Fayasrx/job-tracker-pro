"""Resume data models and builder helpers."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""
    score: str = ""


class ProjectEntry(BaseModel):
    title: str = ""
    description: str = ""
    technologies: str = ""
    bullets: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    role: str = ""
    company: str = ""
    duration: str = ""
    bullets: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""
    objective: str = ""

    education: list[EducationEntry] = Field(default_factory=list)
    skills: dict[str, Any] = Field(default_factory=dict)
    projects: list[ProjectEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ResumeData":
        """Build ResumeData from a plain dictionary."""
        return cls.model_validate(data or {})

    def to_dict(self) -> dict:
        """Serialize ResumeData to a plain dictionary."""
        return self.model_dump()
