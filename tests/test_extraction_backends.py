"""Tests for pluggable extraction backends."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extraction_backends import (
    BackendType,
    TrackInfo,
    ExtractionResult,
    YTDLPExtractionBackend,
    InvidiousExtractionBackend,
    ExtractionManager,
)


class TestBackendType:
    """Test BackendType enum."""
    
    def test_enum_values(self):
        assert BackendType.YT_DLP.value == "yt-dlp"
        assert BackendType.INVIDIOUS.value == "invidious"


class TestTrackInfo:
    """Test TrackInfo dataclass."""
    
    def test_track_info_creation(self):
        track = TrackInfo(
            id="abc123",
            title="Test Track",
            duration=180,
            audio_url="https://example.com/audio.webm",
            codec="opus",
            backend=BackendType.YT_DLP
        )
        
        assert track.id == "abc123"
        assert track.title == "Test Track"
        assert track.duration == 180
        assert track.codec == "opus"
        assert track.backend == BackendType.YT_DLP
        assert track.related == []
    
    def test_track_info_with_related(self):
        related = [{"id": "rel1", "title": "Related", "duration": 120}]
        track = TrackInfo(
            id="abc123",
            title="Test",
            duration=180,
            audio_url="https://example.com/audio.webm",
            related=related
        )
        
        assert len(track.related) == 1


class TestExtractionResult:
    """Test ExtractionResult dataclass."""
    
    def test_success_result(self):
        track = TrackInfo(id="abc", title="Test", duration=180, audio_url="url")
        result = ExtractionResult(success=True, track=track, backend_used=BackendType.YT_DLP)
        
        assert result.success is True
        assert result.track == track
        assert result.error is None
    
    def test_failure_result(self):
        result = ExtractionResult(success=False, error="Failed", backend_used=None)
        
        assert result.success is False
        assert result.track is None
        assert result.error == "Failed"


class TestYTDLPExtractionBackend:
    """Test yt-dlp backend (server-side extraction)."""
    
    @pytest.fixture
    def backend(self):
        return YTDLPExtractionBackend()
    
    def test_is_available(self, backend):
        """yt-dlp should be available."""
        assert backend.is_available() is True
    
    def test_get_name(self, backend):
        """Backend should have name."""
        assert "yt-dlp" in backend.get_name()
        assert "server" in backend.get_name()
    
    def test_extract_video_id_valid(self, backend):
        """Should extract video ID from valid URLs."""
        assert backend._extract_video_id("https://youtube.com/watch?v=abc123defgh") == "abc123defgh"
        assert backend._extract_video_id("https://youtu.be/abc123defgh") == "abc123defgh"
        assert backend._extract_video_id("https://youtube.com/shorts/abc123defgh") == "abc123defgh"
    
    def test_extract_video_id_invalid(self, backend):
        """Should return None for invalid URLs."""
        assert backend._extract_video_id("https://google.com") is None
        assert backend._extract_video_id("not-a-url") is None
        assert backend._extract_video_id("") is None
    
    @patch('yt_dlp.YoutubeDL')
    def test_extract_success(self, mock_youtube_dl, backend):
        """Test successful extraction (server-side)."""
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'id': 'abc123defgh',
            'title': 'Test Track',
            'duration': 180,
            'url': 'https://example.com/audio.webm',
            'acodec': 'opus',
            'related_videos': [
                {'id': 'rel1', 'title': 'Related 1', 'duration': 120}
            ]
        }
        
        track = backend.extract("https://youtube.com/watch?v=abc123defgh")
        
        assert track.id == "abc123defgh"
        assert track.title == "Test Track"
        assert track.duration == 180
        assert track.backend == BackendType.YT_DLP
        # Embed URLs for client-side playback
        assert track.embed_url == "https://www.youtube.com/embed/abc123defgh"
        assert track.invidious_url == "https://yewtu.be/embed/abc123defgh"
    
    def test_extract_invalid_url(self, backend):
        """Should raise ValueError for invalid URL."""
        with pytest.raises(ValueError) as exc_info:
            backend.extract("https://google.com")
        assert "Invalid YouTube URL" in str(exc_info.value)


class TestInvidiousExtractionBackend:
    """Test Invidious backend."""
    
    @pytest.fixture
    def backend(self):
        return InvidiousExtractionBackend()
    
    def test_get_name(self, backend):
        """Backend should have name."""
        assert "Invidious" in backend.get_name()
    
    def test_extract_video_id_valid(self, backend):
        """Should extract video ID."""
        assert backend._extract_video_id("https://youtube.com/watch?v=abc123defgh") == "abc123defgh"
    
    def test_extract_video_id_invalid(self, backend):
        """Should return None for invalid."""
        assert backend._extract_video_id("https://google.com") is None
    
    @patch('urllib.request.urlopen')
    def test_extract_success(self, mock_urlopen, backend):
        """Test successful extraction via Invidious."""
        import json
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'title': 'Test Track',
            'lengthSeconds': 180,  # Can be int or string
            'videoId': 'abc123defgh',
            'formatStreams': [
                {'url': 'https://example.com/audio.webm', 'type': 'audio/webm; codecs="opus"'}
            ],
            'recommendedVideos': [
                {'videoId': 'rel1', 'title': 'Related 1'}
            ]
        }).encode()
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_response)
        mock_context.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_context
        
        track = backend.extract("https://youtube.com/watch?v=abc123defgh")
        
        assert track.id == "abc123defgh"
        assert track.title == "Test Track"
        assert track.duration == 180
        assert track.backend == BackendType.INVIDIOUS
        assert track.codec == "opus"
    
    def test_extract_invalid_url(self, backend):
        """Should raise ValueError for invalid URL."""
        with pytest.raises(ValueError) as exc_info:
            backend.extract("https://google.com")
        assert "Invalid YouTube URL" in str(exc_info.value)
    
    @patch('urllib.request.urlopen')
    def test_find_working_instance(self, mock_urlopen):
        """Test finding working Invidious instance."""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=MagicMock(status=200))
        mock_context.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_context
        
        backend = InvidiousExtractionBackend()
        instance = backend.find_working_instance()
        
        assert instance is not None
        assert "yewtu.be" in instance or "invidious" in instance


class TestExtractionManager:
    """Test ExtractionManager."""
    
    @pytest.fixture
    def manager(self):
        return ExtractionManager()
    
    def test_health_check_structure(self, manager):
        """Health check should return proper structure."""
        health = manager.health_check()
        
        assert "status" in health
        assert "primary" in health
        assert "fallback" in health
        assert health["primary"]["backend"] == "yt-dlp"
        assert health["fallback"]["backend"] == "invidious"
    
    @pytest.fixture
    def manager_with_mocks(self):
        """Create manager with mock backends."""
        manager = ExtractionManager()
        
        # Create mock primary
        mock_primary = MagicMock(spec=YTDLPExtractionBackend)
        mock_primary.is_available.return_value = True
        
        # Create mock fallback
        mock_fallback = MagicMock(spec=InvidiousExtractionBackend)
        mock_fallback.is_available.return_value = True
        
        manager._primary = mock_primary
        manager._fallback = mock_fallback
        
        return manager
    
    def test_extract_with_fallback(self, manager_with_mocks):
        """Test extraction with fallback when primary fails."""
        manager = manager_with_mocks
        
        # Primary fails
        manager._primary.extract.side_effect = Exception("yt-dlp failed")
        
        # Fallback succeeds
        fallback_track = TrackInfo(
            id="abc123",
            title="Fallback Track",
            duration=180,
            audio_url="https://example.com/audio.webm",
            backend=BackendType.INVIDIOUS
        )
        manager._fallback.extract.return_value = fallback_track
        
        result = manager.extract("https://youtube.com/watch?v=abc123")
        
        assert result.success is True
        assert result.backend_used == BackendType.INVIDIOUS
    
    def test_extract_all_backends_fail(self, manager_with_mocks):
        """Test behavior when all backends fail."""
        manager = manager_with_mocks
        manager._primary.is_available.return_value = False
        manager._fallback.is_available.return_value = False
        
        result = manager.extract("https://youtube.com/watch?v=abc123")
        
        assert result.success is False
        assert "No available" in result.error
    
    def test_recommended_backend_yt_dlp_available(self, manager):
        """Should recommend yt-dlp when available."""
        with patch.object(manager._primary, 'is_available', return_value=True):
            health = manager.health_check()
            assert health["recommended_backend"] == BackendType.YT_DLP
    
    def test_recommended_backend_invidious_fallback(self, manager_with_mocks):
        """Should recommend Invidious when yt-dlp unavailable."""
        manager = manager_with_mocks
        manager._primary.is_available.return_value = False
        
        health = manager.health_check()
        assert health["recommended_backend"] == BackendType.INVIDIOUS
