"""
Comprehensive tests for PDF payload transformations.
Tests all field mappings and data transformations.
"""

import pytest
from services.pdf_client import PDFClientService
from models.resume import PersonalInfo, Experience, Education, Project


class TestProfileTransformation:
    """Test profile field mapping transformations."""

    def test_profile_basic_fields(self, sample_resume):
        """Test basic profile fields are correctly mapped."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        profile = payload["resume"]["profile"]
        assert profile["name"] == sample_resume.personalInfo.name
        assert profile["email"] == sample_resume.personalInfo.email
        assert profile["phone"] == sample_resume.personalInfo.phone
        assert profile["location"] == sample_resume.personalInfo.location

    def test_profile_website_to_url(self, sample_personal_info):
        """Test website field is mapped to url."""
        from models.resume import Resume

        resume = Resume(
            id="test-1",
            name="Test",
            personalInfo=sample_personal_info,
            education=[],
            experience=[
                Experience(
                    company="Test", position="Test", location="Test",
                    startDate="2020", endDate="2021", description=["Test"]
                )
            ],
            skills=["Python"],
            projects=[],
            certifications=[],
        )

        client = PDFClientService()
        payload = client._to_open_resume_payload(resume)

        profile = payload["resume"]["profile"]
        assert "url" in profile
        assert profile["url"] == sample_personal_info.website

    def test_profile_linkedin_to_portfolio(self, sample_personal_info):
        """Test linkedin is mapped to portfolio when website exists."""
        from models.resume import Resume

        resume = Resume(
            id="test-1",
            name="Test",
            personalInfo=sample_personal_info,
            education=[],
            experience=[
                Experience(
                    company="Test", position="Test", location="Test",
                    startDate="2020", endDate="2021", description=["Test"]
                )
            ],
            skills=["Python"],
            projects=[],
            certifications=[],
        )

        client = PDFClientService()
        payload = client._to_open_resume_payload(resume)

        profile = payload["resume"]["profile"]
        # When website exists, linkedin goes to portfolio
        assert "portfolio" in profile
        assert profile["portfolio"] == sample_personal_info.linkedin

    def test_profile_linkedin_to_url_without_website(self):
        """Test linkedin is mapped to url when website is missing."""
        from models.resume import Resume, PersonalInfo, Experience

        personal_info = PersonalInfo(
            name="Test User",
            email="test@example.com",
            phone="+1-555-0000",
            location="Test City",
            linkedin="https://linkedin.com/in/testuser",
            github="https://github.com/testuser",
            website=None,  # No website
        )

        resume = Resume(
            id="test-1",
            name="Test",
            personalInfo=personal_info,
            education=[],
            experience=[
                Experience(
                    company="Test", position="Test", location="Test",
                    startDate="2020", endDate="2021", description=["Test"]
                )
            ],
            skills=["Python"],
            projects=[],
            certifications=[],
        )

        client = PDFClientService()
        payload = client._to_open_resume_payload(resume)

        profile = payload["resume"]["profile"]
        # When no website, linkedin goes to url
        assert "url" in profile
        assert profile["url"] == personal_info.linkedin
        assert "portfolio" not in profile


class TestWorkExperienceTransformation:
    """Test work experience transformations."""

    def test_experience_field_mappings(self, sample_resume):
        """Test experience fields are correctly mapped."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        work_exp = payload["resume"]["workExperiences"][0]
        assert "company" in work_exp
        assert "jobTitle" in work_exp
        assert "date" in work_exp
        assert "descriptions" in work_exp

    def test_experience_position_to_jobtitle(self, sample_resume):
        """Test position field is mapped to jobTitle."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        work_exp = payload["resume"]["workExperiences"][0]
        assert work_exp["jobTitle"] == sample_resume.experience[0].position

    def test_experience_date_range_formatting(self, sample_resume):
        """Test date range is properly formatted."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        work_exp = payload["resume"]["workExperiences"][0]
        exp = sample_resume.experience[0]
        expected_date = f"{exp.startDate} - {exp.endDate}"
        assert work_exp["date"] == expected_date

    def test_experience_descriptions_sanitized(self):
        """Test descriptions are sanitized (line breaks removed)."""
        from models.resume import Resume, PersonalInfo, Experience

        experience_with_linebreaks = Experience(
            company="Test Corp",
            position="Engineer",
            location="Remote",
            startDate="2020-01",
            endDate="2021-12",
            description=[
                "Built microservices\nusing Python",
                "Deployed on AWS\r\nwith Docker",
            ]
        )

        resume = Resume(
            id="test-1",
            name="Test",
            personalInfo=PersonalInfo(
                name="Test", email="test@test.com"
            ),
            education=[],
            experience=[experience_with_linebreaks],
            skills=["Python"],
            projects=[],
            certifications=[],
        )

        client = PDFClientService()
        payload = client._to_open_resume_payload(resume)

        descriptions = payload["resume"]["workExperiences"][0]["descriptions"]
        # Line breaks should be replaced with spaces
        assert "\n" not in descriptions[0]
        assert "\r" not in descriptions[0]
        assert "Built microservices using Python" == descriptions[0]


