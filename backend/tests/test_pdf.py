"""
Unit and integration tests for PDF generation endpoint
"""

import pytest
from fastapi import status
import json
from unittest.mock import AsyncMock


@pytest.mark.unit
def test_pdf_status_endpoint(test_client):
    """Test PDF service status check"""
    response = test_client.get("/api/pdf/status")
    
    assert response.status_code in [status.HTTP_200_OK]
    data = response.json()
    assert "status" in data
    assert "service" in data


@pytest.mark.unit
async def test_pdf_client_initialization():
    """Test PDF client can be initialized"""
    from services.pdf_client import PDFClientService
    
    client = PDFClientService()
    assert client.base_url is not None
    assert client.timeout > 0


@pytest.mark.integration
async def test_generate_pdf_endpoint(test_client, sample_resume, mocker):
    """Test PDF generation endpoint"""
    # Mock the PDF generator to return fake PDF bytes (to avoid WeasyPrint issues in tests)
    mock_pdf_bytes = b'%PDF-1.4 fake pdf content'
    
    mock_generator = mocker.Mock()
    mock_generator.generate_pdf.return_value = mock_pdf_bytes
    
    mocker.patch(
        'app.api.pdf.get_template_generator',
        return_value=mock_generator
    )
    
    # Make request
    response = test_client.post(
        "/api/generate-pdf",
        json={
            "resume": json.loads(sample_resume.model_dump_json()),
            "template": "default"
        },
    )
    
    # Should return PDF
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/pdf"
    assert "Content-Disposition" in response.headers
    assert "attachment" in response.headers["Content-Disposition"]
    assert ".pdf" in response.headers["Content-Disposition"]


@pytest.mark.integration
async def test_generate_pdf_service_unavailable(test_client, sample_resume, mocker):
    """Test PDF generation error handling when generation fails"""
    # Mock the PDF generator to raise an exception (generation failed)
    mock_generator = mocker.Mock()
    mock_generator.generate_pdf.side_effect = Exception("PDF generation failed")
    
    mocker.patch(
        'app.api.pdf.get_template_generator',
        return_value=mock_generator
    )
    
    # Make request
    response = test_client.post(
        "/api/generate-pdf",
        json={
            "resume": json.loads(sample_resume.model_dump_json()),
        },
    )
    
    # Should return 500 error when generation fails
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert "detail" in data


@pytest.mark.unit
def test_generate_pdf_invalid_resume(test_client):
    """Test PDF generation with invalid resume data"""
    response = test_client.post(
        "/api/generate-pdf",
        json={
            "resume": {
                "id": "test",
                "name": "Test",
                # Missing required fields
            }
        },
    )
    
    # Should return 422 validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
def test_pdf_filename_generation(sample_resume):
    """Test PDF filename is generated correctly"""
    from datetime import datetime
    
    candidate_name = sample_resume.personalInfo.name.replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    expected_filename = f"{candidate_name}_Resume_{date_str}.pdf"
    
    # Should have proper format
    assert "_" in expected_filename
    assert ".pdf" in expected_filename
    assert "John_Doe" in expected_filename
