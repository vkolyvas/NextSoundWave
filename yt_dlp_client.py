"""
yt-dlp client wrapper for YouTube extraction.
"""

import re
from typing import List, Optional
from dataclasses import dataclass
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from config import config


@dataclass
class TrackInfo:
    """Represents track metadata and streaming info."""
    id: str
    title: str
    duration: int
    audio_url: str
    related: List[dict]


class YTDLPCClient:
    """Client for interacting with yt-dlp."""
    
    # Regex patterns for YouTube URL formats
    URL_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',  # Without www
    ]
    
    def __init__(self):
        """Initialize yt-dlp client with configured options."""
        # Prioritize Opus (YouTube's best adaptive audio)
        # Format: Opus → WebM audio → bestaudio fallback
        self.ydl_opts = {
            'quiet': True,
            'format': 'bestaudio[acodec=opus]/bestaudio[ext=webm]/bestaudio',
            'extract_flat': False,
            'no_warnings': True,
            'socket_timeout': config.ytdlp.timeout,
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL in any supported format
            
        Returns:
            Video ID string or None if invalid
        """
        if not url:
            return None
        
        # Clean up URL
        url = url.strip()
        
        for pattern in self.URL_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL."""
        return self.extract_video_id(url) is not None
    
    def resolve_track(self, url: str) -> TrackInfo:
        """
        Extract track metadata and audio URL from YouTube URL.
        
        Args:
            url: YouTube URL to resolve
            
        Returns:
            TrackInfo with metadata and direct audio URL
            
        Raises:
            ValueError: If URL is invalid or extraction fails
        """
        # Validate URL
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        ydl_opts = self.ydl_opts.copy()
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Validate required fields
                if not info.get('id'):
                    raise ValueError("Incomplete track data: missing id")
                if not info.get('url'):
                    raise ValueError("Incomplete track data: missing url")
                
                # Extract related videos (best-effort)
                related_videos = []
                if info.get('related_videos'):
                    related_videos = [
                        {
                            'id': v.get('id', ''),
                            'title': v.get('title', 'Unknown'),
                            'duration': v.get('duration') or 0
                        }
                        for v in info.get('related_videos', [])[:10]
                    ]
                
                return TrackInfo(
                    id=info['id'],
                    title=info.get('title', 'Unknown Title'),
                    duration=info.get('duration', 0) or 0,
                    audio_url=info.get('url', ''),
                    related=related_videos
                )
                
        except DownloadError as e:
            raise ValueError(f"Failed to extract track: {e}")
        except KeyError as e:
            raise ValueError(f"Incomplete track data: missing {e}")
    
    def search(self, query: str, limit: int = 20) -> List[dict]:
        """
        Search YouTube for videos.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of search result dictionaries
        """
        ydl_opts = {
            'quiet': True,
            'format': 'bestaudio[acodec=opus]/best[height<=720]',
            'extract_flat': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(
                    f"ytsearch{limit}:{query}",
                    download=False
                )
                
                return [
                    {
                        'id': entry.get('id', ''),
                        'title': entry.get('title', 'Unknown'),
                        'duration': entry.get('duration') or 0,
                        'thumbnail': entry.get('thumbnail', ''),
                    }
                    for entry in results.get('entries', [])
                ]
                
        except DownloadError:
            return []
    
    def download_as_opus(self, url: str, output_path: str = ".") -> dict:
        """
        Download audio as Opus and optionally transcode.
        
        Args:
            url: YouTube URL
            output_path: Directory for output file
            
        Returns:
            Downloaded file info
        """
        ydl_opts = {
            'quiet': False,
            'format': 'bestaudio[acodec=opus]',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'no_warnings': False,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'filepath': f"{output_path}/{info.get('title', 'audio')}.webm",
                    'format': 'opus',
                    'codec': info.get('acodec', 'opus')
                }
        except DownloadError as e:
            raise ValueError(f"Download failed: {e}")
    
    def transcode_to_format(self, url: str, output_format: str = "flac", 
                            output_path: str = ".") -> dict:
        """
        Download and transcode to FLAC, WAV, or AAC.
        
        Args:
            url: YouTube URL
            output_format: Target format (flac, wav, aac, mp3)
            output_path: Directory for output file
            
        Returns:
            Transcoded file info
        """
        if output_format not in ['flac', 'wav', 'aac', 'mp3']:
            raise ValueError(f"Unsupported format: {output_format}")
        
        ydl_opts = {
            'quiet': False,
            'format': 'bestaudio[acodec=opus]',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '192',
            }],
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'title': info.get('title'),
                    'format': output_format,
                    'filepath': f"{output_path}/{info.get('title', 'audio')}.{output_format}"
                }
        except DownloadError as e:
            raise ValueError(f"Transcode failed: {e}")


# Global client instance
ytdlp_client = YTDLPCClient()
