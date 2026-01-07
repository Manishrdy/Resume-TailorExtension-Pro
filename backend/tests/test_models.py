"""
Unit tests for Resume Pydantic models
"""

import pytest
from pydantic import ValidationError

from models.resume import PersonalInfo, Experience, Resume


@pytest.mark.unit
def test_personal_info_validation():
    """Test PersonalInfo validation"""
    info = PersonalInfo(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        location="San Francisco",
    )
    assert info.name == "John Doe"


@pytest.mark.unit
def test_experience_validation():
    """Test Experience model validation"""
    exp = Experience(
        company="Tech Corp",
        position="Software Engineer",
        startDate="2020-01",
        endDate="Present",
        description=["Built scalable systems"],
    )
    assert exp.company == "Tech Corp"


@pytest.mark.unit
def test_resume_requires_skills():
    """Test that resume requires at least one skill"""
    with pytest.raises(ValidationError):
        Resume(
            id="test",
            name="Test",
            personalInfo=PersonalInfo(name="John", email="j@example.com"),
            experience=[
                Experience(
                    company="Test",
                    position="Engineer",
                    startDate="2020",
                    endDate="2021",
                    description=["Did stuff"],
                )
            ],
            skills=[],
        )
