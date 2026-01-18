# Production Deployment Guide

## Prerequisites

- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+
- Python 3.11+
- AWS/GCP/Azure account (for cloud deployment)
- Git

## Local Deployment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/portfolio.git
cd portfolio
```

### 2. Set Up Environment

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit with your production values
nano backend/.env
```

Required environment variables:
- `SUPABASE_URL`: PostgreSQL connection string
- `SUPABASE_KEY`: Database API key
- `GA4_PROPERTY_ID`: Google Analytics 4 property ID
- `GA4_CREDENTIALS_JSON`: Path to GA4 credentials file
- `GEMINI_API_KEY`: Google Gemini API key
- `DEEPSEEK_API_KEY`: DeepSeek API key (fallback)
- `ADMIN_SECRET`: Secret key for JWT signing (generate: `openssl rand -hex 32`)
- `ADMIN_USERNAME`: Admin username
- `ADMIN_PASSWORD`: Admin password
- `REDIS_URL`: Redis connection URL

### 3. Start Services

```bash
# Start all services (PostgreSQL, Redis, Backend, Adminer)
docker-compose up -d

# Expected output: Creating portfolio_db, portfolio_redis, portfolio_backend, portfolio_adminer
```

### 4. Run Migrations

```bash
# Run database migrations
docker exec portfolio_backend alembic upgrade head
```

### 5. Verify Health

```bash
# Check all services running
docker-compose ps

# Expected output: All services in "Up" state

# Verify backend health
curl http://localhost:8000/health

# Expected output: {"status":"ok"}

# Access services:
# - Backend: http://localhost:8000
# - Admin Dashboard: http://localhost:8000/admin
# - Adminer (DB UI): http://localhost:8080
```

### 6. View Logs

```bash
# Backend logs
docker logs portfolio_backend -f

# Database logs
docker logs portfolio_db -f

# Redis logs
docker logs portfolio_redis -f
```

## Cloud Deployment - AWS Example

### 1. Build and Push Image

```bash
# Build image
docker build -t portfolio-backend:latest ./backend

# Tag for AWS ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

docker tag portfolio-backend:latest \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest

docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/portfolio-backend:latest
```

### 2. Deploy with ECS

```bash
# Update ECS task definition with new image URI
# Deploy new task revision to ECS service
aws ecs update-service \
  --cluster portfolio-cluster \
  --service portfolio-backend \
  --force-new-deployment
```

### 3. Alternative: Cloud Run

```bash
# Build and push to Google Cloud Run
gcloud run deploy portfolio-backend \
  --source ./backend \
  --region us-central1 \
  --allow-unauthenticated
```

## Database Backups

### Manual Backup

```bash
# Backup PostgreSQL database
docker exec portfolio_db pg_dump -U portfolio portfolio_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup size check
du -h backup_*.sql
```

### Restore from Backup

```bash
# Restore PostgreSQL database
docker exec -i portfolio_db psql -U portfolio portfolio_ai < backup_20240118_120000.sql
```

### Automated Backups (Cron)

```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * docker exec portfolio_db pg_dump -U portfolio portfolio_ai > /backups/portfolio_$(date +\%Y\%m\%d).sql
```

## Scaling

### Horizontal Scaling

```bash
# Use docker-compose scale for multiple backend instances
docker-compose up -d --scale backend=3

# Or use Kubernetes for production:
# kubectl apply -f k8s/deployment.yaml
```

### Database Connection Pool

Configure in `backend/app/config.py`:
```python
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 3600
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourportfolio.com

# Configure Nginx with SSL
# Copy certificate paths to nginx config:
# ssl_certificate /etc/letsencrypt/live/yourportfolio.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourportfolio.com/privkey.pem;
```

## Troubleshooting

### Backend Service Not Starting

```bash
# Check logs
docker logs portfolio_backend

# Verify environment variables
docker exec portfolio_backend env | grep SUPABASE

# Restart service
docker restart portfolio_backend
```

### Database Connection Failed

```bash
# Verify PostgreSQL is running
docker logs portfolio_db

# Check database credentials
docker exec portfolio_db psql -U portfolio -c "SELECT 1"

# Reset database
docker-compose down -v  # WARNING: Deletes data!
docker-compose up -d db
```

### Redis Connection Issues

```bash
# Verify Redis is running
docker logs portfolio_redis

# Test Redis connection
docker exec portfolio_redis redis-cli ping

# Expected output: PONG
```

## Security Best Practices

1. **Environment Variables**: Never commit .env file to git
2. **Secrets Management**: Use AWS Secrets Manager, Azure Key Vault, or similar
3. **Database**: Restrict PostgreSQL access to VPC/private network
4. **Redis**: Use password authentication and restrict network access
5. **API Keys**: Rotate GA4 and LLM API keys regularly
6. **Admin Access**: Use strong passwords, enable 2FA if possible
7. **CORS**: Restrict ALLOWED_ORIGINS to your domain
8. **Rate Limiting**: Monitor and adjust rate limits based on usage
9. **SSL/TLS**: Always use HTTPS in production
10. **Monitoring**: Enable CloudWatch/Stackdriver for resource monitoring

## Performance Optimization

### Database Indexes

```sql
-- Create indexes for common queries
CREATE INDEX idx_analytics_raw_user_id ON analytics_raw(user_pseudo_id);
CREATE INDEX idx_analytics_raw_event_name ON analytics_raw(event_name);
CREATE INDEX idx_analytics_raw_timestamp ON analytics_raw(event_timestamp);
CREATE INDEX idx_user_segments_user_id ON user_segments(user_pseudo_id);
```

### Connection Pooling

- Configure PostgreSQL max_connections appropriately
- Use connection pool in SQLAlchemy (pool_size, max_overflow)
- Monitor active connections with `SHOW max_connections` in psql

### Redis Optimization

- Set maxmemory policy: `redis-cli CONFIG SET maxmemory-policy allkeys-lru`
- Monitor memory with: `redis-cli INFO memory`
- Use connection pooling for Redis clients

### API Caching

- Personalization rules cached for 1 hour
- User segments cached for 24 hours
- Event types cached for 6 hours
- Enable browser caching for static assets (1 year for versioned files)

## Support & Maintenance

### Health Checks

```bash
# Check backend health
curl -s http://localhost:8000/health | jq .

# Check database health
docker exec portfolio_db pg_isready -U portfolio

# Check Redis health
docker exec portfolio_redis redis-cli ping

# Check metrics endpoint
curl http://localhost:8000/metrics
```

### Log Rotation

Configure Docker to rotate logs:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Update Process

```bash
# Pull latest code
git pull origin main

# Build new image
docker build -t portfolio-backend:latest ./backend

# Stop old container and start new one
docker-compose up -d --no-deps --build backend

# Verify health
curl http://localhost:8000/health
```

## Monitoring

See [MONITORING.md](./MONITORING.md) for detailed monitoring setup with Prometheus and Grafana.

## Rollback Procedure

```bash
# View available image tags
docker images portfolio-backend

# Rollback to previous version
docker run -d -p 8000:8000 portfolio-backend:<previous_tag>

# Or with docker-compose:
# Update image tag in docker-compose.yml
# docker-compose up -d
```

## Contact & Support

For deployment issues, contact: devops@example.com

---

**Last Updated:** January 2026
**Version:** 1.3.0
