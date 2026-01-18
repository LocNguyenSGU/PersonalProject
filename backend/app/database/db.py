from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
from app.utils.logger import logger

# Construct database URL
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.SUPABASE_URL.split('//')[1].split('@')[0]}:"
    f"{settings.SUPABASE_KEY}@"
    f"{settings.SUPABASE_URL.split('://')[1]}/postgres"
)

# Use Supabase connection string if available
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
