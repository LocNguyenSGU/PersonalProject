from fastapi import APIRouter, Query, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rules import PersonalizationRulesResponse, PersonalizationRequest
from app.models.events import EventPayload, EventResponse
from app.models.segments import UserSegmentResponse
from app.database import get_db
from app.database.models import UserSegment, PersonalizationRules, AnalyticsRaw
from app.utils.logger import logger
from app.middleware.rate_limit import limiter
from app.security.validators import ValidatedEvent
from datetime import datetime

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@router.post("/events", response_model=EventResponse)
@limiter.limit("100/minute")
async def track_event(
    request: Request, event: EventPayload, db: AsyncSession = Depends(get_db)
):
    """
    Fallback custom event tracking endpoint
    Rate limited to 100 requests per minute per IP
    """
    try:
        # Validate event with security validators
        validated = ValidatedEvent(
            event_name=event.event_name,
            user_pseudo_id=event.user_pseudo_id,
            event_params=event.event_params,
            event_timestamp=event.event_timestamp,
        )

        logger.info(
            f"Event received: {validated.event_name} from user {validated.user_pseudo_id}"
        )

        # Save event to analytics_raw
        raw_event = AnalyticsRaw(
            ga4_event_id=f"{validated.user_pseudo_id}_{validated.event_timestamp}_{validated.event_name}",
            event_name=validated.event_name,
            user_pseudo_id=validated.user_pseudo_id,
            event_params=validated.event_params,
            event_timestamp=validated.event_timestamp,
            created_at=datetime.utcnow(),
        )

        db.add(raw_event)
        await db.commit()

        return EventResponse(status="success", message="Event tracked")
    except Exception as e:
        logger.error(f"Failed to track event: {e}")
        raise HTTPException(status_code=500, detail="Failed to track event")


@router.get("/personalization", response_model=PersonalizationRulesResponse)
async def get_personalization(
    user_id: str = Query(...), db: AsyncSession = Depends(get_db)
):
    """Get personalization rules for user's segment"""
    try:
        logger.info(f"Fetching personalization for user {user_id}")

        # Look up user segment
        stmt = select(UserSegment).where(UserSegment.user_pseudo_id == user_id)
        result = await db.execute(stmt)
        user_segment = result.scalar_one_or_none()

        if not user_segment:
            logger.warning(f"No segment found for user {user_id}, returning default")
            # Return default rules
            user_segment = UserSegment(
                user_pseudo_id=user_id,
                segment="CASUAL",
                confidence=0.5,
                reasoning="First visit - no profile yet",
            )

        # Get rules for segment
        stmt = select(PersonalizationRules).where(
            PersonalizationRules.segment == user_segment.segment
        )
        result = await db.execute(stmt)
        rules = result.scalar_one_or_none()

        if not rules:
            logger.info(
                f"No rules found for segment {user_segment.segment}, using defaults"
            )
            return PersonalizationRulesResponse(
                segment=user_segment.segment,
                priority_sections=["projects", "skills", "experience"],
                featured_projects=[],
                highlight_skills=[],
                reasoning="Default rules - no custom rules generated yet",
            )

        return PersonalizationRulesResponse(
            segment=rules.segment,
            priority_sections=rules.priority_sections or [],
            featured_projects=rules.featured_projects or [],
            highlight_skills=rules.highlight_skills or [],
            reasoning=rules.reasoning or "",
        )
    except Exception as e:
        logger.error(f"Failed to get personalization: {e}")
        raise HTTPException(status_code=500, detail="Failed to get personalization")
