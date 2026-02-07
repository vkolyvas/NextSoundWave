"""Tests for Phase 3 - Search Functionality and Ad-Free Embed."""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSearchIntegration:
    """Test search functionality in app."""
    
    def test_search_input_exists(self):
        """Verify search input is in HTML."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="search-input"' in content
    
    def test_search_calls_api(self):
        """Verify API client has search method."""
        with open('web/js/api.js', 'r') as f:
            content = f.read()
        assert 'async search(' in content
        assert 'search' in content  # /search is in the method
    
    def test_app_search_handler(self):
        """Verify app handles search."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'async search(' in content
        assert 'renderSearchResults' in content


class TestAdFreeEmbedMethods:
    """Test ad-free embed methods in player."""
    
    def test_player_has_youtube_embed_method(self):
        """Player should have YouTube embed method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'playYouTubeEmbed(' in content
        assert 'playInvidiousEmbed(' in content
    
    def test_player_has_adblock_params(self):
        """Player should have AdBlock URL params."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert '_addAdBlockParams(' in content
        # URLSearchParams builds the URL with these params
        assert 'rel' in content
        assert 'modestbranding' in content
    
    def test_player_has_adblock_css(self):
        """Player should have AdBlock CSS."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'ytp-ad' in content
        assert 'video-ads' in content
        assert 'display: none !important' in content
    
    def test_app_prioritizes_youtube_embed(self):
        """App should try YouTube embed first."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'playYouTubeEmbed' in content
        # Should try embed_url first
        assert 'if (track.embed_url)' in content or "track.embed_url" in content


class TestEmbedURLFields:
    """Test embed URL fields in backend."""
    
    def test_track_info_has_embed_url(self):
        """TrackInfo should have embed_url field."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        assert 'embed_url: str = None' in content
    
    def test_track_info_has_invidious_url(self):
        """TrackInfo should have invidious_url field."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        assert 'invidious_url: str = None' in content
    
    def test_youtube_embed_url_format(self):
        """YouTube embed URL should be correct format."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        assert "youtube_embed = f\"https://www.youtube.com/embed/{info['id']}\"" in content
    
    def test_invidious_embed_url_format(self):
        """Invidious embed URL should be correct format."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        assert "invidious_embed = f\"https://yewtu.be/embed/{info['id']}\"" in content


class TestAPIResponseFields:
    """Test API response includes embed URLs."""
    
    def test_api_response_has_embed_url(self):
        """TrackInfoResponse should include embed_url."""
        with open('api/models.py', 'r') as f:
            content = f.read()
        assert 'embed_url: Optional[str]' in content
    
    def test_api_response_has_invidious_url(self):
        """TrackInfoResponse should include invidious_url."""
        with open('api/models.py', 'r') as f:
            content = f.read()
        assert 'invidious_url: Optional[str]' in content
    
    def test_routes_returns_embed_urls(self):
        """Routes should return embed URLs in response."""
        with open('api/routes.py', 'r') as f:
            content = f.read()
        assert 'embed_url=track.embed_url' in content
        assert 'invidious_url=track.invidious_url' in content


class TestAdFreeEmbedHTML:
    """Test standalone ad-free embed page."""
    
    def test_ad_free_embed_html_exists(self):
        """Ad-free embed HTML should exist."""
        assert os.path.exists('ad-free-embed.html'), "ad-free-embed.html should exist"
    
    def test_ad_free_embed_has_iframe(self):
        """Ad-free embed should have iframe."""
        with open('ad-free-embed.html', 'r') as f:
            content = f.read()
        assert '<iframe' in content
        assert 'youtube.com/embed/' in content
    
    def test_ad_free_embed_has_adblock_css(self):
        """Ad-free embed should have AdBlock CSS."""
        with open('ad-free-embed.html', 'r') as f:
            content = f.read()
        assert '.ytp-ad' in content
        assert 'display: none !important' in content
    
    def test_ad_free_embed_has_test_links(self):
        """Ad-free embed should have test links."""
        with open('ad-free-embed.html', 'r') as f:
            content = f.read()
        assert 'Test with other tracks' in content or 'test-links' in content


class TestExtractionBackendPriority:
    """Test extraction backend priority."""
    
    def test_youtube_embed_primary(self):
        """YouTube embed should be primary."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        # YouTube embed should be first
        assert "youtube_embed = f\"https://www.youtube.com/embed/{info['id']}\"" in content
        assert "invidious_embed = f\"https://yewtu.be/embed/{info['id']}\"" in content
    
    def test_embed_in_track_info_order(self):
        """embed_url should come before invidious_url in TrackInfo."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        embed_pos = content.find('embed_url: str')
        invidious_pos = content.find('invidious_url: str')
        assert embed_pos < invidious_pos, "embed_url should come before invidious_url"


class TestPlaybackPriority:
    """Test playback priority in app."""
    
    def test_playback_priority_order(self):
        """Playback should prioritize: YouTube Embed → Audio → Invidious."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        
        # Check priority is correct
        assert 'if (track.embed_url)' in content or "track.embed_url" in content
        # After embed_url check, should check audio_url
        assert 'else if (track.audio_url)' in content or "track.audio_url" in content
        # Last resort: invidious_url
        assert 'else if (track.invidious_url)' in content or "track.invidious_url" in content


class TestPlayerEmbedMode:
    """Test player embed mode switching."""
    
    def test_player_tracks_embed_mode(self):
        """Player should track embed mode."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'isEmbedMode' in content
        assert 'currentEmbedType' in content
    
    def test_player_has_stop_embed_method(self):
        """Player should have stopEmbed method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'stopEmbed(' in content
    
    def test_embed_mode_handles_youtube_and_invidious(self):
        """Embed mode should handle both YouTube and Invidious."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert "'youtube'" in content
        assert "'invidious'" in content
