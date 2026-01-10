"""
Tests for Open Resume PDF client settings mapping.
"""

from app.config import settings
from services.pdf_client import PDFClientService


def test_pdf_payload_includes_open_resume_settings(sample_resume):
    settings.OPEN_RESUME_FONT_FAMILY = "Roboto"
    settings.OPEN_RESUME_FONT_SIZE = 10
    settings.OPEN_RESUME_THEME_COLOR = "#112233"
    settings.OPEN_RESUME_DOCUMENT_SIZE = "LEGAL"

    client = PDFClientService()
    payload = client._to_open_resume_payload(sample_resume)

    # Verify settings structure
    assert payload["settings"]["fontFamily"] == "Roboto"
    assert payload["settings"]["fontSize"] == 10
    assert payload["settings"]["themeColor"] == "#112233"
    assert payload["settings"]["documentSize"] == "LEGAL"

    # Verify new settings properties
    assert "formToHeading" in payload["settings"]
    assert "formToShow" in payload["settings"]
    assert "formsOrder" in payload["settings"]
    assert "showBulletPoints" in payload["settings"]

    # Verify resume structure matches Open Resume format
    assert payload["resume"]["profile"]["name"] == sample_resume.personalInfo.name
    assert "workExperiences" in payload["resume"]
    assert "educations" in payload["resume"]
    assert "skills" in payload["resume"]
    assert "projects" in payload["resume"]
    assert "custom" in payload["resume"]

    # Verify skills structure
    assert "featuredSkills" in payload["resume"]["skills"]
    assert "descriptions" in payload["resume"]["skills"]
