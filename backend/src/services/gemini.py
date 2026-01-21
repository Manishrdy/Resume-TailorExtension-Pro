"""
Gemini AI Service for resume tailoring
Uses the new google-genai package
"""

import json
import time
import re
import threading
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

_TAILOR_RESPONSE_SCHEMA = types.Schema(
    type="OBJECT",
    properties={
        "tailoredResume": types.Schema(type="OBJECT"),
        "matchedKeywords": types.Schema(
            type="ARRAY",
            items=types.Schema(type="STRING"),
        ),
        "missingKeywords": types.Schema(
            type="ARRAY",
            items=types.Schema(type="STRING"),
        ),
        "suggestions": types.Schema(
            type="ARRAY",
            items=types.Schema(type="STRING"),
        ),
        "changes": types.Schema(
            type="ARRAY",
            items=types.Schema(type="STRING"),
        ),
    },
    required=[
        "tailoredResume",
        "matchedKeywords",
        "missingKeywords",
        "suggestions",
        "changes",
    ],
)


class TimeoutError(Exception):
    """Raised when a Gemini API call times out"""
    pass


def _call_with_timeout(func, timeout_seconds, *args, **kwargs):
    """
    Call a function with a timeout using threading
    
    Args:
        func: Function to call
        timeout_seconds: Timeout in seconds
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        Result from func or None if timeout occurred
        
    Raises:
        TimeoutError: If function call exceeds timeout
    """
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target, daemon=False)
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        # Thread is still running - timeout occurred
        logger.error(f"⏱️ Gemini API call timed out after {timeout_seconds} seconds")
        raise TimeoutError(f"Gemini API call timed out after {timeout_seconds} seconds")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]


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
        Make a request to Gemini API with retry logic and timeout

        Args:
            prompt: The prompt to send
            retry_count: Current retry attempt

        Returns:
            Response text or None if failed
        """
        try:
            start_time = time.time()
            logger.info(f"📤 Calling Gemini API (model: {self.model}, attempt: {retry_count + 1}/{settings.GEMINI_RETRY_ATTEMPTS}, timeout: {settings.GEMINI_TIMEOUT}s)")

            # Define the API call function for timeout wrapper
            def api_call():
                return self.client.models.generate_content(
                    model=self.model,
                    contents=types.Content(
                        parts=[types.Part(text=prompt)]
                    ),
                    config=types.GenerateContentConfig(
                        temperature=settings.GEMINI_TEMPERATURE,
                        max_output_tokens=settings.GEMINI_MAX_TOKENS,
                        system_instruction=types.Content(
                            parts=[types.Part(text=SYSTEM_INSTRUCTION)]
                        ),
                        response_mime_type="application/json",
                    ),
                )
            
            # Call with timeout
            response = _call_with_timeout(
                api_call, 
                settings.GEMINI_TIMEOUT
            )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"✅ Gemini API responded in {duration_ms:.0f}ms")

            # Extract text from response
            response_text = response.text

            # Validate response is not empty or truncated
            if not response_text:
                raise ValueError("Empty response from Gemini")
            
            # Check if response seems truncated (doesn't end with } or ])
            if not response_text.rstrip().endswith(('}', ']')):
                logger.warning("⚠️ Response may be truncated, missing closing brace/bracket")
                logger.warning(f"Response ends with: {response_text[-50:]}")

            # Log successful request
            log_ai_request(
                model=self.model,
                prompt_length=len(prompt),
                response_length=len(response_text),
                duration_ms=duration_ms,
            )

            # DEBUG: Log full response
            logger.debug("="*80)
            logger.debug("🔍 GEMINI RAW RESPONSE:")
            logger.debug(f"Response length: {len(response_text)} characters")
            logger.debug(f"Response preview: {response_text[:200]}...")
            logger.debug(f"Response ending: ...{response_text[-200:]}")
            logger.debug("="*80)

            return response_text

        except TimeoutError as e:
            # Don't retry on timeout - log and fail immediately
            logger.error(f"⏱️ Gemini API call timed out after {settings.GEMINI_TIMEOUT} seconds")
            log_ai_error(
                e,
                {
                    "retry_count": retry_count,
                    "prompt_length": len(prompt),
                    "model": self.model,
                    "timeout_seconds": settings.GEMINI_TIMEOUT,
                },
            )
            return None

        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = "429" in error_str or "resource" in error_str or "quota" in error_str

            if is_rate_limit:
                logger.warning(f"⚠️ Gemini Rate Limit hit: {e}")
                # Log full details for debugging
                logger.debug(f"Rate Limit Details: {dir(e)}")
                if hasattr(e, 'response'):
                    logger.debug(f"Response Headers: {e.response.headers if hasattr(e.response, 'headers') else 'N/A'}")
                    logger.debug(f"Response Content: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")

            # Log error with context
            log_ai_error(
                e,
                {
                    "retry_count": retry_count,
                    "prompt_length": len(prompt),
                    "model": self.model,
                    "is_rate_limit": is_rate_limit
                },
            )

            # Retry logic (only for non-timeout errors)
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

    def _build_tailoring_prompt(
        self,
        resume_json: str,
        job_description: str,
        force_changes: bool = False,
    ) -> str:
        """Build tailoring prompt with optional strict change requirements."""
        prompt = get_tailoring_prompt(resume_json, job_description)
        if force_changes:
            prompt += """

