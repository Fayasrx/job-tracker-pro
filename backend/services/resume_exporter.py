"""Resume PDF export service using ReportLab."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from backend.services.resume_builder import ResumeData


MARGIN = 0.75 * inch


def _add_section_line(story: list) -> None:
    story.append(Spacer(1, 8))
    story.append(HRFlowable(color=colors.black, thickness=0.6, width="100%"))
    story.append(Spacer(1, 8))


def export_to_pdf(resume_data: ResumeData) -> bytes:
    """Generate ATS-friendly resume PDF and return bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        "NameStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        spaceAfter=4,
        spaceBefore=2,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
    )
    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=body_style,
        leftIndent=12,
    )

    story: list = []

    story.append(Paragraph(resume_data.name, name_style))

    contact_parts = [
        resume_data.email,
        resume_data.phone,
        resume_data.location,
        resume_data.linkedin,
        resume_data.github,
    ]
    contact_line = " | ".join([part for part in contact_parts if part])
    if contact_line:
        story.append(Paragraph(contact_line, body_style))

    _add_section_line(story)

    story.append(Paragraph("Objective", section_title_style))
    if resume_data.objective:
        story.append(Paragraph(resume_data.objective, body_style))

    _add_section_line(story)

    story.append(Paragraph("Education", section_title_style))
    for edu in resume_data.education:
        edu_line = " - ".join([v for v in [edu.degree, edu.institution, edu.year] if v])
        if edu_line:
            story.append(Paragraph(edu_line, body_style))
        if edu.score:
            story.append(Paragraph(f"Score: {edu.score}", body_style))

    _add_section_line(story)

    story.append(Paragraph("Technical Skills", section_title_style))
    for category, values in resume_data.skills.items():
        story.append(Paragraph(f"{category}: {', '.join(values)}", body_style))

    _add_section_line(story)

    story.append(Paragraph("Experience", section_title_style))
    for exp in resume_data.experience:
        heading = " - ".join([v for v in [exp.role, exp.company, exp.duration] if v])
        if heading:
            story.append(Paragraph(heading, body_style))
        for bullet in exp.bullets:
            story.append(Paragraph(f"• {bullet}", bullet_style))

    _add_section_line(story)

    story.append(Paragraph("Projects", section_title_style))
    for project in resume_data.projects:
        techs = ", ".join(project.technologies)
        heading = " - ".join([v for v in [project.title, techs] if v])
        if heading:
            story.append(Paragraph(heading, body_style))
        if project.description:
            story.append(Paragraph(project.description, body_style))
        for bullet in project.bullets:
            story.append(Paragraph(f"• {bullet}", bullet_style))

    _add_section_line(story)

    story.append(Paragraph("Certifications", section_title_style))
    for cert in resume_data.certifications:
        story.append(Paragraph(f"• {cert}", bullet_style))

    doc.build(story)
    return buffer.getvalue()
