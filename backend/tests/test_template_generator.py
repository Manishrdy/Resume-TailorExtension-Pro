"""
Unit tests for TemplateDocumentGenerator
"""
import pytest
from models.resume import Resume, PersonalInfo, Experience, Education
from services.template_document_generator import TemplateDocumentGenerator
import os

@pytest.mark.unit
def test_prepare_template_data_maps_bullets():
    """Test that _prepare_template_data correctly maps experience.description to experience.bullets"""
    # Create a minimal resume with experience
    resume = Resume(
        id="test-id",
        name="Test Resume",
        personalInfo=PersonalInfo(
            name="Test User",
            email="test@example.com",
            phone="123-456-7890",
            location="Test City",
            summary="A test summary"
        ),
        experience=[
            Experience(
                company="Test Company",
                position="Test Position",
                startDate="2022-01",
                endDate="Present",
                location="Remote",
                description=[
                    "Bullet point 1",
                    "Bullet point 2"
                ]
            )
        ],
        education=[],
        skills=["Python", "Pytest"],
        projects=[],
        certifications=[]
    )

    # Initialize generator (we don't need real templates for this unit test)
    # We construct it with a dummy path as we only care about _prepare_template_data
    generator = TemplateDocumentGenerator(template_dir=os.path.dirname(__file__))

    # Prepare data
    data = generator._prepare_template_data(resume)

    # Verify mapping
    assert "experience" in data
    assert len(data["experience"]) == 1
    exp_entry = data["experience"][0]
    
    # Check that bullets field exists and matches description
    assert "bullets" in exp_entry
    assert exp_entry["bullets"] == ["Bullet point 1", "Bullet point 2"]
    # Ensure description is still there (optional, but good for completeness)
    assert exp_entry["description"] == ["Bullet point 1", "Bullet point 2"]
