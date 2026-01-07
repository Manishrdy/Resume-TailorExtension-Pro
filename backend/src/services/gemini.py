"""
Gemini AI Service for resume tailoring
Uses the new google-genai package
"""

import json
import time
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from app.config import settings
from utils.logger import logger, log_ai_request, log_ai_error
from prompts.tailoring import (
    SYSTEM_INSTRUCTION,
    get_tailoring_prompt,
    get_keyword_extraction_prompt,
    add_json_enforcement,
)
from models.resume import Resume, TailorResponse


class GeminiService:
    """Service for interacting with Gemini AI"""

    def __init__(self):
        """Initialize Gemini client"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        # Initialize client with API key from environment
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

        logger.info(f"✅ Gemini AI service initialized (model: {self.model})")

    def _make_request(
        self, prompt: str, retry_count: int = 0
    ) -> Optional[str]:
        """
        Make a request to Gemini API with retry logic

        Args:
            prompt: The prompt to send
            retry_count: Current retry attempt

        Returns:
            Response text or None if failed
        """
        try:
            start_time = time.time()

            # Generate content with configuration
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    max_output_tokens=settings.GEMINI_MAX_TOKENS,
                    system_instruction=SYSTEM_INSTRUCTION,
                ),
            )

            duration_ms = (time.time() - start_time) * 1000

            # Extract text from response
            response_text = response.text

            # Log successful request
            log_ai_request(
                model=self.model,
                prompt_length=len(prompt),
                response_length=len(response_text),
                duration_ms=duration_ms,
            )

            logger.debug(f"Gemini response preview: {response_text[:200]}...")

            return response_text

        except Exception as e:
            # Log error with context
            log_ai_error(
                e,
                {
                    "retry_count": retry_count,
                    "prompt_length": len(prompt),
                    "model": self.model,
                },
            )

            # Retry logic
            if retry_count < settings.GEMINI_RETRY_ATTEMPTS:
                delay = settings.GEMINI_RETRY_DELAY * (2**retry_count)  # Exponential backoff
                logger.warning(
                    f"Retrying Gemini request in {delay}s (attempt {retry_count + 1}/{settings.GEMINI_RETRY_ATTEMPTS})"
                )
                time.sleep(delay)
                return self._make_request(prompt, retry_count + 1)

            # All retries failed
            logger.error(f"Gemini request failed after {settings.GEMINI_RETRY_ATTEMPTS} attempts")
            return None

    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON response from Gemini, handling various formats

        Args:
            response_text: Raw response from Gemini

        Returns:
            Parsed JSON dict or None if parsing failed
        """
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # Parse JSON
            parsed = json.loads(cleaned)
            logger.info("✅ Successfully parsed JSON response from Gemini")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            return None

    def extract_keywords(self, job_description: str) -> Optional[Dict[str, Any]]:
        """
        Extract keywords from job description

        Args:
            job_description: The job description text

        Returns:
            Dict with extracted keywords or None if failed
        """
        logger.info("📝 Extracting keywords from job description")

        prompt = add_json_enforcement(get_keyword_extraction_prompt(job_description))
        response_text = self._make_request(prompt)

        if not response_text:
            return None

        return self._parse_json_response(response_text)

    def tailor_resume(
        self, resume: Resume, job_description: str
    ) -> Optional[TailorResponse]:
        """
        Tailor resume to match job description

        Args:
            resume: Original resume
            job_description: Target job description

        Returns:
            TailorResponse with optimized resume or None if failed
        """
        logger.info(f"🎯 Starting resume tailoring for: {resume.personalInfo.name}")

        # Convert resume to JSON
        resume_json = resume.model_dump_json(indent=2)

        # Generate prompt
        prompt = add_json_enforcement(get_tailoring_prompt(resume_json, job_description))

        # Make request
        response_text = self._make_request(prompt)

        if not response_text:
            logger.error("❌ Failed to get response from Gemini")
            return None

        # Parse response
        parsed_response = self._parse_json_response(response_text)

        if not parsed_response:
            logger.error("❌ Failed to parse Gemini response")
            return None

        # Validate and construct TailorResponse
        try:
            # Extract tailored resume
            tailored_resume_data = parsed_response.get("tailoredResume")
            if not tailored_resume_data:
                logger.error("❌ Missing 'tailoredResume' in response")
                return None

            # Parse tailored resume
            tailored_resume = Resume(**tailored_resume_data)

            # Calculate ATS score (hybrid approach)
            ats_score = self._calculate_ats_score(
                tailored_resume,
                job_description,
                parsed_response.get("matchedKeywords", []),
            )

            # Construct response
            tailor_response = TailorResponse(
                tailoredResume=tailored_resume,
                atsScore=ats_score,
                matchedKeywords=parsed_response.get("matchedKeywords", []),
                missingKeywords=parsed_response.get("missingKeywords", []),
                suggestions=parsed_response.get("suggestions", []),
                changes=parsed_response.get("changes", []),
            )

            logger.info(
                f"✅ Resume tailored successfully (ATS Score: {ats_score}/100)"
            )
            logger.info(
                f"   Matched: {len(tailor_response.matchedKeywords)} keywords"
            )
            logger.info(
                f"   Missing: {len(tailor_response.missingKeywords)} keywords"
            )

            return tailor_response

        except Exception as e:
            logger.error(f"❌ Failed to construct TailorResponse: {e}")
            log_ai_error(e, {"parsed_response": parsed_response})
            return None

    def _calculate_ats_score(
        self,
        resume: Resume,
        job_description: str,
        matched_keywords: list,
    ) -> int:
        """
        Calculate ATS score using hybrid approach

        Args:
            resume: Tailored resume
            job_description: Job description
            matched_keywords: Keywords matched by AI

        Returns:
            ATS score (0-100)
        """
        # Extract text from resume for analysis
        resume_text = self._extract_resume_text(resume).lower()
        jd_lower = job_description.lower()

        # Count matched keywords
        keyword_matches = len(matched_keywords)

        # Extract important words from JD (simple approach)
        jd_words = set(
            word.strip(".,!?;:")
            for word in jd_lower.split()
            if len(word) > 4  # Filter out short words
        )

        # Count how many JD words appear in resume
        word_matches = sum(1 for word in jd_words if word in resume_text)
        total_jd_words = len(jd_words)

        # Calculate score components
        keyword_score = min(40, keyword_matches * 3)  # Up to 40 points
        word_match_score = (
            (word_matches / total_jd_words) * 40 if total_jd_words > 0 else 0
        )  # Up to 40 points
        completeness_score = 20  # Base score for having complete sections

        # Total score
        total_score = int(keyword_score + word_match_score + completeness_score)

        # Cap at 100
        return min(100, total_score)

    def _extract_resume_text(self, resume: Resume) -> str:
        """Extract all text from resume for analysis"""
        text_parts = [
            resume.personalInfo.name,
            resume.personalInfo.summary or "",
            " ".join(resume.skills),
        ]

        # Add experience
        for exp in resume.experience:
            text_parts.append(exp.company)
            text_parts.append(exp.position)
            text_parts.extend(exp.description)

        # Add projects
        for proj in resume.projects:
            text_parts.append(proj.name)
            text_parts.append(proj.description)
            text_parts.extend(proj.highlights)
            text_parts.extend(proj.technologies)

        # Add education
        for edu in resume.education:
            text_parts.append(edu.institution)
            text_parts.append(edu.degree)

        return " ".join(text_parts)


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
