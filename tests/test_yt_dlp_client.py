"""Tests for yt-dlp client module."""

import pytest
from unittest.mock import patch, MagicMock
from yt_dlp_client import YTDLPCClient, TrackInfo


class TestYTDLPCClient:
    """Test cases for YTDLPCClient."""
    
    @pytest.fixture
    def client(self):
        """Create client instance for testing."""
        return YTDLPCClient()
    
    # ========== extract_video_id tests ==========
    
    @pytest.mark.parametrize("url,expected_id", [
        # Standard watch URL
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("http://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        
        # Shortened URL
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("http://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        
        # Embed URL
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        
        # Shorts URL
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        
        # With additional parameters
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=Test", "dQw4w9WgXcQ"),
    ])
    def test_extract_video_id_valid(self, client, url, expected_id):
        """Test extracting video ID from various valid YouTube URL formats."""
        result = client.extract_video_id(url)
        assert result == expected_id
    
    @pytest.mark.parametrize("url", [
        # Invalid URLs
        "https://www.youtube.com",
        "https://www.google.com",
        "https://vimeo.com/123456",
        "not a url",
        "",
        None,
        "https://youtube.com/watch?v=",
        "https://youtube.com/watch?v=invalid",
    ])
    def test_extract_video_id_invalid(self, client, url):
        """Test that invalid URLs return None."""
        result = client.extract_video_id(url)
        assert result is None
    
    # ========== is_valid_youtube_url tests ==========
    
    def test_is_valid_youtube_url_true(self, client):
        """Test valid YouTube URL detection."""
        # Use valid 11-character video IDs
        assert client.is_valid_youtube_url("https://youtube.com/watch?v=abc123defgh") is True
        assert client.is_valid_youtube_url("youtu.be/abc123defgh") is True
    
    def test_is_valid_youtube_url_false(self, client):
        """Test invalid YouTube URL detection."""
        assert client.is_valid_youtube_url("https://google.com") is False
        assert client.is_valid_youtube_url("invalid") is False
        assert client.is_valid_youtube_url("") is False
        assert client.is_valid_youtube_url(None) is False
    
    # ========== resolve_track tests ==========
    
    @patch('yt_dlp_client.YoutubeDL')
    def test_resolve_track_success(self, mock_youtube_dl, client):
        """Test successful track resolution."""
        # Setup mock
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'id': 'dQw4w9WgXcQ',
            'title': 'Rick Astley - Never Gonna Give You Up',
            'duration': 213,
            'url': 'https://rr1---sn-xxxxx.googlevideo.com/...',
            'related_videos': [
                {'id': 'video1', 'title': 'Related 1', 'duration': 180},
                {'id': 'video2', 'title': 'Related 2', 'duration': 200},
            ]
        }
        
        # Execute
        result = client.resolve_track("https://youtube.com/watch?v=dQw4w9WgXcQ")
        
        # Verify
        assert isinstance(result, TrackInfo)
        assert result.id == 'dQw4w9WgXcQ'
        assert result.title == 'Rick Astley - Never Gonna Give You Up'
        assert result.duration == 213
        assert result.audio_url == 'https://rr1---sn-xxxxx.googlevideo.com/...'
        assert len(result.related) == 2
    
    def test_resolve_track_invalid_url(self, client):
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            client.resolve_track("https://google.com")
        assert "Invalid YouTube URL" in str(exc_info.value)
    
    @patch('yt_dlp_client.YoutubeDL')
    def test_resolve_track_missing_data(self, mock_youtube_dl, client):
        """Test handling of incomplete yt-dlp response."""
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'id': 'abc123def45',  # Valid 11-char ID
            # Missing title, duration, url
        }
        
        with pytest.raises(ValueError) as exc_info:
            client.resolve_track("https://youtube.com/watch?v=abc123def45")
        assert "Incomplete track data" in str(exc_info.value)
    
    # ========== search tests ==========
    
    @patch('yt_dlp_client.YoutubeDL')
    def test_search_success(self, mock_youtube_dl, client):
        """Test successful search."""
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'entries': [
                {'id': 'video1', 'title': 'Song 1', 'duration': 180, 'thumbnail': 'thumb1.jpg'},
                {'id': 'video2', 'title': 'Song 2', 'duration': 200, 'thumbnail': 'thumb2.jpg'},
            ]
        }
        
        results = client.search("lofi beats", limit=10)
        
        assert len(results) == 2
        assert results[0]['id'] == 'video1'
        assert results[0]['title'] == 'Song 1'
    
    @patch('yt_dlp_client.YoutubeDL')
    def test_search_empty_results(self, mock_youtube_dl, client):
        """Test search with no results."""
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'entries': []
        }
        
        results = client.search("nonexistent query xyz123")
        assert results == []
    
    @patch('yt_dlp_client.YoutubeDL')
    def test_search_yt_dlp_error(self, mock_youtube_dl, client):
        """Test search handles yt-dlp errors gracefully."""
        from yt_dlp.utils import DownloadError
        mock_youtube_dl.return_value.__enter__.side_effect = DownloadError("Search failed")
        
        results = client.search("test")
        assert results == []


class TestTrackInfo:
    """Test cases for TrackInfo dataclass."""
    
    def test_track_info_creation(self):
        """Test creating TrackInfo instance."""
        track = TrackInfo(
            id='abc123',
            title='Test Track',
            duration=180,
            audio_url='https://example.com/audio',
            related=[{'id': 'rel1', 'title': 'Related', 'duration': 120}]
        )
        
        assert track.id == 'abc123'
        assert track.title == 'Test Track'
        assert track.duration == 180
        assert track.audio_url == 'https://example.com/audio'
        assert len(track.related) == 1
    
    def test_track_info_defaults(self):
        """Test TrackInfo with minimal data."""
        track = TrackInfo(
            id='abc123',
            title='Test',
            duration=0,
            audio_url='',
            related=[]
        )
        
        assert track.related == []
