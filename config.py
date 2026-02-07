"""
Configuration management for NextSoundWave.
"""

import os
from typing import Optional
from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class YTDLPCConfig(BaseModel):
    """yt-dlp client configuration."""
    # Prioritize Opus (YouTube's best adaptive audio)
    format: str = "bestaudio[acodec=opus]/bestaudio[ext=webm]/bestaudio"
    timeout: int = 30
    max_concurrent_extracts: int = 50


class Config(BaseModel):
    """Application configuration."""
    server: ServerConfig = ServerConfig()
    ytdlp: YTDLPCConfig = YTDLPCConfig()


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        server=ServerConfig(
            host=os.getenv("SERVER_HOST", "0.0.0.0"),
            port=int(os.getenv("SERVER_PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true"
        ),
        ytdlp=YTDLPCConfig(
            format=os.getenv("YTDLP_FORMAT", "bestaudio[ext=m4a]/best"),
            timeout=int(os.getenv("YTDLP_TIMEOUT", "30")),
            max_concurrent_extracts=int(os.getenv("YTDLP_MAX_CONCURRENT", "50"))
        )
    )


# Global config instance
config = load_config()
