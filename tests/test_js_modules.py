"""Tests for JavaScript modules (API client, Player)."""

import pytest
import os


class TestJavaScriptFiles:
    """Test JavaScript files exist and have content."""
    
    def test_api_js_exists(self):
        """API client file should exist."""
        assert os.path.exists('web/js/api.js'), "api.js should exist"
    
    def test_api_js_has_class(self):
        """API client should have APIClient class."""
        with open('web/js/api.js', 'r') as f:
            content = f.read()
        assert 'class APIClient' in content
        assert 'async resolve' in content
        assert 'async search' in content
    
    def test_player_js_exists(self):
        """Player file should exist."""
        assert os.path.exists('web/js/player.js'), "player.js should exist"
    
    def test_player_js_has_class(self):
        """Player should have AudioPlayer class."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'class AudioPlayer' in content
        assert 'play(' in content
        assert 'pause(' in content
        assert 'seek(' in content
    
    def test_app_js_exists(self):
        """Main app file should exist."""
        assert os.path.exists('web/js/app.js'), "app.js should exist"
    
    def test_app_js_has_class(self):
        """App should have NextSoundWaveApp class."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'class NextSoundWaveApp' in content
        assert 'async search' in content
        assert 'renderSearchResults' in content
    
    def test_js_files_not_empty(self):
        """JavaScript files should have substantial content."""
        for js_file in ['web/js/api.js', 'web/js/player.js', 'web/js/app.js']:
            with open(js_file, 'r') as f:
                content = f.read()
            assert len(content) > 100, f"{js_file} should have content"


class TestAPIClientInterface:
    """Verify API client has required methods."""
    
    def test_api_client_has_resolve(self):
        """APIClient should have resolve method."""
        with open('web/js/api.js', 'r') as f:
            content = f.read()
        assert 'async resolve(url)' in content or 'async resolve(' in content
    
    def test_api_client_has_search(self):
        """APIClient should have search method."""
        with open('web/js/api.js', 'r') as f:
            content = f.read()
        assert 'async search(' in content
    
    def test_api_client_has_request_method(self):
        """APIClient should have internal request method."""
        with open('web/js/api.js', 'r') as f:
            content = f.read()
        assert 'async request(' in content


class TestAudioPlayerInterface:
    """Verify AudioPlayer has required methods."""
    
    @pytest.fixture
    def player_content(self):
        with open('web/js/player.js', 'r') as f:
            return f.read()
    
    def test_player_has_play(self, player_content):
        """AudioPlayer should have play method."""
        assert 'play(url)' in player_content or 'play(' in player_content
    
    def test_player_has_pause(self, player_content):
        """AudioPlayer should have pause method."""
        assert 'pause(' in player_content
    
    def test_player_has_toggle_play(self, player_content):
        """AudioPlayer should have togglePlay method."""
        assert 'togglePlay(' in player_content
    
    def test_player_has_seek(self, player_content):
        """AudioPlayer should have seek method."""
        assert 'seek(' in player_content
    
    def test_player_has_volume_control(self, player_content):
        """AudioPlayer should have setVolume method."""
        assert 'setVolume(' in player_content
    
    def test_player_has_preload(self, player_content):
        """AudioPlayer should have preload for gapless playback."""
        assert 'preload(' in player_content


class TestAppOrchestrator:
    """Verify main app has required functionality."""
    
    @pytest.fixture
    def app_content(self):
        with open('web/js/app.js', 'r') as f:
            return f.read()
    
    def test_app_has_search_integration(self, app_content):
        """App should integrate with search."""
        assert 'async search(' in app_content
        assert 'renderSearchResults' in app_content
    
    def test_app_has_player_integration(self, app_content):
        """App should integrate with player."""
        assert 'this.player' in app_content
        assert 'updatePlayerUI' in app_content
    
    def test_app_has_related_videos(self, app_content):
        """App should handle related videos."""
        assert 'relatedVideos' in app_content
        assert 'renderRelatedVideos' in app_content
    
    def test_app_has_gapless_playback(self, app_content):
        """App should implement gapless playback logic."""
        assert 'checkGaplessPlayback' in app_content or 'gapless' in app_content
    
    def test_app_has_error_handling(self, app_content):
        """App should have error display."""
        assert 'showError' in app_content
    
    def test_app_has_duration_formatter(self, app_content):
        """App should format duration."""
        assert 'formatDuration' in app_content
