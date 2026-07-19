"""Resume maker API routes."""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Response

from backend.services.resume_builder import ResumeData
from backend.services.resume_exporter import export_to_pdf
from backend.services.resume_tailor import tailor_resume


router = APIRouter(prefix="/resume", tags=["resume"])


class TailorRequest(BaseModel):
    resume: ResumeData
    job_description: str


@router.post("/build")
def build_resume(resume: ResumeData):
    return {"status": "ok", "resume": resume.model_dump()}


@router.post("/export/pdf")
def export_resume_pdf(resume: ResumeData):
    pdf_bytes = export_to_pdf(resume)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"},
    )


@router.post("/tailor")
def tailor_resume_route(payload: TailorRequest):
    tailored = tailor_resume(payload.resume, payload.job_description)
    return {"status": "ok", "resume": tailored.model_dump()}
