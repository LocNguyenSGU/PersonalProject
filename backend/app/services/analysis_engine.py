from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import UserSegment, PersonalizationRules, AnalyticsRaw
from app.services.ga4_service import GA4Service
from app.services.llm_service import LLMService
from app.utils.logger import logger
from app.cache import cache
from datetime import datetime, timedelta

class AnalysisEngine:
    """Core business logic for analyzing users and generating rules"""
    
    def __init__(self, ga4_svc: GA4Service, llm_svc: LLMService, db_session: AsyncSession):
        self.ga4 = ga4_svc
        self.llm = llm_svc
        self.db = db_session
    
    async def segment_user(self, user_pseudo_id: str) -> UserSegment:
        """Classify user into segment based on their events"""
        try:
            logger.info(f"Segmenting user {user_pseudo_id}")
            
            # Check cache first
            cache_key = f"user_segment:{user_pseudo_id}"
            cached_segment = await cache.get(cache_key)
            if cached_segment:
                logger.info(f"Cache hit for user segment {user_pseudo_id}")
                return cached_segment
            
            # Fetch user's events
            stmt = select(AnalyticsRaw).where(
                AnalyticsRaw.user_pseudo_id == user_pseudo_id
            ).order_by(AnalyticsRaw.created_at.desc()).limit(50)
            
            result = await self.db.execute(stmt)
            events = result.scalars().all()
            
            if not events:
                logger.warning(f"No events found for user {user_pseudo_id}")
                # Default segment
                segment_data = {
                    "segment": "CASUAL",
                    "confidence": 0.3,
                    "reasoning": "No events found"
                }
            else:
                # Aggregate event summary
                event_summary = self._aggregate_events(events)
                
                # Call LLM to classify
                segment_data = await self.llm.segment_user(event_summary)
                
                logger.info(f"User {user_pseudo_id} classified as {segment_data['segment']}")
            
            # Save to database
            segment = UserSegment(
                user_pseudo_id=user_pseudo_id,
                segment=segment_data['segment'],
                confidence=segment_data.get('confidence', 0.5),
                reasoning=segment_data.get('reasoning', ''),
                xai_explanation=segment_data.get('xai_explanation', {}),
                event_summary=self._aggregate_events([]),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            self.db.add(segment)
            await self.db.commit()
            
            # Cache the segment with 24-hour TTL (86400 seconds)
            await cache.set(cache_key, {
                "id": segment.id,
                "user_pseudo_id": segment.user_pseudo_id,
                "segment": segment.segment,
                "confidence": segment.confidence,
                "reasoning": segment.reasoning,
                "xai_explanation": segment.xai_explanation,
                "event_summary": segment.event_summary,
                "expires_at": segment.expires_at.isoformat() if segment.expires_at else None
            }, ttl=86400)
            
            return segment
        except Exception as e:
            logger.error(f"Segmentation failed for user {user_pseudo_id}: {e}")
            raise
    
    async def generate_rules_for_segment(self, segment: str) -> PersonalizationRules:
        """Generate personalization rules for a segment"""
        try:
            logger.info(f"Generating rules for segment {segment}")
            
            # Get sample events for this segment
            stmt = select(AnalyticsRaw).join(
                UserSegment,
                AnalyticsRaw.user_pseudo_id == UserSegment.user_pseudo_id
            ).where(
                UserSegment.segment == segment
            ).limit(100)
            
            result = await self.db.execute(stmt)
            sample_events = result.scalars().all()
            
            # Aggregate for LLM
            event_context = self._aggregate_events(sample_events)
            
            # Generate rules
            rules_data = await self.llm.generate_rules(event_context, segment)
            
            logger.info(f"Rules generated for segment {segment}")
            
            # Save to database
            rules = PersonalizationRules(
                segment=segment,
                priority_sections=rules_data.get('priority_sections', []),
                featured_projects=rules_data.get('featured_projects', []),
                highlight_skills=rules_data.get('highlight_skills', []),
                reasoning=rules_data.get('reasoning', ''),
                xai_explanation=rules_data.get('xai_explanation', {})
            )
            
            self.db.add(rules)
            await self.db.commit()
            
            return rules
        except Exception as e:
            logger.error(f"Rule generation failed for segment {segment}: {e}")
            raise
    
    async def run_hourly_analysis(self):
        """Run hourly analysis job"""
        try:
            logger.info("Starting hourly analysis job")
            
            # 1. Fetch last 1h of events
            stmt = select(AnalyticsRaw).where(
                AnalyticsRaw.created_at > datetime.utcnow() - timedelta(hours=1)
            )
            result = await self.db.execute(stmt)
            events = result.scalars().all()
            
            if not events:
                logger.info("No new events to analyze")
                return
            
            # 2. Get unique users
            unique_users = set(event.user_pseudo_id for event in events)
            logger.info(f"Found {len(unique_users)} unique users")
            
            # 3. Segment each user
            for user_id in unique_users:
                try:
                    await self.segment_user(user_id)
                except Exception as e:
                    logger.error(f"Failed to segment user {user_id}: {e}")
            
            # 4. Generate/update rules per segment
            segments = ["ML_ENGINEER", "FULLSTACK_DEV", "RECRUITER", "STUDENT", "CASUAL"]
            for segment in segments:
                try:
                    await self.generate_rules_for_segment(segment)
                except Exception as e:
                    logger.error(f"Failed to generate rules for {segment}: {e}")
            
            logger.info("Hourly analysis job completed")
        except Exception as e:
            logger.error(f"Hourly analysis failed: {e}")
            raise
    
    def _aggregate_events(self, events: list) -> Dict[str, Any]:
        """Aggregate events for LLM analysis"""
        event_types = {}
        for event in events:
            name = event.event_name if hasattr(event, 'event_name') else 'unknown'
            event_types[name] = event_types.get(name, 0) + 1
        
        return {
            "total_events": len(events),
            "unique_event_types": list(event_types.keys()),
            "event_distribution": event_types
        }
