# Deployment Guide

## Pre-deployment Checklist

- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed
- [ ] Security vulnerabilities scanned
- [ ] Environment variables configured
- [ ] Database migrations prepared
- [ ] Backup strategy in place
- [ ] Monitoring and alerting configured
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Rollback plan documented

## Development Environment

### Local Setup

```bash
# Clone and setup
git clone https://github.com/Aykacius/BeatForge.git
cd BeatForge

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Database
cd ..
psql -U postgres
CREATE DATABASE beatforge;
```

## Staging Deployment

### Using Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend python -m alembic upgrade head

# Verify health
curl http://localhost:8000/api/v1/health

# Check logs
docker-compose logs -f
```

### Configuration for Staging

```bash
# backend/.env
ENVIRONMENT=staging
DATABASE_URL=postgresql://user:pass@db-staging:5432/beatforge
REDIS_URL=redis://redis-staging:6379/0
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.beatforge.dev
MAX_FILE_SIZE=52428800
```

## Production Deployment

### Option 1: AWS EC2 + RDS + ElastiCache

#### Architecture

```
┌─────────────────────────────────────────────┐
│ CloudFront (CDN)                            │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ Application Load Balancer                   │
└────────────┬───────────────────┬────────────┘
             │                   │
    ┌────────▼──────┐   ┌────────▼──────┐
    │ EC2 Instance  │   │ EC2 Instance  │
    │ (Backend)     │   │ (Backend)     │
    └────────┬──────┘   └────────┬──────┘
             │                   │
             └────────┬──────────┘
                      │
        ┌─────────────┼──────────────┐
        │             │              │
     ┌──▼──┐    ┌─────▼──┐    ┌────▼────┐
     │ RDS │    │ Redis  │    │   S3    │
     │ DB  │    │ Cache  │    │Storage  │
     └─────┘    └────────┘    └─────────┘
```

#### Setup Steps

```bash
# 1. Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier beatforge-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password <STRONG_PASSWORD> \
  --allocated-storage 100

# 2. Create ElastiCache Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id beatforge-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# 3. Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name beatforge-alb \
  --subnets subnet-xxxxx subnet-yyyyy

# 4. Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name beatforge-asg \
  --launch-configuration-name beatforge-lc \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3
```

#### Environment Variables

```bash
# Store in AWS Systems Manager Parameter Store
aws ssm put-parameter \
  --name /beatforge/prod/DATABASE_URL \
  --type SecureString \
  --value "postgresql://..."

aws ssm put-parameter \
  --name /beatforge/prod/REDIS_URL \
  --type SecureString \
  --value "redis://..."

aws ssm put-parameter \
  --name /beatforge/prod/API_KEY \
  --type SecureString \
  --value "<GENERATED_KEY>"
```

### Option 2: Kubernetes Deployment

#### Kubernetes Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: beatforge
```

```yaml
# k8s/deployment-backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beatforge-backend
  namespace: beatforge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: beatforge-backend
  template:
    metadata:
      labels:
        app: beatforge-backend
    spec:
      containers:
      - name: backend
        image: beatforge:backend-latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: beatforge-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: beatforge-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

```yaml
# k8s/deployment-celery-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beatforge-worker
  namespace: beatforge
spec:
  replicas: 5
  selector:
    matchLabels:
      app: beatforge-worker
  template:
    metadata:
      labels:
        app: beatforge-worker
    spec:
      containers:
      - name: worker
        image: beatforge:backend-latest
        command: ["celery", "-A", "app.workers.celery_tasks", "worker"]
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: beatforge-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "1000m"
          limits:
            memory: "1Gi"
            cpu: "2000m"
```

#### Deploy to Kubernetes

```bash
# Create namespace and secrets
kubectl create namespace beatforge
kubectl create secret generic beatforge-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=redis-url="redis://..." \
  -n beatforge

# Deploy
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments -n beatforge
kubectl get pods -n beatforge

# View logs
kubectl logs -n beatforge -l app=beatforge-backend -f
```

## Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1

# Check migration history
alembic history
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```bash
# Install Certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot certonly --nginx -d beatforge.dev

# Update nginx config
# docker/nginx.conf
server {
    listen 443 ssl http2;
    server_name beatforge.dev;
    
    ssl_certificate /etc/letsencrypt/live/beatforge.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatforge.dev/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of config
}
```

## Monitoring Setup

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'beatforge-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'beatforge-celery'
    static_configs:
      - targets: ['localhost:5555']
```

### Grafana Dashboard

```bash
# Start Grafana
docker run -d -p 3000:3000 grafana/grafana

# Access at http://localhost:3000
# Add Prometheus as data source
# Import dashboard JSON
```

### Alert Rules

```yaml
# monitoring/alerts.yml
groups:
  - name: beatforge
    rules:
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) /
           sum(rate(http_requests_total[5m]))) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: CeleryQueueBacklog
        expr: |
          celery_queue_length > 1000
        for: 10m
        annotations:
          summary: "High Celery queue backlog"
```

## Performance Tuning

### FastAPI Workers

```bash
# Use Gunicorn with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

### Database Connection Pooling

```python
# app/config.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Test connections
    echo_pool=False
)
```

### Redis Optimization

```bash
# Increase max memory and eviction policy
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Backup Strategy

### Database Backups

```bash
# Daily backup to S3
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump $DATABASE_URL | \
  gzip | \
  aws s3 cp - s3://beatforge-backups/db/db_$DATE.sql.gz
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-database.sh
```

## Rollback Procedure

### Docker Compose Rollback

```bash
# If deployment fails, revert to previous version
docker-compose down
git checkout previous-stable-tag
docker-compose up -d
alembic downgrade -1  # Rollback migrations if needed
```

### Kubernetes Rollback

```bash
# Check rollout history
kubectl rollout history deployment/beatforge-backend -n beatforge

# Rollback to previous version
kubectl rollout undo deployment/beatforge-backend -n beatforge

# Verify rollback
kubectl rollout status deployment/beatforge-backend -n beatforge
```

## Post-Deployment Checklist

- [ ] All services healthy
- [ ] API endpoints responding
- [ ] Database migrations applied
- [ ] Monitoring dashboards active
- [ ] Alerts configured and tested
- [ ] Backups running
- [ ] SSL certificate valid
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team notified

## Troubleshooting

### Common Issues

**Service won't start**
```bash
# Check logs
docker-compose logs backend
kubectl logs deployment/beatforge-backend -n beatforge

# Check environment variables
env | grep BEATFORGE
```

**Database connection timeout**
```bash
# Verify connectivity
psql $DATABASE_URL

# Check connection pool
ps aux | grep postgres
```

**High Celery queue backlog**
```bash
# Check number of workers
celery -A app.workers.celery_tasks inspect active

# Scale workers
kubectl scale deployment beatforge-worker --replicas=10 -n beatforge
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs` or `kubectl logs`
2. Verify configuration in environment variables
3. Run health checks: `curl http://localhost:8000/api/v1/health`
4. Review monitoring dashboards
5. Contact DevOps team
