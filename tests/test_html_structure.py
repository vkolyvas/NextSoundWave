"""Tests for frontend HTML structure."""

import pytest
import os


class TestHTMLStructure:
    """Test cases for HTML structure verification."""
    
    @pytest.fixture
    def html_content(self):
        """Read and parse HTML file."""
        html_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'index.html')
        with open(html_path, 'r') as f:
            return f.read()
    
    def test_html_file_exists(self):
        """Verify index.html exists."""
        assert os.path.exists('web/index.html'), "index.html should exist"
    
    def test_has_doctype(self, html_content):
        """HTML should have DOCTYPE declaration."""
        assert '<!DOCTYPE html>' in html_content
    
    def test_has_five_regions(self, html_content):
        """HTML should have all 5 required regions."""
        assert 'id="top-bar"' in html_content, "Missing top-bar"
        assert 'id="sidebar"' in html_content, "Missing sidebar"
        assert 'id="main-content"' in html_content, "Missing main-content"
        assert 'id="right-panel"' in html_content, "Missing right-panel"
        assert 'id="player-bar"' in html_content, "Missing player-bar"
    
    def test_has_search_input(self, html_content):
        """Top bar should have search input."""
        assert 'id="search-input"' in html_content
    
    def test_has_audio_player(self, html_content):
        """Should have hidden audio element."""
        assert 'id="audio-player"' in html_content
        assert '<audio' in html_content
    
    def test_has_player_controls(self, html_content):
        """Player bar should have all control buttons."""
        assert 'id="btn-prev"' in html_content
        assert 'id="btn-play"' in html_content
        assert 'id="btn-next"' in html_content
        assert 'id="progress-bar"' in html_content
        assert 'id="volume-slider"' in html_content
    
    def test_has_player_info_elements(self, html_content):
        """Player should display track info."""
        assert 'id="player-track-title"' in html_content
        assert 'id="player-artist"' in html_content
        assert 'id="player-thumbnail"' in html_content
    
    def test_has_time_display(self, html_content):
        """Player should show time."""
        assert 'id="current-time"' in html_content
        assert 'id="total-time"' in html_content
    
    def test_has_css_link(self, html_content):
        """HTML should link to stylesheet."""
        assert 'href="/static/css/styles.css"' in html_content
    
    def test_has_js_script(self, html_content):
        """HTML should include main JavaScript."""
        assert 'src="/static/js/app.js"' in html_content


class TestNavigationStructure:
    """Test navigation and sidebar structure."""
    
    @pytest.fixture
    def html_content(self):
        """Read HTML file."""
        with open('web/index.html', 'r') as f:
            return f.read()
    
    def test_has_sidebar_nav(self, html_content):
        """Sidebar should have navigation list."""
        assert 'id="sidebar"' in html_content
        assert 'nav-list' in html_content
    
    def test_has_required_nav_items(self, html_content):
        """Should have Home, Explore, Library navigation."""
        assert 'Home' in html_content
        assert 'Explore' in html_content
        assert 'Library' in html_content
    
    def test_has_user_avatar(self, html_content):
        """Top bar should have user avatar."""
        assert 'class="user-avatar"' in html_content or 'user-avatar' in html_content


class TestMainContentArea:
    """Test main content area structure."""
    
    def test_main_content_has_placeholder(self):
        """Main content should have placeholder text."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'id="content-area"' in content
    
    def test_right_panel_has_header(self):
        """Right panel should have header."""
        with open('web/index.html', 'r') as f:
            content = f.read()
        assert 'class="panel-header"' in content or 'panel-header' in content


class TestCSSFile:
    """Test CSS file exists and has content."""
    
    def test_css_file_exists(self):
        """Verify styles.css exists."""
        assert os.path.exists('web/css/styles.css'), "styles.css should exist"
    
    def test_css_has_content(self):
        """CSS file should not be empty."""
        with open('web/css/styles.css', 'r') as f:
            content = f.read()
        assert len(content) > 100, "CSS file should have substantial content"
    
    def test_css_defines_css_variables(self):
        """CSS should define CSS variables for theming."""
        with open('web/css/styles.css', 'r') as f:
            content = f.read()
        assert ':root' in content or '--bg-' in content
    
    def test_css_has_responsive_rules(self):
        """CSS should have responsive/mobile rules."""
        with open('web/css/styles.css', 'r') as f:
            content = f.read()
        assert '@media' in content
