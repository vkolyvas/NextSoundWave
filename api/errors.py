"""
API error handling.
"""

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class InvalidURLError(Exception):
    """Raised when YouTube URL is invalid."""
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Invalid YouTube URL: {url}")


class ExtractionError(Exception):
    """Raised when yt-dlp extraction fails."""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


def setup_error_handlers(app: FastAPI):
    """Register error handlers with FastAPI app."""
    
    @app.exception_handler(InvalidURLError)
    async def invalid_url_handler(request: Request, exc: InvalidURLError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid URL",
                "detail": str(exc)
            }
        )
    
    @app.exception_handler(ExtractionError)
    async def extraction_error_handler(request: Request, exc: ExtractionError):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Extraction failed",
                "detail": exc.message
            }
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "detail": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if app.debug else "An unexpected error occurred"
            }
        )
