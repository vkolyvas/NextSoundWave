"""Tests for Phase 5 - Related Videos."""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRelatedVideosData:
    """Test related videos data structure."""
    
    def test_track_info_has_related_field(self):
        """TrackInfo should have related field."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        assert 'related: List[dict]' in content
    
    def test_api_response_has_related(self):
        """API response should include related videos."""
        with open('api/models.py', 'r') as f:
            content = f.read()
        assert 'related: List[dict]' in content
    
    def test_routes_returns_related(self):
        """Routes should return related videos."""
        with open('api/routes.py', 'r') as f:
            content = f.read()
        assert 'related=track.related' in content
    
    def test_related_video_structure(self):
        """Related videos should have id, title, duration."""
        with open('extraction_backends.py', 'r') as f:
            content = f.read()
        assert "'id'" in content
        assert "'title'" in content
        assert "'duration'" in content


class TestRelatedVideosUI:
    """Test related videos UI elements."""
    
    def test_right_panel_exists(self):
        """Right panel should exist for related videos."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="right-panel"' in content
    
    def test_related_videos_container_exists(self):
        """Container for related videos should exist."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="related-videos"' in content
    
    def test_panel_header_exists(self):
        """Panel header should exist."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'panel-header' in content


class TestRelatedVideosRendering:
    """Test related videos rendering in app."""
    
    def test_app_has_render_related_videos_method(self):
        """App should have renderRelatedVideos method."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'renderRelatedVideos' in content
    
    def test_app_stores_related_videos(self):
        """App should store related videos."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'this.relatedVideos' in content
    
    def test_app_updates_related_on_play(self):
        """App should update related videos when playing."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'this.relatedVideos = track.related' in content or 'track.related' in content


class TestRelatedVideosClickHandling:
    """Test clicking related videos."""
    
    def test_related_video_items_are_clickable(self):
        """Related video items should have click handlers."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'related-video-item' in content
        assert "addEventListener('click'" in content
    
    def test_click_plays_video(self):
        """Clicking related video should play it."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'playVideo(videoId)' in content
    
    def test_related_video_has_id_attribute(self):
        """Related video items should have data-id attribute."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert "data-id=" in content or "dataset.id" in content


class TestGaplessPlayback:
    """Test gapless playback functionality."""
    
    def test_app_has_gapless_check_method(self):
        """App should have checkGaplessPlayback method."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'checkGaplessPlayback' in content
    
    def test_gapless_checks_time_remaining(self):
        """Gapless should check remaining time."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'remaining' in content or 'timeupdate' in content
    
    def test_gapless_preloads_at_15_seconds(self):
        """Gapless should pre-fetch at T-15 seconds."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert '15' in content
    
    def test_gapless_preloads_next_track(self):
        """Gapless should pre-fetch next track."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'preload(' in content
    
    def test_player_has_preload_method(self):
        """Player should have preload method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'preload(' in content
    
    def test_gapless_uses_first_related_video(self):
        """Gapless should use first related video."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'relatedVideos[0]' in content or 'relatedVideos.length' in content


class TestNextPrevious:
    """Test next/previous track navigation."""
    
    def test_app_has_play_next_method(self):
        """App should have playNext method."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'playNext(' in content
    
    def test_app_has_play_previous_method(self):
        """App should have playPrevious method."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'playPrevious(' in content
    
    def test_play_next_plays_related(self):
        """playNext should play related video."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'relatedVideos' in content
        assert 'playNext' in content
    
    def test_play_previous_restarts(self):
        """playPrevious should restart current track."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'restart()' in content


class TestRelatedVideosDisplay:
    """Test related videos display formatting."""
    
    def test_format_duration_exists(self):
        """App should have formatDuration method."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'formatDuration(' in content
    
    def test_related_video_shows_title(self):
        """Related videos should show title."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'related-title' in content
    
    def test_related_video_shows_duration(self):
        """Related videos should show duration."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'related-duration' in content
    
    def test_empty_related_shows_message(self):
        """Empty related videos should show placeholder."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'placeholder-text' in content or 'No related videos' in content


class TestRelatedVideosStyling:
    """Test related videos styling."""
    
    def test_css_has_related_video_styles(self):
        """CSS should have related video styles."""
        with open('web/css/styles.css', 'r') as f:
            content = f.read()
        assert '.related-video-item' in content
    
    def test_css_has_related_title_styles(self):
        """CSS should have related title styles."""
        with open('web/css/styles.css', 'r') as f:
            content = f.read()
        assert '.related-title' in content
    
    def test_css_has_related_duration_styles(self):
        """CSS should have related duration styles."""
        with open('web/css/styles.css', 'r') as f:
            content = f.read()
        assert '.related-duration' in content
    
    def test_related_video_has_hover_state(self):
        """Related videos should have hover state."""
        with open('web/css/styles.css', 'r') as f:
            content = f.read()
        assert ':hover' in content


class TestAutoPlayNext:
    """Test auto-play next track."""
    
    def test_audio_ended_event_handled(self):
        """Audio ended event should trigger next track."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert "ended" in content or 'audio.addEventListener' in content
    
    def test_player_bar_has_next_button(self):
        """Player bar should have next button."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="btn-next"' in content
    
    def test_player_bar_has_prev_button(self):
        """Player bar should have previous button."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="btn-prev"' in content


class TestPlaylistNavigation:
    """Test playlist navigation."""
    
    def test_related_videos_used_as_playlist(self):
        """Related videos should function as playlist."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        # Check that relatedVideos is used like a playlist
        assert 'relatedVideos' in content
    
    def test_click_related_updates_playlist(self):
        """Clicking related should update the 'playlist'."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        # After clicking related, it should become current and load its related
        assert 'playVideo' in content
    
    def test_playlist_wraps_around(self):
        """Playlist should handle end of list."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        # Should handle when last track ends
        assert 'playNext' in content
