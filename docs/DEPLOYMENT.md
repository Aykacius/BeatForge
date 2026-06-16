# BeatForge - Deployment Guide

## Docker Deployment

The project includes a complete Docker Compose setup for local and production deployment.

### Local Development with Docker

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache/broker
- FastAPI backend
- Celery worker
- Next.js frontend

Access the application at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs: http://localhost:8000/docs

### Stopping Services

```bash
docker-compose down
```

### Viewing Logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery
```

## Production Deployment

### Prerequisites
- Docker & Docker Compose installed
- Domain name (optional but recommended)
- SSL certificate (for HTTPS)
- 4GB+ RAM, 20GB+ storage

### Environment Setup

Create production `.env`:

```bash
DEBUG=False
DATABASE_URL=postgresql://user:secure_password@postgres:5432/beatforge
REDIS_URL=redis://redis:6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Production Docker Compose

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Health Checks

```bash
# Check backend
curl http://localhost:8000/health

# Check database
psql -U beatforge -d beatforge -h localhost

# Check Redis
redis-cli ping
```

### Monitoring

- Backend logs: `docker-compose logs backend`
- Celery logs: `docker-compose logs celery`
- Database metrics: Check PostgreSQL logs

## Scaling

### Multiple Celery Workers

```yaml
celery:
  deploy:
    replicas: 3
```

### Database Backups

```bash
docker-compose exec postgres pg_dump -U beatforge beatforge > backup.sql
```

### Restore from Backup

```bash
psql -U beatforge -d beatforge -f backup.sql
```

## Security Considerations

1. **Never commit `.env` files**
2. Use strong database passwords
3. Enable HTTPS in production
4. Use environment-specific configurations
5. Implement rate limiting
6. Validate all user inputs
7. Keep dependencies updated

## Performance Optimization

1. **Caching**: Redis for session and query caching
2. **Async Processing**: Celery for long-running tasks
3. **Database Indexing**: Add indexes on frequently queried columns
4. **CDN**: Serve static assets from CDN
5. **Compression**: Enable gzip compression

## Troubleshooting

### Container won't start
```bash
docker-compose logs <service>
```

### Port already in use
```bash
lsof -i :8000  # Find process on port 8000
kill -9 <PID>
```

### Database connection failed
- Ensure PostgreSQL container is healthy
- Check connection string
- Verify network connectivity

## CI/CD Pipeline

Example GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and test
        run: docker-compose build
      - name: Run tests
        run: docker-compose run backend pytest
      - name: Deploy
        run: docker-compose up -d
```

## Maintenance

### Update Dependencies
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```

### Database Maintenance
```bash
# Vacuum and analyze
VACUUM ANALYZE;

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```
