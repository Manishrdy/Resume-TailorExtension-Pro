"""
Pydantic models for Resume data structure
Provides validation and type safety for all resume-related data
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class PersonalInfo(BaseModel):
    """Personal information section"""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=2000)  # Increased for AI-enhanced summaries


class Education(BaseModel):
    """Education entry"""

    institution: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=200)
    field: Optional[str] = Field(None, max_length=200)
    startDate: str  # Format: "YYYY-MM" or "YYYY"
    endDate: str  # Format: "YYYY-MM" or "YYYY" or "Present"
    gpa: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Experience(BaseModel):
    """Work experience entry"""

    company: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    startDate: str  # Format: "YYYY-MM" or "YYYY"
    endDate: str  # Format: "YYYY-MM" or "YYYY" or "Present"
    description: List[str] = Field(..., min_items=1)


class Project(BaseModel):
    """Project entry"""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)  # Increased for AI enhancements
    technologies: List[str] = Field(default_factory=list)
    link: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class Certification(BaseModel):
    """Certification entry"""

    name: str = Field(..., min_length=1, max_length=200)
    issuer: str = Field(..., min_length=1, max_length=200)
    date: str  # Format: "YYYY-MM" or "YYYY"
    credentialId: Optional[str] = None
    url: Optional[str] = None


class Resume(BaseModel):
    """Complete resume structure"""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100, description="Resume version name")
    personalInfo: PersonalInfo
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v):
        """Ensure skills list is not empty"""
        if not v:
            raise ValueError("At least one skill is required")
        return v

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, v):
        """Ensure at least one experience entry"""
        if not v:
            raise ValueError("At least one work experience is required")
        return v


class TailorRequest(BaseModel):
    """Request model for AI tailoring endpoint"""

    resume: Resume
    jobDescription: str = Field(..., min_length=50, max_length=50000)
    preserveStructure: bool = Field(
        default=True, description="Keep original structure vs allow AI to reorganize"
    )
    targetRole: Optional[str] = Field(
        None, max_length=100, description="Target job role for optimization"
    )


class KeywordMatch(BaseModel):
    """Keyword matching information"""

    keyword: str
    found: bool
    context: Optional[str] = None  # Where it was found in resume


class TailorResponse(BaseModel):
    """Response model for AI tailoring endpoint"""

    tailoredResume: Resume
    atsScore: int = Field(..., ge=0, le=100)
    matchedKeywords: List[str]
    missingKeywords: List[str]
    suggestions: List[str]
    changes: List[str] = Field(
        default_factory=list, description="Summary of changes made"
    )


class GeneratePDFRequest(BaseModel):
    """Request model for PDF generation endpoint"""

    resume: Resume
    template: str = Field(default="default", description="PDF template to use")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    timestamp: datetime
    services: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str
    message: str
    details: Optional[dict] = None
