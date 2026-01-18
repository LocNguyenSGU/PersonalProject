#!/bin/bash
# scripts/deploy.sh - Production deployment automation
# Usage: ./scripts/deploy.sh

set -e

echo "🚀 Starting deployment..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/yourusername/portfolio.git"
BRANCH="main"
DEPLOY_DIR="/opt/portfolio"
BACKUP_DIR="/opt/backups"

# 1. Update code
echo -e "${YELLOW}📦 Pulling latest code from $BRANCH branch...${NC}"
cd "$DEPLOY_DIR"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"
echo -e "${GREEN}✓ Code updated${NC}"

# 2. Backup database
echo -e "${YELLOW}💾 Backing up database...${NC}"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/portfolio_$(date +%Y%m%d_%H%M%S).sql"
docker exec portfolio_db pg_dump -U portfolio portfolio_ai > "$BACKUP_FILE"
echo -e "${GREEN}✓ Database backed up to $BACKUP_FILE${NC}"

# 3. Build Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t portfolio-backend:$(git rev-parse --short HEAD) ./backend
docker tag portfolio-backend:$(git rev-parse --short HEAD) portfolio-backend:latest
echo -e "${GREEN}✓ Docker image built${NC}"

# 4. Stop old containers
echo -e "${YELLOW}🛑 Stopping old containers...${NC}"
docker-compose down
echo -e "${GREEN}✓ Old containers stopped${NC}"

# 5. Start new containers
echo -e "${YELLOW}▶️  Starting new containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ New containers started${NC}"

# 6. Run migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
docker exec portfolio_backend alembic upgrade head
echo -e "${GREEN}✓ Migrations complete${NC}"

# 7. Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 5

# 8. Verify deployment
echo -e "${YELLOW}✅ Verifying deployment...${NC}"

# Check backend health
if curl -s http://localhost:8000/health | jq . > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "  Rolling back..."
    docker-compose down -v
    exit 1
fi

# Check database
if docker exec portfolio_db pg_isready -U portfolio > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is accessible${NC}"
else
    echo -e "${RED}✗ Database is not accessible${NC}"
    exit 1
fi

# Check Redis
if docker exec portfolio_redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is accessible${NC}"
else
    echo -e "${RED}✗ Redis is not accessible${NC}"
    exit 1
fi

# 9. Run smoke tests (optional)
echo -e "${YELLOW}🧪 Running smoke tests...${NC}"
if [ -f "backend/tests/smoke_test.sh" ]; then
    bash backend/tests/smoke_test.sh
    echo -e "${GREEN}✓ Smoke tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  No smoke tests found (optional)${NC}"
fi

# 10. Log deployment
echo -e "${GREEN}✨ Deployment complete!${NC}"
echo ""
echo "Deployment Summary:"
echo "  Timestamp: $(date)"
echo "  Commit: $(git rev-parse --short HEAD)"
echo "  Branch: $BRANCH"
echo "  Backup: $BACKUP_FILE"
echo ""
echo "Services:"
echo "  Backend: http://localhost:8000"
echo "  Admin Dashboard: http://localhost:8000/admin"
echo "  Database UI (Adminer): http://localhost:8080"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000"
echo ""
echo "Next steps:"
echo "  - Verify services in browser"
echo "  - Check logs: docker logs portfolio_backend -f"
echo "  - Monitor metrics: http://localhost:9090"
echo ""
echo "To rollback:"
echo "  - docker-compose down"
echo "  - git checkout <previous-commit>"
echo "  - docker-compose up -d"
echo "  - docker exec portfolio_backend alembic upgrade head"

# 11. Clean up old backups (keep only last 10)
echo -e "${YELLOW}🧹 Cleaning up old backups...${NC}"
cd "$BACKUP_DIR"
ls -t portfolio_*.sql | tail -n +11 | xargs -r rm
echo -e "${GREEN}✓ Cleanup complete${NC}"

exit 0
