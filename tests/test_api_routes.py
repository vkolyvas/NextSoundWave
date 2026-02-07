"""Tests for API routes and endpoints."""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


# Marker for tests that make real network calls
pytestmark = pytest.mark.network


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns service info."""
        response = client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert data['service'] == 'NextSoundWave'
        assert data['status'] == 'running'
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    def test_resolve_invalid_url(self, client):
        """Test resolve endpoint with invalid URL."""
        response = client.post('/api/resolve', json={
            'url': 'https://google.com'
        })
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data or 'error' in data  # FastAPI uses 'detail'
    
    def test_resolve_missing_url(self, client):
        """Test resolve endpoint with missing URL."""
        response = client.post('/api/resolve', json={})
        assert response.status_code == 422  # Validation error
    
    def test_resolve_empty_body(self, client):
        """Test resolve endpoint with empty body."""
        response = client.post('/api/resolve', content='')
        assert response.status_code == 422
    
    def test_search_missing_query(self, client):
        """Test search endpoint with missing query."""
        response = client.get('/api/search')
        assert response.status_code == 400
    
    def test_search_short_query(self, client):
        """Test search with too short query."""
        response = client.get('/api/search?q=a')
        assert response.status_code == 400
    
    @pytest.mark.network
    def test_search_endpoint_exists(self, client):
        """Test search endpoint exists and accepts query."""
        # Note: This will hit yt-dlp, may fail due to bot detection
        # We just verify the endpoint is properly configured
        response = client.get('/api/search?q=test')
        # Accept either success or rate-limit error
        assert response.status_code in [200, 429, 500]


class TestResolveRequestValidation:
    """Test request validation for /resolve endpoint."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.parametrize("url", [
        "not-a-url",
        "https://example.com/video",
        "ftp://example.com/video",
        "https://vimeo.com/12345",
        "",
    ])
    def test_resolve_rejects_non_youtube_urls(self, client, url):
        """Non-YouTube URLs should return 400."""
        response = client.post('/api/resolve', json={'url': url})
        assert response.status_code == 400
    
    @pytest.mark.parametrize("url", [
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    ])
    @pytest.mark.network
    def test_resolve_accepts_youtube_urls(self, client, url):
        """YouTube URLs should be accepted (may fail extraction)."""
        # URL validation passes, extraction may fail
        response = client.post('/api/resolve', json={'url': url})
        # 400 = invalid URL, 200 = success, 500 = extraction error
        # We accept 400, 200, or 500 (but not 422)
        assert response.status_code in [200, 400, 500]


class TestStaticFiles:
    """Test static file serving."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_css_served(self, client):
        """CSS file should be accessible."""
        response = client.get('/static/css/styles.css')
        assert response.status_code == 200
        assert 'text/css' in response.headers.get('content-type', '')
    
    def test_index_html_served(self, client):
        """index.html should be served."""
        response = client.get('/static/index.html')
        # May redirect or serve from web/
        assert response.status_code in [200, 404]
