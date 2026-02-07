"""
API request/response models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ResolveRequest(BaseModel):
    """Request body for track resolution."""
    url: str = Field(..., description="YouTube URL to resolve")


class TrackInfoResponse(BaseModel):
    """Response containing track metadata and streaming info."""
    id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Track title")
    duration: int = Field(..., ge=0, description="Duration in seconds")
    audio_url: str = Field(..., description="Direct audio stream URL")
    embed_url: Optional[str] = Field(
        default=None, 
        description="YouTube embed URL (primary)"
    )
    invidious_url: Optional[str] = Field(
        default=None, 
        description="Invidious embed URL (fallback)"
    )
    related: List[dict] = Field(
        default_factory=list,
        description="Related video suggestions"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None


class SearchRequest(BaseModel):
    """Search query request."""
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=20, ge=1, le=50)


class SearchResultItem(BaseModel):
    """Individual search result item."""
    id: str
    title: str
    duration: int = 0
    thumbnail: Optional[str] = None


class SearchResponse(BaseModel):
    """Search results response."""
    query: str
    results: List[SearchResultItem]
