from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.ga4_service import GA4Service
from app.services.llm_service import LLMService
from app.services.analysis_engine import AnalysisEngine
from app.database import async_session
from app.config import settings
from app.utils.logger import logger

scheduler = AsyncIOScheduler()


async def hourly_analysis_job():
    """Runs every hour to analyze GA4 data and generate insights"""
    try:
        logger.info("=" * 50)
        logger.info("HOURLY ANALYSIS JOB STARTED")
        logger.info("=" * 50)

        # Initialize services
        ga4_svc = GA4Service(settings.GA4_CREDENTIALS_JSON, settings.GA4_PROPERTY_ID)
        llm_svc = LLMService(settings.GEMINI_API_KEY, settings.DEEPSEEK_API_KEY)

        async with async_session() as db:
            engine = AnalysisEngine(ga4_svc, llm_svc, db)
            await engine.run_hourly_analysis()

        logger.info("=" * 50)
        logger.info("HOURLY ANALYSIS JOB COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"Analysis job failed: {e}")
        raise


def start_scheduler():
    """Start the APScheduler"""
    try:
        # Add job to run every hour
        scheduler.add_job(hourly_analysis_job, "interval", hours=1)
        scheduler.start()
        logger.info("Scheduler started - jobs will run every hour")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise


# Services package
from app.services.ga4_service import GA4Service
from app.services.llm_service import LLMService
from app.services.analysis_engine import AnalysisEngine
from app.services.scheduler import start_scheduler

__all__ = [
    "GA4Service",
    "LLMService",
    "AnalysisEngine",
    "start_scheduler",
]
