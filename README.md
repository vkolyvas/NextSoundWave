# NextSoundWave - Self-hosted Music Streaming

Self-hosted music/podcast streaming via YouTube with ad-free embeds.

## Features

- 🎵 **Search** - Find music/podcasts on YouTube
- ▶️ **Playback** - YouTube Embed (with AdBlock) or direct audio
- 🔗 **Related Videos** - Auto-load related content
- 📱 **Responsive UI** - Works on desktop and mobile
- 🚀 **Docker Ready** - Easy deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVER (yt-dlp)                              │
│  • Search YouTube                                             │
│  • Extract metadata + stream URL                               │
│  • Extract related videos                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                          │
│  Playback Priority:                                           │
│  1. YouTube Embed + AdBlock (PRIMARY)                      │
│  2. Direct Audio Stream (fallback)                           │
│  3. Invidious Embed (last resort)                            │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f nextsoundwave

# Stop
docker-compose down
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Access

- **Web UI:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resolve` | Resolve YouTube URL to track info |
| GET | `/api/search?q=<query>` | Search YouTube |
| GET | `/api/health` | Health check |
| GET | `/api/health/extraction` | Backend health |

## Project Structure

```
NextSoundWave/
├── Dockerfile              # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── main.py                # FastAPI entry point
├── config.py              # Configuration management
├── pytest.ini             # Pytest configuration
├── ports.md               # Port allocation
│
├── yt_dlp_client.py       # yt-dlp wrapper
├── extraction_backends.py  # Extraction backend manager
│
├── api/
│   ├── routes.py          # API endpoints
│   ├── errors.py          # Error handlers
│   └── models.py          # Pydantic models
│
├── web/
│   ├── index.html         # Main HTML template
│   ├── css/styles.css     # UI styling
│   └── js/
│       ├── api.js         # API client
│       ├── player.js      # Audio player wrapper
│       └── app.js         # Main orchestrator
│
└── tests/                 # Test suite (155 tests)
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_phase*.py -v

# Run with coverage
pytest --cov=. tests/
```

## Configuration

Environment variables:
- `SERVER_HOST` - Server host (default: 0.0.0.0)
- `SERVER_PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: false)
- `YTDLP_TIMEOUT` - yt-dlp timeout (default: 30s)

## Port Allocation

| Service | Port | Status |
|---------|------|--------|
| NextSoundWave API | 8000 | ✅ Allocated |

See [ports.md](ports.md) for details.

## License

MIT
