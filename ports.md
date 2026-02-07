# NextSoundWave Port Allocation

| Service | Port | Increment | Status |
|---------|------|-----------|--------|
| NextSoundWave API | 8000 | Base | ✅ Allocated |

## Notes

- Port 8000: FastAPI server (main service)
- Increment by 10 for future services (8010, 8020, etc.)

## Quick Commands

```bash
# Start with Docker
docker-compose up -d

# View logs
docker-compose logs -f nextsoundwave

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```
