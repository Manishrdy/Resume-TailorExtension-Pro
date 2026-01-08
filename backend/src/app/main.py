"""
Resume Tailor - FastAPI Backend
Main application entry point with API routes, middleware, and logging
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn

from app.api import health, tailor, pdf
from app.config import settings
from utils.logger import logger, log_request

# Initialize FastAPI app
app = FastAPI(
    title="Resume Tailor API",
    description="AI-powered resume optimization and PDF generation service",
    version="2.0.0",  # Align with tests expecting 2.0.0
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Chrome Extension (Module 1 fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # Using helper method
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing"""
    start_time = time.time()

    # Log incoming request
    logger.info(f"➡️  Incoming: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log response
    log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    # Add timing header
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

    return response


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 80)
    logger.info("🚀 Resume Tailor API (Module 3) starting up...")
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 API URL: {settings.API_URL}")
    logger.info(f"📄 PDF Service URL: {settings.OPEN_RESUME_URL}")
    logger.info(f"🤖 Gemini Model: {settings.GEMINI_MODEL}")
    logger.info(f"🔑 Gemini API Key: {'✅ Configured' if settings.GEMINI_API_KEY else '❌ Missing'}")
    logger.info("✅ Server ready to accept requests")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("=" * 80)
    logger.info("🛑 Resume Tailor API shutting down...")
    logger.info("=" * 80)


# Include API routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(tailor.router, prefix="/api", tags=["AI Tailoring"])
app.include_router(pdf.router, prefix="/api", tags=["Document Generation"])


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information"""
    return JSONResponse(
        content={
            "name": "Resume Tailor API",
            "version": "2.0.0",
            "module": "Module 3: PDF Generation (Complete)",
            "status": "running",
            "docs": f"{settings.API_URL}/docs",
            "features": {
                "health_check": "✅ Available",
                "ai_tailoring": "✅ Available (Module 2)",
                "pdf_generation": "✅ Available (Module 3)",
            },
        }
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        f"❌ Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "path": str(request.url.path),
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
