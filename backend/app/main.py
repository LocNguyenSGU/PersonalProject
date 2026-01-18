from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
from prometheus_client import generate_latest
from slowapi.errors import RateLimitExceeded
from app.database import init_db
from app.cache import cache
from app.services.scheduler import start_scheduler
from app.utils.logger import logger
from app.middleware.metrics import MetricsMiddleware
from app.middleware.rate_limit import limiter, rate_limit_error_handler
from app.utils.metrics import metrics_registry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    await init_db()
    await cache.connect()
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down...")
    await cache.disconnect()

app = FastAPI(
    title="Portfolio AI Personalization API",
    description="AI-powered user behavior tracking and portfolio personalization",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)

# Add limiter middleware
app.add_middleware(limiter.LimitMiddleware)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "portfolio-ai-personalization"}

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(metrics_registry),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

# Include routes
from app.api import public, admin
app.include_router(public.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

logger.info("FastAPI app initialized")
