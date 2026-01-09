"""
PDF Generation API endpoint - FULLY IMPLEMENTED
Generates ATS-friendly PDFs using Open Resume service
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from datetime import datetime

from models.resume import GeneratePDFRequest
from services import pdf_client
from utils import artifacts
from utils.logger import logger, log_error

router = APIRouter()


@router.post(
    "/generate-pdf",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Generate PDF",
    description="Generate ATS-friendly PDF from resume JSON using Open Resume",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF file",
        },
        500: {"description": "PDF generation failed"},
        503: {"description": "Open Resume service unavailable"},
    },
)
async def generate_pdf(request: GeneratePDFRequest):
    try:
        logger.info("=" * 80)
        logger.info(f"📄 PDF generation request received")
        logger.info(f"   Resume ID: {request.resume.id}")
        logger.info(f"   Candidate: {request.resume.personalInfo.name}")
        logger.info(f"   Template: {request.template}")
        logger.info("=" * 80)

        # Get PDF client
        try:
            client = pdf_client.get_pdf_client()
        except Exception as e:
            logger.error(f"Failed to initialize PDF client: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PDF service is not properly configured.",
            )

        # Generate PDF
        logger.info("🔄 Sending request to Open Resume service...")
        pdf_bytes = await client.generate_pdf(request.resume)

        # Check if generation succeeded
        if not pdf_bytes:
            logger.error("❌ PDF generation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF. Please ensure Open Resume service is running and try again.",
            )

        # Generate filename
        candidate_name = request.resume.personalInfo.name.replace(" ", "_")
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{candidate_name}_Resume_{date_str}.pdf"

        logger.info("=" * 80)
        logger.info("✅ PDF generated successfully")
        logger.info(f"   Filename: {filename}")
        logger.info(f"   Size: {len(pdf_bytes) / 1024:.2f} KB")
        logger.info("=" * 80)

        # Save PDF to the latest artifact session (or create a new one)
        session_path = artifacts.get_latest_session(request.resume.id)
        if session_path is None:
            session_path = artifacts.start_session(request.resume)
        artifacts.save_pdf(session_path, pdf_bytes, filename)

        # Return PDF with proper headers
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in generate_pdf endpoint: {e}")
        log_error(
            e,
            {
                "resume_id": request.resume.id,
                "candidate_name": request.resume.personalInfo.name,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating PDF. Please try again later.",
        )


@router.get(
    "/pdf/status",
    status_code=status.HTTP_200_OK,
    summary="Check PDF Service Status",
    description="Check if PDF generation service (Open Resume) is available",
)
async def pdf_status():
    """
    Check if the PDF generation service is properly configured and available
    """
    try:
        client = pdf_client.get_pdf_client()
        is_healthy = await client.check_service_health()

        if is_healthy:
            return {
                "status": "available",
                "service": "Open Resume",
                "url": client.base_url,
                "message": "PDF generation service is ready",
            }
        else:
            return {
                "status": "unavailable",
                "service": "Open Resume",
                "url": client.base_url,
                "message": f"Cannot connect to Open Resume at {client.base_url}",
            }

    except Exception as e:
        logger.error(f"PDF service status check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "PDF generation service is not properly configured",
        }