class TestEducationTransformation:
    """Test education transformations."""

    def test_education_field_mappings(self, sample_resume):
        """Test education fields are correctly mapped."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        education = payload["resume"]["educations"][0]
        assert "school" in education
        assert "degree" in education
        assert "date" in education

    def test_education_institution_to_school(self, sample_resume):
        """Test institution field is mapped to school."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        education = payload["resume"]["educations"][0]
        assert education["school"] == sample_resume.education[0].institution

    def test_education_achievements_to_descriptions(self, sample_resume):
        """Test achievements field is mapped to descriptions."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        education = payload["resume"]["educations"][0]
        assert "descriptions" in education
        assert education["descriptions"] == sample_resume.education[0].achievements


class TestProjectsTransformation:
    """Test projects transformations."""

    def test_projects_field_mappings(self, sample_resume):
        """Test project fields are correctly mapped."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        project = payload["resume"]["projects"][0]
        assert "project" in project
        assert "descriptions" in project

    def test_projects_name_to_project(self, sample_resume):
        """Test name field is mapped to project."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        project = payload["resume"]["projects"][0]
        assert project["project"] == sample_resume.projects[0].name

    def test_projects_link_to_url(self, sample_resume):
        """Test link field is mapped to url."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        project = payload["resume"]["projects"][0]
        assert "url" in project
        assert project["url"] == sample_resume.projects[0].link

    def test_projects_highlights_to_descriptions(self, sample_resume):
        """Test highlights field is mapped to descriptions."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        project = payload["resume"]["projects"][0]
        assert project["descriptions"] == sample_resume.projects[0].highlights


class TestSkillsTransformation:
    """Test skills transformations."""

    def test_skills_structure(self, sample_resume):
        """Test skills have correct structure."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        skills = payload["resume"]["skills"]
        assert "featuredSkills" in skills
        assert "descriptions" in skills
        assert isinstance(skills["featuredSkills"], list)
        assert isinstance(skills["descriptions"], list)

    def test_skills_featured_first_six(self, sample_resume):
        """Test first 6 skills become featured skills."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        featured = payload["resume"]["skills"]["featuredSkills"]
        assert len(featured) == min(6, len(sample_resume.skills))

        # Each featured skill should have skill and rating
        for skill_obj in featured:
            assert "skill" in skill_obj
            assert "rating" in skill_obj
            assert skill_obj["rating"] == 4

    def test_skills_categorization(self):
        """Test skills beyond first 6 are categorized."""
        from models.resume import Resume, PersonalInfo, Experience

        all_skills = [
            "Python", "JavaScript", "TypeScript",  # First 6 featured
            "React", "Node.js", "FastAPI",
            "PostgreSQL", "MongoDB", "Redis",  # These get categorized
            "AWS", "Docker", "Kubernetes",
            "LangChain", "GPT", "RAG"
        ]

        resume = Resume(
            id="test-1",
            name="Test",
            personalInfo=PersonalInfo(name="Test", email="test@test.com"),
            education=[],
            experience=[
                Experience(
                    company="Test", position="Test", location="Test",
                    startDate="2020", endDate="2021", description=["Test"]
                )
            ],
            skills=all_skills,
            projects=[],
            certifications=[],
        )

        client = PDFClientService()
        payload = client._to_open_resume_payload(resume)

        descriptions = payload["resume"]["skills"]["descriptions"]
        # Should have categorized descriptions
        assert len(descriptions) > 0

        # Check that categories are present
        categories_found = []
        for desc in descriptions:
            if ":" in desc:
                category = desc.split(":")[0]
                categories_found.append(category)

        # Should have multiple categories
        assert len(categories_found) > 0


class TestUtilityMethods:
    """Test utility methods."""

    def test_format_date_range(self):
        """Test date range formatting."""
        client = PDFClientService()

        # Different dates
        assert client._format_date_range("2020-01", "2021-12") == "2020-01 - 2021-12"

        # Same dates
        assert client._format_date_range("2020-01", "2020-01") == "2020-01"

        # Only start date
        assert client._format_date_range("2020-01", None) == "2020-01"

        # Only end date
        assert client._format_date_range(None, "2021-12") == "2021-12"

        # Both None
        assert client._format_date_range(None, None) == ""

    def test_sanitize_bullet_point(self):
        """Test bullet point sanitization."""
        client = PDFClientService()

        # Remove line breaks
        text = "Line 1\nLine 2"
        assert "\n" not in client._sanitize_bullet_point(text)

        # Remove carriage returns
        text = "Line 1\r\nLine 2"
        assert "\r" not in client._sanitize_bullet_point(text)
        assert "\n" not in client._sanitize_bullet_point(text)

        # Collapse multiple spaces
        text = "Too    many     spaces"
        result = client._sanitize_bullet_point(text)
        assert "  " not in result

        # Empty string
        assert client._sanitize_bullet_point("") == ""
        assert client._sanitize_bullet_point(None) == ""

    def test_categorize_skills(self):
        """Test skill categorization."""
        client = PDFClientService()

        skills = [
            "Python", "JavaScript", "MySQL",
            "AWS", "Kafka", "LangChain"
        ]

        categorized = client._categorize_skills(skills)

        # Should have multiple categories
        assert len(categorized) >= 2

        # Check that skills are being categorized
        total_categorized = sum(len(skills) for skills in categorized.values())
        assert total_categorized == 6  # All skills should be categorized


class TestCompletePayloadStructure:
    """Test complete payload structure."""

    def test_complete_payload_structure(self, sample_resume):
        """Test complete payload has all required sections."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        # Top level structure
        assert "resume" in payload
        assert "settings" in payload

        # Resume sections
        resume = payload["resume"]
        assert "profile" in resume
        assert "workExperiences" in resume
        assert "educations" in resume
        assert "skills" in resume
        assert "projects" in resume
        assert "custom" in resume

        # Settings sections
        settings = payload["settings"]
        assert "fontFamily" in settings
        assert "fontSize" in settings
        assert "themeColor" in settings
        assert "documentSize" in settings
        assert "formToHeading" in settings
        assert "formToShow" in settings
        assert "formsOrder" in settings
        assert "showBulletPoints" in settings

    def test_custom_section_structure(self, sample_resume):
        """Test custom section has correct structure."""
        client = PDFClientService()
        payload = client._to_open_resume_payload(sample_resume)

        custom = payload["resume"]["custom"]
        assert "descriptions" in custom
        assert isinstance(custom["descriptions"], list)
