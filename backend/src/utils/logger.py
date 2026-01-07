"""
Centralized logging configuration using loguru
All application logs go to a single file for easy debugging
"""

import sys
from loguru import logger
from pathlib import Path
from app.config import settings

# Remove default handler
logger.remove()

# Create logs directory
log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Console format (with newline for readability)
console_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>\n"
)

# File format (NO trailing newline - loguru adds it automatically)
file_format = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message} | "
    "{extra}"
)

# Console handler (always on)
logger.add(
    sys.stdout,
    format=console_format,
    level=settings.LOG_LEVEL,
    colorize=True,
)

# Centralized application log (ALL logs go here)
logger.add(
    log_dir / "app.log",
    format=file_format,
    level="DEBUG",  # Capture everything
    rotation="50 MB",
    retention="7 days",
    compression="zip",
    enqueue=True,  # Thread-safe
)

# Error-specific log
logger.add(
    log_dir / "error.log",
    format=file_format,
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
)

# Gemini API specific log (for debugging AI interactions)
logger.add(
    log_dir / "gemini.log",
    format=file_format,
    level="DEBUG",
    rotation="25 MB",
    retention="7 days",
    compression="zip",
    enqueue=True,
    filter=lambda record: "gemini" in record["name"].lower() or "ai" in record.get("extra", {}).get("service", "").lower(),
)


# Convenience methods
def log_request(method: str, path: str, status_code: int, duration_ms: float):
    """Log HTTP request with timing information"""
    logger.info(
        f"HTTP {method} {path} - {status_code} - {duration_ms:.2f}ms",
        extra={
            "service": "api",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
        },
    )


def log_ai_request(model: str, prompt_length: int, response_length: int, duration_ms: float):
    """Log AI API request"""
    logger.info(
        f"Gemini API call: model={model}, prompt={prompt_length}chars, response={response_length}chars, duration={duration_ms:.2f}ms",
        extra={
            "service": "gemini",
            "model": model,
            "prompt_length": prompt_length,
            "response_length": response_length,
            "duration_ms": duration_ms,
        },
    )


def log_ai_error(error: Exception, context: dict):
    """Log AI API error with full context"""
    logger.error(
        f"Gemini API error: {str(error)}",
        extra={
            "service": "gemini",
            "error_type": type(error).__name__,
            "context": context,
        },
        exc_info=True,
    )


def log_error(error: Exception, context: dict = None):
    """Log general error with context"""
    logger.error(
        f"Error: {str(error)}",
        extra={
            "service": "general",
            "error_type": type(error).__name__,
            "context": context or {},
        },
        exc_info=True,
    )


# Startup log
logger.info("=" * 80)
logger.info("🚀 Resume Tailor API - Logging initialized")
logger.info(f"📁 Log directory: {log_dir}")
logger.info(f"📊 Log level: {settings.LOG_LEVEL}")
logger.info("=" * 80)


# Export logger
__all__ = ["logger", "log_request", "log_ai_request", "log_ai_error", "log_error"]
