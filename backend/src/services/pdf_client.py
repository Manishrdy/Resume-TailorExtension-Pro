"""
PDF Client Service for Open Resume integration
Handles communication with Open Resume service for PDF generation
"""

import httpx
from typing import Optional
import time
import json

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
            resume_data = json.loads(resume.model_dump_json())

            # Call Open Resume API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate-pdf",
                    json={"resume": resume_data},
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
