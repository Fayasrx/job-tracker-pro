"""Resume data models for resume builder workflows."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Education(BaseModel):
    degree: str
    institution: str
    year: str
    score: str | None = None


class Experience(BaseModel):
    role: str
    company: str
    duration: str
    bullets: list[str] = Field(default_factory=list)


class Project(BaseModel):
    title: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    name: str
    email: str
    phone: str
    linkedin: str
    github: str
    location: str
    objective: str
    education: list[Education] = Field(default_factory=list)
    skills: dict[str, list[str]] = Field(default_factory=dict)
    projects: list[Project] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
