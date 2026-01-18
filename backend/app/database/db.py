from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
from app.utils.logger import logger
import os

# Use DATABASE_URL from env if available, otherwise construct from SUPABASE_URL
if settings.DATABASE_URL:
    # Use provided DATABASE_URL (for testing or custom configs)
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    # Ensure it uses asyncpg driver
    if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
else:
    # Construct from SUPABASE_URL (production)
    SQLALCHEMY_DATABASE_URL = settings.SUPABASE_URL.replace(
        "postgres://", "postgresql+asyncpg://"
    )

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
    pool_pre_ping=True,
    pool_recycle=3600,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
