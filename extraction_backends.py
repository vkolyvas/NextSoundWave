"""
Extraction backends for YouTube.

Strategy:
- Server (yt-dlp): Metadata extraction, search, stream URL resolution
- Client (Browser): YouTube Embed with AdBlock → Invidious (last resort)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class BackendType(Enum):
    """Extraction backend types."""
    YT_DLP = "yt-dlp"
    INVIDIOUS = "invidious"


@dataclass
class TrackInfo:
    """Represents track metadata and streaming info."""
    id: str
    title: str
    duration: int
    audio_url: str  # Direct stream URL (from yt-dlp)
    codec: str = "opus"
    backend: BackendType = BackendType.YT_DLP
    related: List[dict] = None
    embed_url: str = None  # Client: YouTube Embed URL (with AdBlock)
    invidious_url: str = None  # Client: Invidious Embed URL (last resort)
    
    def __post_init__(self):
        if self.related is None:
            self.related = []


@dataclass  
class ExtractionResult:
    """Result of extraction attempt."""
    success: bool
    track: Optional[TrackInfo] = None
    error: Optional[str] = None
    backend_used: Optional[BackendType] = None


class ExtractionBackend(ABC):
    """Abstract base class for extraction backends."""
    
    @abstractmethod
    def extract(self, url: str) -> TrackInfo:
        """Extract track info from YouTube URL."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available/healthy."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get backend name for logging."""
        pass


class YTDLPExtractionBackend(ExtractionBackend):
    """Primary backend: yt-dlp for server-side extraction.
    
    Server-side operations:
    - Metadata extraction (title, duration, etc.)
    - YouTube search
    - Direct stream URL resolution
    
    Returns embed URLs for client-side playback.
    """
    
    def __init__(self):
        from yt_dlp import YoutubeDL
        from config import config
        
        self.ydl_opts = {
            'quiet': True,
            'format': 'bestaudio[acodec=opus]/bestaudio[ext=webm]/bestaudio',
            'extract_flat': False,
            'no_warnings': True,
            'socket_timeout': config.ytdlp.timeout,
        }
        self._name = "yt-dlp (server)"
    
    def extract(self, url: str) -> TrackInfo:
        """Extract using yt-dlp (server-side).
        
        Server-side: Gets metadata and direct stream URL.
        Client-side: Uses embed_url for playback.
        """
        from yt_dlp import YoutubeDL
        from yt_dlp.utils import DownloadError
        
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract related videos (best-effort)
                related = []
                if info.get('related_videos'):
                    related = [
                        {
                            'id': v.get('id', ''),
                            'title': v.get('title', 'Unknown'),
                            'duration': v.get('duration') or 0
                        }
                        for v in info.get('related_videos', [])[:10]
                    ]
                
                # Build YouTube embed URL (primary)
                youtube_embed = f"https://www.youtube.com/embed/{info['id']}"
                
                # Build Invidious embed URL (fallback)
                invidious_embed = f"https://yewtu.be/embed/{info['id']}"
                
                # Determine codec
                codec = info.get('acodec', 'opus')
                if not codec or codec == 'none':
                    codec = 'opus'
                
                return TrackInfo(
                    id=info['id'],
                    title=info.get('title', 'Unknown Title'),
                    duration=info.get('duration', 0) or 0,
                    audio_url=info.get('url', ''),
                    codec=codec,
                    backend=BackendType.YT_DLP,
                    related=related,
                    embed_url=youtube_embed,
                    invidious_url=invidious_embed
                )
                
        except DownloadError as e:
            raise ValueError(f"yt-dlp extraction failed: {e}")
    
    def is_available(self) -> bool:
        """Check if yt-dlp is available."""
        try:
            from yt_dlp import YoutubeDL
            return True
        except ImportError:
            return False
    
    def get_name(self) -> str:
        return self._name
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL."""
        import re
        
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class InvidiousExtractionBackend(ExtractionBackend):
    """Last resort backend: Invidious API.
    
    Used when yt-dlp is blocked on server.
    Returns embed URLs for client-side playback.
    
    Priority:
    1. Server: yt-dlp (primary)
    2. Server: Invidious (fallback)
    3. Client: YouTube Embed + AdBlock (primary)
    4. Client: Invidious Embed (last resort)
    """
    
    # Known working Invidious instances (public, no auth, ad-free)
    INSTANCES = [
        "https://yewtu.be",
        "https://invidious.snopyta.org", 
        "https://invidious.kavin.rocks",
        "https://invidious.jingl.xyz",
    ]
    
    def __init__(self, instance_url: str = None):
        self._instance = instance_url or self.INSTANCES[0]
        self._name = f"Invidious ({self._instance})"
    
    def extract(self, url: str) -> TrackInfo:
        """Extract using Invidious API."""
        import re
        import urllib.request
        import json
        
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        # Try to get video info from Invidious
        api_url = f"{self._instance}/api/v1/videos/{video_id}.json"
        
        try:
            req = urllib.request.Request(
                api_url,
                headers={'User-Agent': 'NextSoundWave/1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Get best audio format (prefer opus)
            audio_formats = [f for f in data.get('formatStreams', []) 
                           if f.get('type', '').startswith('audio/')]
            
            best_audio = None
            if audio_formats:
                # Prefer opus, then aac
                for fmt in audio_formats:
                    if 'opus' in fmt.get('type', '').lower():
                        best_audio = fmt
                        break
                if not best_audio:
                    best_audio = audio_formats[0]
            
            # Extract related videos
            related = []
            if data.get('recommendedVideos'):
                related = [
                    {
                        'id': v.get('videoId', ''),
                        'title': v.get('title', 'Unknown'),
                        'duration': 0  # Invidious API doesn't always include duration
                    }
                    for v in data.get('recommendedVideos', [])[:10]
                ]
            
            return TrackInfo(
                id=video_id,
                title=data.get('title', 'Unknown Title'),
                duration=data.get('lengthSeconds', 0) or 0,
                audio_url=best_audio.get('url', '') if best_audio else '',
                codec='opus',
                backend=BackendType.INVIDIOUS,
                related=related,
                embed_url=f"{self._instance}/embed/{video_id}",
                invidious_url=f"{self._instance}/embed/{video_id}"
            )
            
        except Exception as e:
            raise ValueError(f"Invidious extraction failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Invidious instance is available."""
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self._instance}/api/v1/trending",
                headers={'User-Agent': 'NextSoundWave/1.0'},
                method='HEAD'
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False
    
    def get_name(self) -> str:
        return self._name
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL."""
        import re
        
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def find_working_instance(self) -> Optional[str]:
        """Find a working Invidious instance."""
        import urllib.request
        import concurrent.futures
        import threading
        
        def check_instance(instance: str) -> tuple:
            try:
                req = urllib.request.Request(
                    f"{instance}/api/v1/trending",
                    headers={'User-Agent': 'NextSoundWave/1.0'},
                    method='HEAD'
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    return (instance, resp.status == 200)
            except Exception:
                return (instance, False)
        
        # Check instances in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(check_instance, self.INSTANCES))
        
        for instance, available in results:
            if available:
                return instance
        
        return None


class ExtractionManager:
    """
    Pluggable extraction backend manager (SERVER-SIDE).
    
    Strategy:
    1. yt-dlp (primary) - full metadata + stream URL
    2. Invidious (fallback) - when yt-dlp is blocked
    
    Returns embed URLs for CLIENT-SIDE playback:
    - embed_url: YouTube Embed (with AdBlock)
    - invidious_url: Invidious Embed (last resort)
    """
    
    def __init__(self):
        self._primary: ExtractionBackend = YTDLPExtractionBackend()
        self._fallback: Optional[ExtractionBackend] = None
        self._backend_order: List[BackendType] = [BackendType.YT_DLP, BackendType.INVIDIOUS]
    
    def extract(self, url: str, prefer_backend: BackendType = None) -> ExtractionResult:
        """
        Extract track info using available backends.
        
        Args:
            url: YouTube URL to extract
            prefer_backend: Optional preference override
            
        Returns:
            ExtractionResult with track info or error
        """
        # Try preferred backend first if specified
        if prefer_backend == BackendType.INVIDIOUS and self._fallback:
            try:
                track = self._fallback.extract(url)
                return ExtractionResult(
                    success=True,
                    track=track,
                    backend_used=BackendType.INVIDIOUS
                )
            except Exception as e:
                pass  # Fall through to try other backends
        
        # Try primary backend first
        if self._primary.is_available():
            try:
                track = self._primary.extract(url)
                return ExtractionResult(
                    success=True,
                    track=track,
                    backend_used=BackendType.YT_DLP
                )
            except Exception as e:
                pass  # Try fallback
        
        # Initialize fallback if needed
        if not self._fallback:
            self._fallback = InvidiousExtractionBackend()
            # Try to find best instance
            working = self._fallback.find_working_instance()
            if working:
                self._fallback = InvidiousExtractionBackend(working)
        
        # Try fallback
        if self._fallback and self._fallback.is_available():
            try:
                track = self._fallback.extract(url)
                return ExtractionResult(
                    success=True,
                    track=track,
                    backend_used=BackendType.INVIDIOUS
                )
            except Exception as e:
                return ExtractionResult(
                    success=False,
                    error=str(e)
                )
        
        # All backends failed
        return ExtractionResult(
            success=False,
            error="No available extraction backend"
        )
    
    def health_check(self) -> dict:
        """
        Check health of all backends.
        
        Returns:
            Dict with backend availability status
        """
        yt_dlp_available = self._primary.is_available()
        
        # Check Invidious
        if not self._fallback:
            self._fallback = InvidiousExtractionBackend()
        
        invidious_available = self._fallback.is_available()
        
        # Determine overall status
        if yt_dlp_available:
            status = "healthy"
            primary_status = "available"
        elif invidious_available:
            status = "degraded"
            primary_status = "unavailable"
        else:
            status = "unhealthy"
            primary_status = "unavailable"
        
        return {
            "status": status,
            "primary": {
                "backend": "yt-dlp",
                "available": yt_dlp_available
            },
            "fallback": {
                "backend": "invidious",
                "available": invidious_available
            },
            "recommended_backend": BackendType.YT_DLP if yt_dlp_available else BackendType.INVIDIOUS
        }


# Global extraction manager
extraction_manager = ExtractionManager()
