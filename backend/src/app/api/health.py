"""
Health check API endpoint
Returns service status and connectivity to dependencies
"""

from fastapi import APIRouter, status
from datetime import datetime
import httpx

from models.resume import HealthResponse
from app.config import settings
from utils.logger import logger

router = APIRouter()


async def check_open_resume_service() -> dict:
    """Check if Open Resume service is reachable"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Changed from /api/health to root endpoint (Module 1 fix)
            response = await client.get(f"{settings.OPEN_RESUME_URL}")
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                }
            else:
                return {"status": "unhealthy", "error": f"Status code: {response.status_code}"}
    except Exception as e:
        logger.error(f"Failed to connect to Open Resume service: {str(e)}")
        return {"status": "unreachable", "error": str(e)}


async def check_gemini_api() -> dict:
    """Check if Gemini API is configured and available"""
    if not settings.GEMINI_API_KEY:
        return {"status": "not_configured", "error": "GEMINI_API_KEY not set"}

    # Check if we can initialize the service
    try:
        from services.gemini import get_gemini_service

        service = get_gemini_service()
        return {
            "status": "configured",
            "model": service.model,
            "key_length": len(settings.GEMINI_API_KEY),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check API health and dependency status",
)
async def health_check():
    """
    Health check endpoint that verifies:
    - API is running
    - Open Resume service connectivity
    - Gemini API configuration
    """
    logger.info("Health check requested")

    # Check dependencies
    open_resume_status = await check_open_resume_service()
    gemini_status = await check_gemini_api()

    response = HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
        services={
            "fastapi": {"status": "healthy"},
            "open_resume": open_resume_status,
            "gemini_ai": gemini_status,
        },
    )

    logger.info(f"Health check completed: {response.services}")
    return response


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Simple Ping",
    description="Simple endpoint to verify API is responsive",
)
async def ping():
    """Simple ping endpoint for quick health checks"""
    return {"ping": "pong", "timestamp": datetime.now()}
