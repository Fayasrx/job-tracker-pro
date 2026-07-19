"""AI-powered resume tailoring helpers."""

from __future__ import annotations

import json
from anthropic import Anthropic

from resume_maker.builder import ResumeData


SYSTEM_PROMPT = (
    "You are an expert resume writer and ATS optimization specialist. "
    "Given a candidate's resume data as JSON and a job description, "
    "return ONLY a valid JSON object with the same schema as the input resume, "
    "but with the objective and project/experience bullet points rewritten to "
    "better match the job description keywords and requirements. "
    "Do not add false information. Keep all facts accurate."
)


def tailor_resume(resume_data: ResumeData, job_description: str, api_key: str) -> ResumeData:
    """Tailor resume to a job description using Claude; fallback to original on error."""
    if not job_description or not api_key:
        return resume_data

    try:
        client = Anthropic(api_key=api_key)
        payload = {
            "resume": resume_data.to_dict(),
            "job_description": job_description,
        }

        response = client.messages.create(
            model="claude-sonnet-4-6",
            system=SYSTEM_PROMPT,
            max_tokens=4096,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                }
            ],
        )

        text_chunks: list[str] = []
        for block in response.content:
            block_text = getattr(block, "text", None)
            if block_text:
                text_chunks.append(block_text)

        if not text_chunks:
            return resume_data

        merged_text = "\n".join(text_chunks).strip()

        if merged_text.startswith("```"):
            merged_text = merged_text.strip("`")
            if merged_text.lower().startswith("json"):
                merged_text = merged_text[4:].strip()

        tailored_dict = json.loads(merged_text)
        return ResumeData.from_dict(tailored_dict)
    except Exception:
        return resume_data
