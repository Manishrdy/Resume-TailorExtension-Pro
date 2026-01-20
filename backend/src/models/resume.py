"""
Pydantic models for Resume data structure
Provides validation and type safety for all resume-related data
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, Field, field_validator


class PersonalInfo(BaseModel):
    """Personal information section"""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    linkedin: Optional[str] = None
    github: Optional[str] = None

    # Accept legacy "portfolio" key from older popup.js exports.
    website: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("website", "portfolio"),
    )

    summary: Optional[str] = Field(None, max_length=2000)  # Increased for AI-enhanced summaries


class Education(BaseModel):
    """Education entry"""

    institution: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=200)
    field: Optional[str] = Field(None, max_length=200)
    startDate: str  # Format: "YYYY-MM" or "YYYY"
    endDate: str  # Format: "YYYY-MM" or "YYYY" or "Present"
    gpa: Optional[str] = None

    # Accept legacy "coursework" from older exports.
    achievements: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("achievements", "coursework"),
    )


class Experience(BaseModel):
    """Work experience entry"""

    # Accept legacy keys from older exports.
    company: str = Field(
        ...,
        min_length=1,
        max_length=200,
        validation_alias=AliasChoices("company", "employer"),
    )
    position: str = Field(
        ...,
        min_length=1,
        max_length=200,
        validation_alias=AliasChoices("position", "role"),
    )

    location: Optional[str] = Field(None, max_length=100)
    startDate: str  # Format: "YYYY-MM" or "YYYY"
    endDate: str  # Format: "YYYY-MM" or "YYYY" or "Present"
    description: List[str] = Field(..., min_items=1)


class Project(BaseModel):
    """Project entry"""

    name: str = Field(..., min_length=1, max_length=200)

    # Older exports sometimes sent a list of strings; coerce to a single string.
    description: str = Field(..., min_length=1, max_length=1000)  # Increased for AI enhancements

    technologies: List[str] = Field(default_factory=list)

    # Accept legacy "github" key from older exports.
    link: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("link", "github"),
    )

    highlights: List[str] = Field(default_factory=list)
    startDate: Optional[str] = None
    endDate: Optional[str] = None

    @field_validator("description", mode="before")
    @classmethod
    def coerce_project_description(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            # Join list items into a compact paragraph
            parts = [str(x).strip() for x in v if str(x).strip()]
            return " ".join(parts)
        return v


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

    # Some legacy exports sent skills as an object or category list; coerce to List[str].
    skills: List[str] = Field(default_factory=list)

    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    # Customization options
    accentColor: Optional[str] = Field(
        default=None,
        description="Hex color code for resume accent color (e.g., #1e3a5f). Falls back to .env default if not provided.",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )

    @field_validator("skills", mode="before")
    @classmethod
    def coerce_skills(cls, v):
        if v is None:
            return []
        # legacy: dict (category -> list/str)
        if isinstance(v, dict):
            out: List[str] = []
            for val in v.values():
                if isinstance(val, list):
                    out.extend(val)
                else:
                    out.extend(re.split(r"[,;\n]", str(val)))
            return [s.strip() for s in out if str(s).strip()]

        # legacy: list of objects [{category, skills:"a,b"}]
        if isinstance(v, list):
            if all(isinstance(x, dict) for x in v):
                out: List[str] = []
                for item in v:
                    raw = item.get("skills") or item.get("items") or ""
                    out.extend(re.split(r"[,;\n]", str(raw)))
                return [s.strip() for s in out if str(s).strip()]
            return [str(s).strip() for s in v if str(s).strip()]

        if isinstance(v, str):
            return [s.strip() for s in re.split(r"[,;\n]", v) if s.strip()]

        return v

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
    changes: List[str] = Field(default_factory=list, description="Summary of changes made")


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
