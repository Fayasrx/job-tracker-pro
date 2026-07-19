"""Gemini-based resume tailoring service."""

from __future__ import annotations

import json
import os

from google import genai

from backend.services.resume_builder import ResumeData


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    return cleaned


def tailor_resume(resume_data: ResumeData, job_description: str) -> ResumeData:
    """Tailor objective and bullets to job keywords; fallback to original on any error."""
    if not job_description.strip():
        return resume_data

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = (
            "You are an expert resume writer. Given resume JSON and a job description, "
            "rewrite the objective and bullet points in experience/projects to better match "
            "the job-description keywords while keeping all facts accurate. "
            "Return ONLY valid JSON with the exact same schema as input.\n\n"
            f"Resume JSON:\n{resume_data.model_dump_json()}\n\n"
            f"Job Description:\n{job_description}"
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        raw_text = (response.text or "").strip()
        if not raw_text:
            return resume_data

        parsed = json.loads(_strip_code_fences(raw_text))
        return ResumeData.model_validate(parsed)
    except Exception:
        return resume_data
