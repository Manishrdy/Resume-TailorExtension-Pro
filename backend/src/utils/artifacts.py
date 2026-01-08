"""
Artifact management utility for saving tailored resumes (JSON) and PDFs
Creates a unique folder per tailoring session and keeps track of latest by resume id.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any, Union
import time
import re
import json

from models.resume import Resume
from utils.logger import logger

# Base directory for artifacts
BASE_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# In-memory map of latest session path per resume id
_latest_sessions: Dict[str, Path] = {}


def _sanitize(value: Optional[str]) -> str:
    if not value:
        return "unknown"
    return re.sub(r"[^A-Za-z0-9_\-]", "_", value.strip()) or "unknown"


def start_session(resume: Resume, target_role: Optional[str] = None) -> Path:
    """Create a unique folder for a tailoring session and remember it by resume id."""
    ts = time.strftime("%Y%m%d-%H%M%S")
    candidate = _sanitize(resume.personalInfo.name)
    resume_id = _sanitize(resume.id)
    role = _sanitize(target_role) if target_role else "general"
    path = BASE_DIR / candidate / resume_id / f"{ts}-{role}"
    path.mkdir(parents=True, exist_ok=True)
    _latest_sessions[resume.id] = path
    logger.info(f"📁 Artifact session created: {path}")
    return path


def get_latest_session(resume_id: str) -> Optional[Path]:
    """Return the latest session path for a resume id, if any."""
    return _latest_sessions.get(resume_id)


def save_json(path: Path, data: Union[Dict[str, Any], str], filename: Optional[str] = None) -> Path:
    """Save JSON content (dict or JSON string) to the given path."""
    fname = filename or "tailored_resume.json"
    file_path = path / fname
    with file_path.open("w", encoding="utf-8") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            # Fallback serializer for non-JSON-native types (e.g., datetime)
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"📝 Saved tailored JSON: {file_path}")
    return file_path


def save_pdf(path: Path, pdf_bytes: bytes, filename: str) -> Path:
    """Save PDF bytes to the given path with the specified filename."""
    file_path = path / filename
    with file_path.open("wb") as f:
        f.write(pdf_bytes)
    logger.info(f"📄 Saved PDF: {file_path} ({len(pdf_bytes)/1024:.2f} KB)")
    return file_path

