"""
Gemini AI-powered resume matcher and cover letter generator.
Uses Google Gemini to analyze job-profile fit and generate tailored content.
"""

import json
from pathlib import Path
from typing import Optional

import google.generativeai as genai

from ..config import Config
from ..models import JobListing, MatchAnalysis
from ..utils.logger import log


class GeminiMatcher:
    """AI-powered job matching and content generation using Google Gemini."""

    def __init__(self):
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_gemini_api_key_here":
            log.warning("Gemini API key not configured. AI features will be limited.")
            self._model = None
            return

        genai.configure(api_key=Config.GEMINI_API_KEY)
        self._model = genai.GenerativeModel("gemini-2.0-flash")
        self._profile = self._load_profile()
        log.info("Gemini AI matcher initialized")

    def _load_profile(self) -> dict:
        """Load user profile from JSON."""
        profile_path = Path(__file__).parent.parent.parent / "data" / "profile.json"
        if profile_path.exists():
            return json.loads(profile_path.read_text(encoding="utf-8"))
        return {}

    async def analyze_match(self, job: JobListing) -> MatchAnalysis:
        """Analyze how well a job matches the user's profile."""
        if not self._model:
            return MatchAnalysis(
                score=0,
                recommendation="Gemini API key not configured. Add your key to .env file."
            )

        prompt = f"""You are an expert career advisor. Analyze the match between this candidate's profile and the job listing.

## CANDIDATE PROFILE:
Name: {self._profile.get('name', 'N/A')}
Education: {self._profile.get('education', {}).get('degree', 'N/A')} from {self._profile.get('education', {}).get('college', 'N/A')}
Skills: {json.dumps(self._profile.get('skills', {}), indent=1)}
Experience: {json.dumps(self._profile.get('experience', []), indent=1)}
Projects: {json.dumps(self._profile.get('projects', []), indent=1)}
Certifications: {json.dumps(self._profile.get('certifications', []))}

## JOB LISTING:
Title: {job.title}
Company: {job.company}
Location: {job.location}
Experience Required: {job.experience}
Description: {job.description[:1500]}
Skills Required: {', '.join(job.skills) if job.skills else 'Not specified'}

## INSTRUCTIONS:
Return a JSON object (and nothing else) with these exact keys:
{{
  "score": <number 0-100 representing match percentage>,
  "matching_skills": [<list of candidate skills that match this job>],
  "missing_skills": [<list of required skills candidate lacks>],
  "recommendation": "<1-2 sentence recommendation: should they apply? why?>",
  "tailored_summary": "<A 2-3 sentence professional summary tailored for THIS specific job>"
}}

Be realistic and honest. A fresher with relevant skills and projects should score 50-80 for entry-level roles.
Return ONLY valid JSON, no markdown formatting."""

        try:
            response = await self._model.generate_content_async(prompt)
            text = response.text.strip()

            # Clean markdown code blocks if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()

            data = json.loads(text)
            return MatchAnalysis(**data)
        except json.JSONDecodeError as e:
            log.error(f"Gemini returned invalid JSON: {e}")
            return MatchAnalysis(score=0, recommendation=f"AI parsing error: {str(e)[:100]}")
        except Exception as e:
            log.error(f"Gemini API error: {e}")
            return MatchAnalysis(score=0, recommendation=f"AI error: {str(e)[:100]}")

    async def generate_cover_letter(self, job: JobListing) -> str:
        """Generate a tailored cover letter for a specific job."""
        if not self._model:
            return "Error: Gemini API key not configured."

        prompt = f"""Write a professional, concise cover letter for this job application.

## CANDIDATE:
Name: {self._profile.get('name', 'N/A')}
Email: {self._profile.get('email', 'N/A')}
Phone: {self._profile.get('phone', 'N/A')}
Education: {self._profile.get('education', {}).get('degree', 'N/A')} from {self._profile.get('education', {}).get('college', 'N/A')} (CGPA: {self._profile.get('education', {}).get('cgpa', 'N/A')})
Key Skills: {', '.join(self._profile.get('skills', {}).get('ml_dl', []) + self._profile.get('skills', {}).get('generative_ai', [])[:5])}
Experience: {json.dumps(self._profile.get('experience', [])[:2], indent=1)}
Notable Projects: {json.dumps(self._profile.get('projects', [])[:3], indent=1)}

## JOB:
Title: {job.title}
Company: {job.company}
Description: {job.description[:1000]}

## GUIDELINES:
- Keep it to 250-300 words max
- Be specific about how the candidate's skills and projects relate to this role
- Sound enthusiastic but professional
- Mention 2-3 specific projects/experiences that directly align
- End with a clear call-to-action
- Do NOT use placeholder text"""

        try:
            response = await self._model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            log.error(f"Cover letter generation error: {e}")
            return f"Error generating cover letter: {e}"

    async def suggest_resume_improvements(self, job: JobListing) -> str:
        """Suggest resume tweaks for a specific job."""
        if not self._model:
            return "Error: Gemini API key not configured."

        prompt = f"""You are a resume optimization expert. Based on this job listing, suggest specific improvements to the candidate's resume.

## CANDIDATE PROFILE:
{json.dumps(self._profile, indent=2)}

## TARGET JOB:
Title: {job.title}
Company: {job.company}
Description: {job.description[:1200]}
Required Skills: {', '.join(job.skills)}

## PROVIDE:
1. **Keywords to Add** — ATS-friendly keywords missing from the resume
2. **Skills to Highlight** — Which existing skills should be more prominent
3. **Projects to Emphasize** — Which projects are most relevant to this role
4. **Summary Rewrite** — Rewrite the professional summary for this specific role
5. **Action Items** — 3-5 specific, actionable changes

Be concise and actionable."""

        try:
            response = await self._model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            log.error(f"Resume improvement error: {e}")
            return f"Error: {e}"
