"""
AI Tailoring API endpoint - FULLY IMPLEMENTED
Optimizes resumes for specific job descriptions using Gemini AI
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from models.resume import TailorRequest, TailorResponse, ErrorResponse
from services.gemini import get_gemini_service
from utils.logger import logger, log_error
from utils import artifacts

router = APIRouter()


@router.post(
    "/tailor",
    response_model=TailorResponse,
    status_code=status.HTTP_200_OK,
    summary="Tailor Resume",
    description="Optimize resume for a specific job description using AI",
    responses={
        200: {"model": TailorResponse, "description": "Successfully tailored resume"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "AI service error"},
        503: {"model": ErrorResponse, "description": "Service temporarily unavailable"},
    },
)
async def tailor_resume(request: TailorRequest):
    """
    Tailor resume to match job description using Gemini AI
    
    This endpoint:
    1. Validates the resume and job description
    2. Extracts keywords from the job description
    3. Uses AI to optimize resume content
    4. Calculates ATS compatibility score
    5. Returns enhanced resume with suggestions
    
    **Important Notes:**
    - All factual information (companies, dates, titles) remains unchanged
    - Only phrasing and keyword integration is enhanced
    - Processing time: 10-25 seconds
    - Requires valid GEMINI_API_KEY in environment
    
    **Request Body:**
    - resume: Complete resume object (required)
    - jobDescription: Target job description text (required, min 50 chars)
    - preserveStructure: Keep original structure (optional, default: true)
    - targetRole: Target job role for optimization (optional)
    
    **Response:**
    - tailoredResume: Optimized resume with enhanced content
    - atsScore: Compatibility score (0-100)
    - matchedKeywords: Keywords from JD found in resume
    - missingKeywords: Important JD keywords not in resume
    - suggestions: Actionable improvement suggestions
    - changes: Summary of modifications made
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📨 New tailor request received")
        logger.info(f"   Resume ID: {request.resume.id}")
        logger.info(f"   Resume Name: {request.resume.name}")
        logger.info(f"   Candidate: {request.resume.personalInfo.name}")
        logger.info(f"   Job Description Length: {len(request.jobDescription)} chars")
        logger.info(f"   Target Role: {request.targetRole or 'Not specified'}")
        logger.info(f"   Preserve Structure: {request.preserveStructure}")
        logger.info("=" * 80)

        # Log resume details for debugging
        logger.debug(f"Resume has {len(request.resume.experience)} work experiences")
        logger.debug(f"Resume has {len(request.resume.projects)} projects")
        logger.debug(f"Resume has {len(request.resume.skills)} skills")

        # Get Gemini service
        try:
            gemini_service = get_gemini_service()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not properly configured. Please check GEMINI_API_KEY.",
            )

        # Tailor resume
        logger.info("🤖 Sending request to Gemini AI...")
        tailor_response = gemini_service.tailor_resume(
            resume=request.resume,
            job_description=request.jobDescription,
        )

        # Check if tailoring succeeded
        if not tailor_response:
            logger.error("❌ Gemini AI failed to tailor resume")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API is currently preserving energy (Rate Limit/Overloaded). Please try again in a moment.",
            )

        # Log success
        logger.info("=" * 80)
        logger.info("✅ Resume tailoring completed successfully")
        logger.info(f"   ATS Score: {tailor_response.atsScore}/100")
        logger.info(f"   Matched Keywords: {len(tailor_response.matchedKeywords)}")
        logger.info(f"   Missing Keywords: {len(tailor_response.missingKeywords)}")
        logger.info(f"   Suggestions: {len(tailor_response.suggestions)}")
        logger.info(f"   Changes Made: {len(tailor_response.changes)}")
        logger.info("=" * 80)

        # Log matched and missing keywords
        logger.info(f"Matched keywords: {', '.join(tailor_response.matchedKeywords[:10])}...")
        if tailor_response.missingKeywords:
            logger.info(
                f"Missing keywords: {', '.join(tailor_response.missingKeywords[:10])}..."
            )

        # Save tailored JSON artifact to a unique session folder
        session_path = artifacts.start_session(request.resume, request.targetRole)
        date_str = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        candidate_name = request.resume.personalInfo.name.replace(" ", "_")
        json_filename = f"{candidate_name}_Tailored_{date_str}.json"
        artifacts.save_json(session_path, tailor_response.model_dump_json(indent=2), json_filename)

        logger.info(f"🧾 Tailored resume JSON saved to: {session_path / json_filename}")

        return tailor_response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Validation errors
        logger.error(f"Validation error: {e}")
        log_error(e, {"request": request.model_dump()})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in tailor endpoint: {e}")
        log_error(
            e,
            {
                "resume_id": request.resume.id,
                "job_description_length": len(request.jobDescription),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request. Please try again later.",
        )


@router.get(
    "/tailor/status",
    status_code=status.HTTP_200_OK,
    summary="Check Tailor Service Status",
    description="Check if AI tailoring service is available",
)
async def tailor_status():
    """
    Check if the AI tailoring service is properly configured and available
    """
    try:
        gemini_service = get_gemini_service()
        return JSONResponse(
            content={
                "status": "available",
                "model": gemini_service.model,
                "message": "AI tailoring service is ready",
            }
        )
    except Exception as e:
        logger.error(f"Tailor service status check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unavailable",
                "error": str(e),
                "message": "AI tailoring service is not properly configured",
            },
        )
