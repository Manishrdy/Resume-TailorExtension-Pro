"""
Configuration management using Pydantic Settings
Loads environment variables and provides typed configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Union
import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env file - go up from app/config.py to backend/.env
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent.parent
env_path = backend_dir / '.env'

print(f"Looking for .env at: {env_path}")

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"WARNING: .env file not found at: {env_path}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Environment
    ENVIRONMENT: str = "development"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_URL: str = "http://localhost:8000"

    # CORS Configuration - accepts string or list
    CORS_ORIGINS: Union[str, List[str]] = "chrome-extension://*,http://localhost:5173,http://localhost:3000"

    # Gemini AI Configuration (NEW google-genai package)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = ""
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 16384
    GEMINI_TIMEOUT: int = 30
    GEMINI_RETRY_ATTEMPTS: int = 3
    GEMINI_RETRY_DELAY: float = 1.0

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"

    # Request Configuration
    REQUEST_TIMEOUT: int = 60
    MAX_RESUME_SIZE: int = 5 * 1024 * 1024

    # Resume Template Styling
    RESUME_ACCENT_COLOR: str = "#1e3a5f"
    RESUME_FONT_FAMILY: str = "Roboto"
    RESUME_FONT_SIZE: int = 9

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        """Convert CORS_ORIGINS to list if it's a string"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
        return self.CORS_ORIGINS


# Create global settings instance
settings = Settings()

# Check for critical configuration
if not settings.GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set in .env file. AI features will not work.")

print(f"Loaded configuration from: {env_path if env_path.exists() else 'Environment Variables'}")
print(f"Environment: {settings.ENVIRONMENT}")
print(f"CORS Origins: {settings.get_cors_origins()}")
