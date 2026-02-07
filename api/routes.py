"""
API routes and endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from api.models import (
    ResolveRequest,
    TrackInfoResponse,
    SearchResponse,
    ErrorResponse
)
from yt_dlp_client import ytdlp_client
from extraction_backends import extraction_manager, BackendType


router = APIRouter()


@router.post(
    "/resolve",
    response_model=TrackInfoResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid URL"},
        500: {"model": ErrorResponse, "description": "Extraction error"}
    },
    summary="Resolve YouTube URL",
    description="Extract track metadata and direct audio URL from YouTube"
)
async def resolve_track(request: ResolveRequest):
    """
    Resolve a YouTube URL to get track metadata and streaming URL.
    
    Uses pluggable extraction backends:
    - Primary: yt-dlp (direct extraction, best quality)
    - Fallback: Invidious API (no auth, reliable)
    
    - **url**: YouTube video URL (any format: watch, shorts, embed)
    
    Returns track info including:
    - Video ID
    - Title
    - Duration
    - Direct audio stream URL (Opus codec)
    - Related videos (best-effort)
    """
    try:
        # Use extraction manager with pluggable backends
        result = extraction_manager.extract(request.url)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Extraction failed: {result.error}"
            )
        
        track = result.track
        
        return TrackInfoResponse(
            id=track.id,
            title=track.title,
            duration=track.duration,
            audio_url=track.audio_url,
            embed_url=track.embed_url,
            invidious_url=track.invidious_url,
            related=track.related
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {e}")


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search YouTube",
    description="Search for videos on YouTube"
)
async def search(
    q: str = "",
    limit: int = 20
):
    """
    Search YouTube for videos.
    
    - **q**: Search query string
    - **limit**: Maximum results (1-50, default 20)
    
    Returns list of matching videos with basic metadata.
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters"
        )
    
    try:
        results = ytdlp_client.search(q.strip(), min(limit, 50))
        
        return SearchResponse(
            query=q,
            results=results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {e}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if API server is running"
)
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}


@router.get(
    "/health/extraction",
    summary="Extraction Backend Health",
    description="Check availability of extraction backends"
)
async def extraction_health():
    """
    Check health of extraction backends.
    
    Returns:
    - Primary (yt-dlp) availability
    - Fallback (Invidious) availability
    - Overall status
    - Recommended backend
    """
    health = extraction_manager.health_check()
    return health