STRICT REQUIREMENTS:
- You MUST make visible improvements to the resume text.
- Rewrite the professional summary.
- Update at least 2 bullet points in work experience.
- Reorder skills by relevance to the job description.
- Do NOT return the original resume unchanged.
"""

        return add_json_enforcement(prompt)

    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON response from Gemini, handling various formats

        Args:
            response_text: Raw response from Gemini

        Returns:
            Parsed JSON dict or None if parsing failed
        """
        try:
            # DEBUG: Log raw response before cleaning
            logger.debug("🔍 JSON PARSING - Raw response:")
            logger.debug(f"Raw text (first 500 chars): {response_text[:500]}...")
            
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # DEBUG: Log cleaned response
            logger.debug("🔍 JSON PARSING - After cleaning:")
            logger.debug(f"Cleaned text (first 500 chars): {cleaned[:500]}...")
            logger.debug(f"Cleaned text (last 200 chars): ...{cleaned[-200:]}")

            # Parse JSON
            parsed = json.loads(cleaned)
            logger.info("✅ Successfully parsed JSON response from Gemini")
            
            # DEBUG: Log parsed structure
            logger.debug("🔍 JSON PARSING - Parsed structure:")
            logger.debug(f"Keys in parsed JSON: {list(parsed.keys())}")
            
            return parsed

        except json.JSONDecodeError as e:
            logger.error("="*80)
            logger.error("❌ JSON PARSING ERROR:")
            logger.error(f"Error: {e}")
            logger.error(f"Error position: Line {e.lineno}, Column {e.colno}")
            logger.error(f"Response text (first 500): {response_text[:500]}...")
            logger.error(f"Response text (last 500): ...{response_text[-500:]}")
            
            # Attempt to repair truncated JSON
            logger.warning("🔧 Attempting to repair truncated JSON...")
            try:
                # Start with cleaned text (remove possible markdown fences)
                repaired = response_text.strip()
                if repaired.startswith("```json"):
                    repaired = repaired[7:]
                if repaired.startswith("```"):
                    repaired = repaired[3:]
                if repaired.endswith("```"):
                    repaired = repaired[:-3]
                repaired = repaired.strip()
                
                # If the content appears to end inside a string, close the quote
                # Detect odd number of unescaped quotes as a heuristic
                unescaped_quote_count = len(re.findall(r'(?<!\\)"', repaired))
                if unescaped_quote_count % 2 == 1:
                    repaired += '"'
                    logger.warning("Closed unterminated string by appending ending quote")

                # Count braces
                open_braces = repaired.count('{')
                close_braces = repaired.count('}')
                open_brackets = repaired.count('[')
                close_brackets = repaired.count(']')
                
                # Add missing closing characters
                if open_braces > close_braces:
                    repaired += '}' * (open_braces - close_braces)
                    logger.warning(f"Added {open_braces - close_braces} closing braces")
                
                if open_brackets > close_brackets:
                    repaired += ']' * (open_brackets - close_brackets)
                    logger.warning(f"Added {open_brackets - close_brackets} closing brackets")

                # Remove trailing commas before object/array closers (common truncation issue)
                # Example: {"email": "x",} -> {"email": "x"}
                repaired = re.sub(r",\s*(\}|\])", r"\1", repaired)

                # If the text ends with a dangling comma, drop it
                if repaired.rstrip().endswith(','):
                    repaired = repaired.rstrip()
                    repaired = repaired[:-1]
                    logger.warning("Removed trailing dangling comma at end of JSON")
                
                # Try parsing repaired JSON
                parsed = json.loads(repaired)
                logger.info("✅ Successfully repaired and parsed JSON!")
                return parsed
                
            except Exception as repair_error:
                logger.error(f"❌ JSON repair failed: {repair_error}")
                logger.error(f"Full response text for debugging:\n{response_text}")
                logger.error("="*80)
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
        logger.debug("="*80)
        logger.debug("🔍 KEYWORD EXTRACTION - Input:")
        logger.debug(f"Job description length: {len(job_description)} characters")
        logger.debug(f"Job description preview: {job_description[:300]}...")
        logger.debug("="*80)

        prompt = add_json_enforcement(get_keyword_extraction_prompt(job_description))
        response_text = self._make_request(prompt)

        if not response_text:
            logger.error("❌ KEYWORD EXTRACTION - No response from Gemini")
            return None

        result = self._parse_json_response(response_text)
        
        # DEBUG: Log final result
        if result:
            logger.debug("🔍 KEYWORD EXTRACTION - Final result:")
            logger.debug(f"Result: {json.dumps(result, indent=2)}")
        
        return result

    
    def _extract_minimal_resume(self, resume: Resume) -> dict:
        """
        Extract only the content that needs tailoring to minimize tokens
        
        Args:
            resume: Complete Resume object
            
        Returns:
            Minimal dict with only content to be enhanced
        """
        # Handle skills - convert list to dict if needed
        skills = resume.skills
        if isinstance(skills, list):
            # If skills is a flat list, group them
            skills_dict = {}
            chunk_size = 6
            for i in range(0, len(skills), chunk_size):
                chunk = skills[i:i + chunk_size]
                category = "Primary Skills" if i == 0 else f"Skills Set {i // chunk_size + 1}"
                skills_dict[category] = chunk
            skills = skills_dict
        
        return {
            "summary": resume.personalInfo.summary or "",
            "experiences": [
                {
                    "company": exp.company,
                    "description": exp.description
                }
                for exp in resume.experience
            ],
            "projects": [
                {
                    "name": proj.name,
                    "highlights": proj.highlights if proj.highlights else 
                                ([proj.description] if isinstance(proj.description, str) else [])
                }
                for proj in resume.projects
            ],
            "skills": skills if isinstance(skills, dict) else {}
        }

    def _merge_tailored_content(self, original: Resume, tailored: dict) -> Resume:
        """
        Merge tailored content back into original resume
        
        Args:
            original: Original Resume object
            tailored: Dict with enhanced content from Gemini
            
        Returns:
            Enhanced Resume object with merged content
        """
        # Create a deep copy to avoid mutating original
        enhanced = original.model_copy(deep=True)
        
        # Update summary
        if "summary" in tailored and tailored["summary"]:
            enhanced.personalInfo.summary = tailored["summary"]
        
        # Update experience descriptions (match by company name)
        if "experiences" in tailored:
            tailored_exps = {exp["company"]: exp["description"] for exp in tailored["experiences"]}
            for exp in enhanced.experience:
                if exp.company in tailored_exps:
                    desc = tailored_exps[exp.company]
                    # Ensure description is always a list
                    if isinstance(desc, str):
                        # Split by newlines or keep as single item
                        exp.description = [line.strip() for line in desc.split('\n') if line.strip()]
                    elif isinstance(desc, list):
                        exp.description = desc
        
        # Update project highlights (match by name)
        if "projects" in tailored:
            tailored_projs = {proj["name"]: proj.get("highlights", []) for proj in tailored["projects"]}
            for proj in enhanced.projects:
                if proj.name in tailored_projs and tailored_projs[proj.name]:
                    highlights = tailored_projs[proj.name]
                    # Ensure highlights is always a list
                    if isinstance(highlights, str):
                        proj.highlights = [line.strip() for line in highlights.split('\n') if line.strip()]
                    elif isinstance(highlights, list):
                        proj.highlights = highlights
        
        # Update skills
        if "skills" in tailored and tailored["skills"]:
            enhanced.skills = tailored["skills"]
        
        return enhanced
    
    def tailor_resume(
        self, resume: Resume, job_description: str
    ) -> Optional[TailorResponse]:
        """
        Tailor resume to match job description using minimal token approach
        
        Args:
            resume: Complete Resume object
            job_description: Job description text
            
        Returns:
            TailorResponse with enhanced resume or None if failed
        """
        logger.info(f"🎯 Starting resume tailoring for: {resume.personalInfo.name}")
        
        # STEP 1: Extract minimal resume data (saves 60-70% tokens)
        minimal_resume = self._extract_minimal_resume(resume)
        minimal_json = json.dumps(minimal_resume)
        
        # For comparison, use model_dump_json() which handles datetime serialization
        full_resume_json = resume.model_dump_json()
        
        logger.debug("="*80)
        logger.debug("🔍 MINIMAL RESUME EXTRACTION:")
        logger.debug(f"Original resume size: ~{len(full_resume_json)} chars")
        logger.debug(f"Minimal resume size: ~{len(minimal_json)} chars")
        logger.debug(f"Token savings: ~{100 - (len(minimal_json) / len(full_resume_json) * 100):.1f}%")
        logger.debug("="*80)
        
        # STEP 2: Generate prompt with minimal data
        prompt = add_json_enforcement(
            get_tailoring_prompt(minimal_resume, job_description, resume.personalInfo.name)
        )
        
        logger.debug("🔍 Generated prompt:")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        # STEP 3: Get Gemini response
        response_text = self._make_request(prompt)
        
        if not response_text:
            logger.error("❌ Failed to get response from Gemini")
            return None
        
        # STEP 4: Parse response
        result = self._parse_json_response(response_text)
        
        if not result:
            logger.error("❌ Failed to parse Gemini response")
            return None
        
        # STEP 5: Merge tailored content back into original resume
        try:
            # NEW (CORRECT)
            enhanced_resume = self._merge_tailored_content(resume, result["tailoredResume"])
            
            logger.info("✅ Successfully merged tailored content into resume")
            logger.debug("="*80)
            logger.debug("🔍 MERGE RESULTS:")
            logger.debug(f"Summary updated: {enhanced_resume.personalInfo.summary != resume.personalInfo.summary}")
            logger.debug(f"Experience count: {len(enhanced_resume.experience)}")
            logger.debug(f"Projects count: {len(enhanced_resume.projects)}")
            logger.debug(f"Skills updated: {enhanced_resume.skills != resume.skills}")
            logger.debug("="*80)
            
            # STEP 6: Create response
            return TailorResponse(
                tailoredResume=enhanced_resume,
                atsScore=self._calculate_ats_score(
                    result.get("matchedKeywords", []),
                    result.get("missingKeywords", [])
                ),
                matchedKeywords=result.get("matchedKeywords", []),
                missingKeywords=result.get("missingKeywords", []),
                suggestions=result.get("suggestions", []),
                changes=result.get("changes", [])
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to merge tailored content: {e}")
            logger.exception("Full traceback:")
            return None

    def _calculate_ats_score(self, matched: list, missing: list) -> int:
        """Calculate ATS score based on keyword matching"""
        if not matched and not missing:
            return 75
        
        total = len(matched) + len(missing)
        if total == 0:
            return 75
        
        score = int((len(matched) / total) * 100)
        return max(0, min(100, score))

    def _fallback_match_keywords(self, resume: Resume, job_description: str) -> list:
        """Fallback keyword matching when AI response doesn't provide them.

        Uses a simple intersection between resume skills and job description tokens.
        """
        jd_tokens = set(
            token.lower().strip(".,!?;:/()[]{}")
            for token in job_description.split()
            if len(token) >= 2
        )
        
        # Flatten skills if they are a dict
        if isinstance(resume.skills, dict):
            flat_skills = []
            for category_skills in resume.skills.values():
                flat_skills.extend(category_skills)
            resume_skills = {skill.lower() for skill in flat_skills}
            
            # For ordered return, we need a flat list again
            original_skills_ordered = flat_skills
        else:
            resume_skills = {skill.lower() for skill in resume.skills}
            original_skills_ordered = resume.skills

        matched = sorted(list(resume_skills.intersection(jd_tokens)))
        # Return capitalized form based on original skills order
        ordered = [skill for skill in original_skills_ordered if skill.lower() in matched]
        # De-duplicate while preserving order
        seen = set()
        final_ordered = []
        for s in ordered:
            if s.lower() not in seen:
                final_ordered.append(s)
                seen.add(s.lower())
                
        return final_ordered

    def _is_resume_unchanged(self, original: Resume, tailored: Resume) -> bool:
        """Check if tailored resume is identical to the original."""
        original_data = original.model_dump(mode="json", exclude_none=False)
        tailored_data = tailored.model_dump(mode="json", exclude_none=False)
        return original_data == tailored_data

    def _merge_with_original(self, original: Resume, ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge AI output with original resume to ensure required fields are present.

        - Preserve `personalInfo` fields when AI returns nulls
        - Ensure `experience` and `skills` are non-empty; fallback to originals
        - Preserve `projects` and `education` if AI drops them entirely
        """
        orig = json.loads(original.model_dump_json())

        # Personal info: fill nulls from original
        if "personalInfo" in ai_data and isinstance(ai_data["personalInfo"], dict):
            for key, val in orig.get("personalInfo", {}).items():
                if ai_data["personalInfo"].get(key) is None:
                    ai_data["personalInfo"][key] = val
        else:
            ai_data["personalInfo"] = orig.get("personalInfo", {})

        # Experience: must have at least one item
        if not ai_data.get("experience"):
            ai_data["experience"] = orig.get("experience", [])

        # Skills: must have at least one item
        if not ai_data.get("skills"):
            ai_data["skills"] = orig.get("skills", [])

        # Education / Projects / Certifications: preserve if AI removed
        for section in ("education", "projects", "certifications"):
            if ai_data.get(section) is None:
                ai_data[section] = orig.get(section, [])

        # createdAt / updatedAt: preserve timestamps if AI set null
        for ts in ("createdAt", "updatedAt"):
            if ai_data.get(ts) is None and orig.get(ts) is not None:
                ai_data[ts] = orig.get(ts)

        return ai_data

    def _extract_resume_text(self, resume: Resume) -> str:
        """Extract all text from resume for analysis"""
        # Flatten skills for text extraction
        if isinstance(resume.skills, dict):
            flat_skills = []
            for cats in resume.skills.values():
                flat_skills.extend(cats)
            skills_str = " ".join(flat_skills)
        else:
            skills_str = " ".join(resume.skills)

        text_parts = [
            resume.personalInfo.name,
            resume.personalInfo.summary or "",
            skills_str,
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
