# Backend (FastAPI) - Developer Notes

This backend powers AI resume tailoring and PDF generation. Below are tips for running, testing, and common integration scenarios.

## Quick Start

- Python 3.11+
- Create venv and install deps:

```powershell
cd backend
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

- Run the API:

```powershell
Push-Location backend\src
& ..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
Pop-Location
```

## Environment

Create `backend/.env` (or update via OS env vars):

```
ENVIRONMENT=development
API_URL=http://localhost:8000
OPEN_RESUME_URL=http://localhost:3000
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
LOG_LEVEL=INFO
```

## Testing

- Run all tests:

```powershell
Push-Location backend
& ..\.venv\Scripts\python.exe -m pytest -q
Pop-Location
```

- Coverage:

```powershell
Push-Location backend
& ..\.venv\Scripts\python.exe -m pytest --cov --cov-report=html
Pop-Location
```

### PDF Service Mocking

The test `tests/test_pdf.py::test_generate_pdf_endpoint` mocks the PDF client via:

- `mocker.patch('services.pdf_client.get_pdf_client', ...)` to intercept client creation
- `AsyncMock().generate_pdf.return_value = b'%PDF-1.4 ...'` to simulate successful PDF bytes

Implementation detail:

- `app.api.pdf` imports the module `services.pdf_client` and uses `pdf_client.get_pdf_client()` so the patch applies consistently.

### Gemini JSON Robustness

- Responses are requested as `application/json` and cleaned of any Markdown fences.
- Repair strategy handles:
  - Trailing commas before `}`/`]`
  - Dangling end comma
  - Unterminated strings (closing missing quote)
  - Balancing missing `}`/`]`
- If the first parse fails and the output appears truncated, the service performs a single regeneration request asking Gemini to return the full JSON.
- As a safety net, when `matchedKeywords` is missing/empty, a fallback computes matches from resume skills and job description tokens.

## Logs

- `backend/logs/app.log` (general)
- `backend/logs/error.log` (errors)
- `backend/logs/gemini.log` (AI interactions)

## Common Issues

- "datetime is not JSON serializable" in PDF payloads:
  - The service uses `resume.model_dump_json()` followed by `json.loads(...)` to ensure safe serialization.
- Version mismatch in root endpoint tests:
  - API version is set to `2.0.0` in `app.main` to match tests.

## Tips

- If Gemini frequently truncates responses, consider:
  - Lowering `temperature` (e.g., 0.3)
  - Ensuring `GEMINI_MAX_TOKENS` is high enough (already 8192)
  - Keeping prompts concise; large resumes + detailed JDs can increase output size
