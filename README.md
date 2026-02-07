# NextSoundWave - Self-hosted Music Streaming

Self-hosted music/podcast streaming via YouTube with ad-free embeds.

## Features

- 🎵 **Search** - Find music/podcasts on YouTube
- ▶️ **Playback** - YouTube Embed (with AdBlock) or direct audio
- 🔗 **Related Videos** - Auto-load related content
- 📱 **Responsive UI** - Works on desktop and mobile
- 🚀 **Docker Ready** - Easy deployment with 2 containers

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                             │
│                                                                  │
│   ┌─────────────────┐              ┌─────────────────┐         │
│   │   Frontend      │   /api/     │    Backend       │         │
│   │   (nginx:80)    │────────────▶│   (FastAPI)     │         │
│   │                  │   ◀─────────│   (:8000)       │         │
│   └────────┬────────┘              └────────┬────────┘         │
│            │                               │                   │
│            ▼                               │                   │
│      Port 3000 (Host)                     │                   │
│      http://localhost:3000               │                   │
│                                          │                   │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Docker (Recommended)

```bash
# Start both containers (Frontend + Backend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Local Development

```bash
# Backend only
pip install -r requirements.txt
python main.py

# Access
# Frontend: http://localhost:3000 (via nginx)
# Backend:  http://localhost:8000
```

## Access Points

| Service | Container | Port | URL | Description |
|---------|-----------|------|-----|-------------|
| Frontend | nginx | 3000 | http://localhost:3000 | Web UI |
| Backend | FastAPI | 8000 | http://localhost:8000 | API Server |
| API Docs | FastAPI | 8000 | http://localhost:8000/docs | Swagger UI |
| Health | FastAPI | 8000 | http://localhost:8000/api/health | Health Check |

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
├── Dockerfile              # Backend Docker config
├── docker-compose.yml     # Two-container orchestration
├── nginx/
│   └── default.conf      # Frontend nginx config
├── requirements.txt       # Python dependencies
├── main.py               # FastAPI entry point
├── config.py             # Configuration
├── extraction_backends.py # yt-dlp wrapper
│
├── api/
│   ├── routes.py         # API endpoints
│   ├── models.py         # Pydantic models
│   └── errors.py         # Error handlers
│
├── web/
│   ├── index.html        # Main UI
│   ├── css/styles.css    # Styling
│   └── js/
│       ├── api.js       # API client
│       ├── player.js    # Audio player
│       └── app.js       # Orchestrator
│
└── tests/               # 186 tests
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific phase
pytest tests/test_phase*.py -v
```

## Configuration

Environment variables:
- `SERVER_HOST` - Backend host (default: 0.0.0.0)
- `SERVER_PORT` - Backend port (default: 8000)
- `DEBUG` - Debug mode (default: false)

## License

MIT
