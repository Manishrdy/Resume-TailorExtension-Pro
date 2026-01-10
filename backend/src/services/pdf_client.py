"""
PDF Client Service for Open Resume integration
Handles communication with Open Resume service for PDF generation
"""

import httpx
from typing import Optional, List, Dict, Any
import time
import re

from app.config import settings
from utils.logger import logger, log_error
from models.resume import Resume


class PDFClientService:
    """Service for generating PDFs via Open Resume"""

    def __init__(self):
        """Initialize PDF client"""
        self.base_url = settings.OPEN_RESUME_URL
        self.timeout = settings.OPEN_RESUME_API_TIMEOUT

        logger.info(f"✅ PDF Client initialized (Open Resume: {self.base_url})")

    @staticmethod
    def _format_date_range(start: Optional[str], end: Optional[str]) -> str:
        if start and end:
            return start if start == end else f"{start} - {end}"
        return start or end or ""

    @staticmethod
    def _sanitize_bullet_point(text: str) -> str:
        """Sanitize bullet point text by removing line breaks and extra whitespace."""
        if not text:
            return ""
        # Replace line breaks with spaces
        text = re.sub(r"\r?\n", " ", text)
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        return text.strip()

    @staticmethod
    def _clean_url(url: str) -> str:
        """Remove https://, http://, and www. from URLs for cleaner display."""
        if not url:
            return ""
        # Remove protocol
        cleaned = re.sub(r"^https?://", "", url)
        # Remove www.
        cleaned = re.sub(r"^www\.", "", cleaned)
        # Remove trailing slash
        cleaned = cleaned.rstrip("/")
        return cleaned

    @staticmethod
    def _categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
        """Intelligently categorize skills into groups with strict matching."""
        # Define skill categories - checked in order, first match wins
        categories = {
            "Programming Languages": [
                "python", "javascript", "typescript", "java", "c#", "c++", "go",
                "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "julia", "c", "sql"
            ],
            "Frontend Frameworks": [
                "react.js", "react", "vue.js", "vue", "angular.js", "angular", "svelte",
                "next.js", "nuxt", "gatsby", "redux", "mobx", "jquery"
            ],
            "Backend Frameworks": [
                "spring boot", "spring", "node.js", "express.js", "express", "fastapi",
                "flask", "django", ".net", "asp.net", "laravel", "rails"
            ],
            "Databases & Messaging": [
                "postgresql", "mysql", "mongodb", "redis", "cassandra", "dynamodb",
                "elasticsearch", "apache kafka", "kafka", "rabbitmq", "oracle"
            ],
            "Cloud & DevOps": [
                "aws", "azure", "gcp", "google cloud", "ec2", "s3", "cloudwatch",
                "docker", "kubernetes", "terraform", "jenkins", "github actions",
                "circle ci", "circleci", "travis ci", "ci/cd", "maven", "dynatrace"
            ],
            "AI & Machine Learning": [
                "llms", "llm", "langchain", "openai", "gpt", "gemini",
                "rag pipeline", "rag", "semantic search", "fuzzy search",
                "spacy", "tensorflow", "pytorch"
            ],
            "APIs & Web Services": [
                "rest api", "rest", "soap web services", "soap", "graphql", "grpc",
                "microsoft graph api", "web services"
            ],
            "Security & Auth": [
                "oauth 2.0", "oauth", "sso", "jwt", "pii/phi data encryption",
                "secure data transmission", "data privacy compliance"
            ],
            "Development Tools": [
                "git", "junit", "mockito", "easymock", "test driven development",
                "tdd", "postman", "swagger", "jira"
            ],
            "Data Processing": [
                "apache spark", "spark", "apache flink", "flink", "kinesis",
                "document parsing"
            ],
        }

        categorized = {}
        uncategorized = []

        for skill in skills:
            skill_lower = skill.lower().strip()
            matched = False

            # Check each category in order (first match wins)
            for category, keywords in categories.items():
                # Sort keywords by length (longest first) to match more specific terms first
                sorted_keywords = sorted(keywords, key=len, reverse=True)
                for keyword in sorted_keywords:
                    # Exact match only to avoid false positives
                    if skill_lower == keyword:
                        if category not in categorized:
                            categorized[category] = []
                        categorized[category].append(skill)
                        matched = True
                        break
                if matched:
                    break

            if not matched:
                uncategorized.append(skill)

        # Add uncategorized skills to "Other" category if any
        if uncategorized:
            categorized["Other"] = uncategorized

        return categorized

    @staticmethod
    def _split_description_to_bullets(description: Optional[str]) -> List[str]:
        if not description:
            return []
        primary_parts = [
            part.strip()
            for part in re.split(r"(?:\r?\n|•|\u2022|;)", description)
            if part.strip()
        ]
        if len(primary_parts) > 1:
            return primary_parts

        sentence_parts = [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", description)
            if part.strip()
        ]
        return sentence_parts or primary_parts

    def _to_open_resume_payload(self, resume: Resume) -> Dict[str, Any]:
        """Convert Resume to Open Resume API payload format.

        The Open Resume PDF generator expects the resume in its native structure,
        matching the sample-resume.json format exactly.
        """

        # Transform profile to Open Resume format
        # Open Resume expects: name, email, phone, location, url, portfolio, github, summary
        profile = {
            "name": resume.personalInfo.name,
            "email": resume.personalInfo.email,
        }

        # Add optional fields if present
        if resume.personalInfo.phone:
            profile["phone"] = resume.personalInfo.phone
        if resume.personalInfo.location:
            profile["location"] = resume.personalInfo.location
        if resume.personalInfo.summary:
            profile["summary"] = resume.personalInfo.summary

        # Map our fields to Open Resume's expected fields
        # Open Resume shows: email, phone, location, url, portfolio, github
        # Priority: website -> url, linkedin -> portfolio (if no website), github -> github
        # Clean URLs to remove https://www. for cleaner display
        if resume.personalInfo.website:
            profile["url"] = self._clean_url(resume.personalInfo.website)

        if resume.personalInfo.linkedin:
            # If we have a website, put linkedin in portfolio, otherwise in url
            if resume.personalInfo.website:
                profile["portfolio"] = self._clean_url(resume.personalInfo.linkedin)
            else:
                profile["url"] = self._clean_url(resume.personalInfo.linkedin)

        if resume.personalInfo.github:
            profile["github"] = self._clean_url(resume.personalInfo.github)

        # Transform work experiences to Open Resume format
        work_experiences = []
        for exp in resume.experience:
            # Sanitize each description to remove line breaks
            sanitized_descriptions = [
                self._sanitize_bullet_point(desc) for desc in exp.description
            ]
            work_experiences.append({
                "company": exp.company,
                "jobTitle": exp.position,
                "date": self._format_date_range(exp.startDate, exp.endDate),
                "descriptions": sanitized_descriptions,
            })

        # Transform educations to Open Resume format
        educations = []
        for edu in resume.education:
            education_entry = {
                "school": edu.institution,
                "degree": edu.degree,
                "date": self._format_date_range(edu.startDate, edu.endDate),
            }
            if edu.gpa:
                education_entry["gpa"] = edu.gpa
            if edu.achievements:
                # Sanitize achievements
                education_entry["descriptions"] = [
                    self._sanitize_bullet_point(ach) for ach in edu.achievements
                ]
            educations.append(education_entry)

        # Transform projects to Open Resume format
        projects = []
        for proj in resume.projects:
            # Sanitize project highlights
            sanitized_highlights = [
                self._sanitize_bullet_point(highlight) for highlight in proj.highlights
            ]
            project_entry = {
                "project": proj.name,
                "descriptions": sanitized_highlights,
            }
            if proj.startDate or proj.endDate:
                project_entry["date"] = self._format_date_range(proj.startDate, proj.endDate)
            if proj.link:
                project_entry["url"] = proj.link
            projects.append(project_entry)

        # Transform skills to Open Resume format
        # Open Resume expects: { featuredSkills: [{skill, rating}], descriptions: [] }
        # Strategy: Categorize ALL skills and format as inline text
        # Format: "Category: skill1, skill2, skill3"
        skill_descriptions = []

        # Categorize all skills
        if resume.skills:
            categorized = self._categorize_skills(resume.skills)

            # Format each category as "Category: skill1, skill2, skill3"
            for category, category_skills in categorized.items():
                if category_skills:
                    skills_str = ", ".join(category_skills)
                    skill_descriptions.append(f"{category}: {skills_str}")

        # No featured skills - using categorized inline format only
        skills = {
            "featuredSkills": [],
            "descriptions": skill_descriptions,
        }

        # Add custom section (empty by default)
        custom = {
            "descriptions": []
        }

        return {
            "resume": {
                "profile": profile,
                "workExperiences": work_experiences,
                "educations": educations,
                "skills": skills,
                "projects": projects,
                "custom": custom,
            },
            "settings": {
                "fontFamily": settings.OPEN_RESUME_FONT_FAMILY,
                "fontSize": settings.OPEN_RESUME_FONT_SIZE,
                "themeColor": settings.OPEN_RESUME_THEME_COLOR,
                "documentSize": settings.OPEN_RESUME_DOCUMENT_SIZE,
                "formToHeading": {
                    "workExperiences": "WORK EXPERIENCE",
                    "educations": "EDUCATION",
                    "projects": "PROJECTS",
                    "skills": "SKILLS",
                    "custom": "CUSTOM",
                },
                "formToShow": {
                    "workExperiences": True,
                    "educations": True,
                    "projects": True,
                    "skills": True,
                    "custom": True,
                },
                "formsOrder": ["workExperiences", "educations", "projects", "skills", "custom"],
                "showBulletPoints": {
                    "workExperiences": True,
                    "educations": True,
                    "projects": True,
                    "skills": True,
                    "custom": True,
                },
            },
        }

    async def generate_pdf(self, resume: Resume) -> Optional[bytes]:
        """
        Generate PDF from resume using Open Resume service

        Args:
            resume: Resume object to convert to PDF

        Returns:
            PDF bytes or None if failed
        """
        try:
            start_time = time.time()

            logger.info(f"📄 Generating PDF for: {resume.personalInfo.name}")
            logger.info(f"   Resume ID: {resume.id}")

            # Convert resume to JSON-friendly dict (ensure datetime serialization)
            # Using Pydantic's JSON encoding to handle datetimes and other types
            payload = self._to_open_resume_payload(resume)

            # Call Open Resume API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate-pdf",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                duration_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    pdf_bytes = response.content
                    pdf_size_kb = len(pdf_bytes) / 1024

                    logger.info(
                        f"✅ PDF generated successfully in {duration_ms:.2f}ms"
                    )
                    logger.info(f"   Size: {pdf_size_kb:.2f} KB")

                    return pdf_bytes
                else:
                    logger.error(
                        f"❌ Open Resume returned error: {response.status_code}"
                    )
                    logger.error(f"   Response: {response.text[:200]}")
                    return None

        except httpx.TimeoutException as e:
            logger.error(f"❌ PDF generation timeout after {self.timeout}s")
            log_error(
                e,
                {
                    "resume_id": resume.id,
                    "resume_name": resume.personalInfo.name,
                    "timeout": self.timeout,
                },
            )
            return None

        except httpx.ConnectError as e:
            logger.error(f"❌ Cannot connect to Open Resume service at {self.base_url}")
            logger.error(
                f"   Make sure Open Resume is running on {self.base_url}"
            )
            log_error(e, {"service_url": self.base_url})
            return None

        except Exception as e:
            logger.error(f"❌ Unexpected error during PDF generation: {e}")
            log_error(
                e,
                {
                    "resume_id": resume.id,
                    "resume_name": resume.personalInfo.name,
                },
            )
            return None

    async def check_service_health(self) -> bool:
        """
        Check if Open Resume service is available

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/health")
                return response.status_code == 200
        except Exception:
            return False


# Singleton instance
_pdf_client: Optional[PDFClientService] = None


def get_pdf_client() -> PDFClientService:
    """Get or create PDF client instance"""
    global _pdf_client
    if _pdf_client is None:
        _pdf_client = PDFClientService()
    return _pdf_client
