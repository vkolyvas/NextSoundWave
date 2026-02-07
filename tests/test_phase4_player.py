"""Tests for Phase 4 - Player Module."""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAudioPlayerClass:
    """Test AudioPlayer class exists and has required methods."""
    
    def test_player_js_exists(self):
        """Player JS should exist."""
        assert os.path.exists('web/js/player.js'), "player.js should exist"
    
    def test_player_has_audio_player_class(self):
        """Should have AudioPlayer class."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'class AudioPlayer' in content
    
    def test_player_has_play_method(self):
        """AudioPlayer should have play method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'play(url)' in content or 'play(' in content
    
    def test_player_has_pause_method(self):
        """AudioPlayer should have pause method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'pause(' in content
    
    def test_player_has_resume_method(self):
        """AudioPlayer should have resume method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'resume(' in content
    
    def test_player_has_toggle_play_method(self):
        """AudioPlayer should have togglePlay method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'togglePlay(' in content
    
    def test_player_has_seek_method(self):
        """AudioPlayer should have seek method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'seek(time)' in content or 'seek(' in content
    
    def test_player_has_set_volume_method(self):
        """AudioPlayer should have setVolume method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'setVolume(' in content
    
    def test_player_has_getters(self):
        """AudioPlayer should have currentTime and duration getters."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'get currentTime()' in content or 'currentTime' in content
        assert 'get duration()' in content or 'duration' in content


class TestAudioPlayerState:
    """Test AudioPlayer state management."""
    
    def test_player_tracks_playing_state(self):
        """Player should track isPlaying state."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'isPlaying' in content
    
    def test_player_tracks_embed_mode(self):
        """Player should track embed mode."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'isEmbedMode' in content
    
    def test_player_tracks_current_track(self):
        """Player should track current track."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'currentTrack' in content
    
    def test_player_updates_play_button(self):
        """Player should update play button text."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'updatePlayButton()' in content
        assert "btn-play" in content


class TestPlayerEmbedMode:
    """Test embed mode functionality."""
    
    def test_player_has_youtube_embed_method(self):
        """Player should have playYouTubeEmbed method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'playYouTubeEmbed(' in content
    
    def test_player_has_invidious_embed_method(self):
        """Player should have playInvidiousEmbed method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'playInvidiousEmbed(' in content
    
    def test_player_has_stop_embed_method(self):
        """Player should have stopEmbed method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'stopEmbed(' in content
    
    def test_player_tracks_embed_type(self):
        """Player should track current embed type."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'currentEmbedType' in content


class TestPlayerAdBlock:
    """Test AdBlock functionality."""
    
    def test_player_has_adblock_params_method(self):
        """Player should have _addAdBlockParams method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert '_addAdBlockParams(' in content
    
    def test_player_has_rel_param(self):
        """AdBlock should include rel param."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert "'rel'" in content or '"rel"' in content
    
    def test_player_has_modestbranding_param(self):
        """AdBlock should include modestbranding param."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert "'modestbranding'" in content or '"modestbranding"' in content
    
    def test_player_has_iv_load_policy_param(self):
        """AdBlock should include iv_load_policy param."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert "'iv_load_policy'" in content or '"iv_load_policy"' in content


class TestPlayerEventHandling:
    """Test event handling in player."""
    
    def test_player_listens_to_basic_events(self):
        """Player should listen to basic audio events (play, pause, ended)."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'addEventListener' in content
        assert "addEventListener('play'" in content
        assert "addEventListener('pause'" in content
        assert "addEventListener('ended'" in content
    
    def test_app_handles_metadata_and_progress(self):
        """App should handle loadedmetadata and timeupdate events."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'loadedmetadata' in content
        assert 'timeupdate' in content
        assert 'error' in content


class TestPlayerControls:
    """Test player control integration."""
    
    def test_player_bar_exists_in_html(self):
        """Player bar should exist in HTML."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="player-bar"' in content
    
    def test_player_has_play_button(self):
        """Player should have play button."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="btn-play"' in content
    
    def test_player_has_prev_button(self):
        """Player should have previous button."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="btn-prev"' in content
    
    def test_player_has_next_button(self):
        """Player should have next button."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="btn-next"' in content
    
    def test_player_has_progress_bar(self):
        """Player should have progress slider."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="progress-bar"' in content
    
    def test_player_has_volume_slider(self):
        """Player should have volume slider."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="volume-slider"' in content
    
    def test_player_has_time_display(self):
        """Player should show current and total time."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="current-time"' in content
        assert 'id="total-time"' in content


class TestPlayerTrackInfo:
    """Test track info display."""
    
    def test_player_displays_track_title(self):
        """Player should display track title."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="player-track-title"' in content
    
    def test_player_displays_artist(self):
        """Player should display artist."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="player-artist"' in content
    
    def test_player_displays_thumbnail(self):
        """Player should display track thumbnail."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="player-thumbnail"' in content


class TestPlayerMethods:
    """Test specific player methods."""
    
    def test_player_has_restart_method(self):
        """Player should have restart method."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'restart(' in content
    
    def test_player_has_preload_method(self):
        """Player should have preload method for gapless playback."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert 'preload(' in content
    
    def test_player_has_audio_element_reference(self):
        """Player should reference audio element."""
        with open('web/js/player.js', 'r') as f:
            content = f.read()
        assert "document.getElementById('audio-player')" in content or 'getElementById("audio-player")' in content


class TestAppPlayerIntegration:
    """Test app integration with player."""
    
    def test_app_has_player_reference(self):
        """App should have player reference."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'this.player' in content
    
    def test_app_updates_player_ui(self):
        """App should update player UI."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'updatePlayerUI' in content
    
    def test_app_plays_video(self):
        """App should have playVideo method."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'async playVideo(' in content or 'playVideo(' in content
    
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
    
    def test_app_has_gapless_playback(self):
        """App should have gapless playback check."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'checkGaplessPlayback' in content
    
    def test_app_updates_time_display(self):
        """App should update time display."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'updateTimeDisplay' in content
    
    def test_app_updates_progress(self):
        """App should update progress bar."""
        with open('web/js/app.js', 'r') as f:
            content = f.read()
        assert 'updateProgress' in content
