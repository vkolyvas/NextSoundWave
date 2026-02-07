# NextSoundWave Port Allocation

| Service | Container Port | Host Port | Status |
|---------|---------------|-----------|--------|
| Frontend (nginx) | 80 | 3000 | ✅ Allocated |
| Backend (FastAPI) | 8000 | 8000 | ✅ Allocated |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                            │
│                                                             │
│  ┌─────────────────┐          ┌─────────────────┐         │
│  │   Frontend      │          │    Backend       │         │
│  │   (nginx)       │  /api/   │   (FastAPI)     │         │
│  │   :80           │◄─────────│   :8000         │         │
│  │                 │          │                 │         │
│  └────────┬────────┘          └────────┬────────┘         │
│           │                            │                   │
│           ▼                            │                   │
│      Port 3000                        │                   │
│     (Host访问)                        │                   │
└─────────────────────────────────────────────────────────────┘
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Web UI |
| Backend API | http://localhost:8000 | API Server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health | http://localhost:8000/api/health | Health Check |

## Quick Commands

```bash
# Start both containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

## Notes

- Frontend proxies `/api/` requests to backend
- All increment by 10 for future services (3010, 3020, etc.)
