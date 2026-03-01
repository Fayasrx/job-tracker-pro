"""
Mock data seeder — populates DB with realistic test jobs on first run,
so the UI is immediately usable without running scrapers.
"""

import json
import uuid
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from backend.db.models import Job


MOCK_JOBS = [
    {"title": "ML Engineer", "company": "Google DeepMind", "location": "Remote", "platform": "linkedin", "match_score": 92.5, "skills": ["Python", "PyTorch", "TensorFlow", "Transformers"]},
    {"title": "AI/ML Engineer", "company": "Microsoft Azure AI", "location": "Hyderabad", "platform": "indeed", "match_score": 88.0, "skills": ["Python", "Azure ML", "Scikit-learn", "REST APIs"]},
    {"title": "Data Scientist", "company": "Amazon", "location": "Bangalore", "platform": "linkedin", "match_score": 82.0, "skills": ["Python", "SQL", "Pandas", "Machine Learning"]},
    {"title": "Python Developer", "company": "Infosys", "location": "Chennai", "platform": "naukri", "match_score": 78.5, "skills": ["Python", "Flask", "REST APIs", "SQL"]},
    {"title": "NLP Engineer", "company": "Zoho", "location": "Chennai", "platform": "naukri", "match_score": 85.0, "skills": ["NLP", "Hugging Face", "BERT", "Python"]},
    {"title": "Generative AI Engineer", "company": "Startup Labs", "location": "Remote", "platform": "internshala", "match_score": 91.0, "skills": ["LangChain", "RAG", "Hugging Face", "Python"]},
    {"title": "Software Engineer - AI", "company": "Wipro", "location": "Bangalore", "platform": "naukri", "match_score": 72.0, "skills": ["Python", "Java", "Machine Learning"]},
    {"title": "Deep Learning Engineer", "company": "NVIDIA", "location": "Hyderabad", "platform": "linkedin", "match_score": 87.5, "skills": ["PyTorch", "CUDA", "CNNs", "Python"]},
    {"title": "Data Engineer", "company": "Flipkart", "location": "Bangalore", "platform": "indeed", "match_score": 68.0, "skills": ["Python", "SQL", "Spark", "Hadoop"]},
    {"title": "AI Research Intern", "company": "IIT-M AI Lab", "location": "Chennai", "platform": "internshala", "match_score": 80.0, "skills": ["Python", "Research", "PyTorch", "NLP"]},
    {"title": "MLOps Engineer", "company": "Swiggy", "location": "Bangalore", "platform": "linkedin", "match_score": 75.0, "skills": ["MLflow", "Docker", "Python", "CI/CD"]},
    {"title": "Computer Vision Engineer", "company": "Ola AI", "location": "Hyderabad", "platform": "naukri", "match_score": 79.0, "skills": ["OpenCV", "PyTorch", "CNNs", "Python"]},
    {"title": "LLM Engineer", "company": "Sarvam AI", "location": "Remote", "platform": "linkedin", "match_score": 93.0, "skills": ["LLMs", "Fine-tuning", "Hugging Face", "Python"]},
    {"title": "AI Product Engineer", "company": "PhonePe", "location": "Bangalore", "platform": "glassdoor", "match_score": 76.0, "skills": ["Python", "ML", "Flask", "SQL"]},
    {"title": "Backend Engineer (Python)", "company": "Razorpay", "location": "Bangalore", "platform": "glassdoor", "match_score": 70.0, "skills": ["Python", "FastAPI", "PostgreSQL", "Redis"]},
    {"title": "Fresher AI Engineer", "company": "TCS", "location": "Chennai", "platform": "naukri", "match_score": 74.0, "skills": ["Python", "Machine Learning", "SQL"]},
    {"title": "ML Platform Engineer", "company": "Myntra", "location": "Bangalore", "platform": "linkedin", "match_score": 81.0, "skills": ["Python", "MLflow", "Kubernetes", "PyTorch"]},
    {"title": "Recommendation Engineer", "company": "Meesho", "location": "Bangalore", "platform": "indeed", "match_score": 77.0, "skills": ["Python", "Collaborative Filtering", "Pandas"]},
    {"title": "AI Automation Engineer", "company": "Accenture", "location": "Hyderabad", "platform": "naukri", "match_score": 69.0, "skills": ["Python", "Playwright", "Automation", "Selenium"]},
    {"title": "Research Engineer - GenAI", "company": "Adobe India", "location": "Remote", "platform": "linkedin", "match_score": 89.0, "skills": ["Generative AI", "Diffusion Models", "Python", "PyTorch"]},
]

JOB_DESCRIPTIONS = {
    "ML Engineer": "We are looking for a talented ML Engineer to join our team. You will design and build machine learning models, work with large datasets, and deploy models to production. Experience with PyTorch or TensorFlow is required.",
    "default": "Join our team and work on cutting-edge AI/ML projects. You will collaborate with senior engineers, build production systems, and have direct impact on our products. We value curiosity, ownership and technical excellence.",
}


def seed_mock_data(db: Session):
    """Seed DB with mock jobs if empty."""
    existing = db.query(Job).count()
    if existing > 0:
        return  # Already seeded

    now = datetime.utcnow()
    for i, mock in enumerate(MOCK_JOBS):
        days_ago = random.randint(0, 7)
        scraped = now - timedelta(days=days_ago)
        desc = JOB_DESCRIPTIONS.get(mock["title"], JOB_DESCRIPTIONS["default"])
        domain = mock["company"].lower().replace(" ", "").replace(",", "")
        # Remove common words
        for w in ["ai", "labs", "india", "azure", "deepmind"]:
            domain = domain.replace(w, "")
        domain = domain.strip() or "company"

        job = Job(
            id=str(uuid.uuid4()),
            title=mock["title"],
            company=mock["company"],
            location=mock["location"],
            description=f"{desc}\n\nRequired Skills: {', '.join(mock['skills'])}",
            url=f"https://{mock['platform']}.com/jobs/{uuid.uuid4().hex[:8]}",
            platform=mock["platform"],
            job_type="Full-time" if i % 5 != 0 else "Internship",
            experience_level="fresher",
            salary_range="3-8 LPA" if "Intern" not in mock["title"] else "Stipend",
            skills_required=json.dumps(mock["skills"]),
            posted_date=scraped.strftime("%Y-%m-%d"),
            scraped_at=scraped,
            match_score=mock["match_score"],
            match_analysis=json.dumps({
                "matching_skills": mock["skills"][:2],
                "missing_skills": ["Kubernetes"] if mock["match_score"] < 85 else [],
                "recommendation": "Good match! Apply soon.",
                "tailored_summary": f"Fresher AI/ML engineer with experience in {', '.join(mock['skills'][:2])} and strong project background.",
            }),
            is_saved=False,
            is_active=True,
            company_logo_url=f"https://logo.clearbit.com/{domain}.com",
        )
        db.add(job)

    db.commit()
