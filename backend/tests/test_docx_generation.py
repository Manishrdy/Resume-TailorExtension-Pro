
import pytest
import io
from models.resume import Resume, PersonalInfo, Experience, Education
from services.template_document_generator import TemplateDocumentGenerator
import os

@pytest.mark.unit
def test_generate_docx_native_structure():
    """Test that generate_docx runs and creates a valid docx file using the new native generator"""
    
    # Create a full resume
    resume = Resume(
        id="test-id",
        name="Test Resume",
        personalInfo=PersonalInfo(
            name="Test User",
            email="test@example.com",
            phone="123-456-7890",
            location="Test City",
            summary="A test summary",
            linkedin="linkedin.com/in/test",
            website="test.com"
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
        education=[
            Education(
                institution="Test University",
                degree="BS",
                field="Computer Science",
                startDate="2018",
                endDate="2022",
                achievements=["CS101", "Algorithms"]
            )
        ],
        skills=["Python", "Pytest", "HTML", "CSS"],
        projects=[],
        certifications=[]
    )
    
    # Init generator
    generator = TemplateDocumentGenerator(template_dir=os.path.dirname(__file__))
    
    # Generate DOCX
    docx_bytes = generator.generate_docx(resume)
    
    # Basic verification
    assert docx_bytes is not None
    assert len(docx_bytes) > 0
    assert docx_bytes.startswith(b'PK') # ZIP magic header for .docx
