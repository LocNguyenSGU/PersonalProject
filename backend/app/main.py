from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.cache import cache
from app.services.scheduler import start_scheduler
from app.utils.logger import logger

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

# Include routes
from app.api import public, admin
app.include_router(public.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

logger.info("FastAPI app initialized")
