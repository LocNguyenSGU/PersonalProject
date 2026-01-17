from typing import List, Dict, Any
from app.utils.logger import logger
from app.utils.exceptions import GA4Error
from datetime import datetime, timedelta
import json

class GA4Service:
    """Service for fetching data from Google Analytics 4"""
    
    def __init__(self, credentials_path: str, property_id: str):
        self.property_id = property_id
        self.credentials_path = credentials_path
        logger.info(f"GA4Service initialized with property {property_id}")
        
        # Lazy load credentials
        self._client = None
    
    @property
    def client(self):
        """Lazy load GA4 client"""
        if self._client is None:
            try:
                from google.analytics.data_v1beta import BetaAnalyticsDataClient
                self._client = BetaAnalyticsDataClient.from_service_account_file(self.credentials_path)
            except Exception as e:
                logger.error(f"Failed to initialize GA4 client: {e}")
                raise GA4Error(f"GA4 initialization failed: {str(e)}")
        return self._client
    
    async def fetch_events(self, hours: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch GA4 events from last N hours
        Returns formatted event list for analysis
        """
        try:
            logger.info(f"Fetching GA4 events from last {hours} hours")
            
            # Mock implementation for MVP (real GA4 API would be used in Phase 2)
            # For now, return empty list to avoid authentication errors
            events = []
            
            logger.info(f"Fetched {len(events)} events from GA4")
            return events
        except Exception as e:
            logger.error(f"GA4 fetch failed: {e}")
            raise GA4Error(f"Failed to fetch GA4 events: {str(e)}")
    
    async def get_segment_distribution(self) -> Dict[str, int]:
        """Get user counts by segment"""
        try:
            # Mock implementation
            return {
                "ML_ENGINEER": 25,
                "FULLSTACK_DEV": 35,
                "RECRUITER": 30,
                "STUDENT": 8,
                "CASUAL": 2
            }
        except Exception as e:
            logger.error(f"Failed to get segment distribution: {e}")
            raise GA4Error(f"Failed to get segment distribution: {str(e)}")
    
    def format_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw GA4 event to standard format"""
        return {
            "event_name": event.get("event_name"),
            "user_pseudo_id": event.get("user_id"),
            "event_params": event.get("event_params", {}),
            "event_timestamp": event.get("timestamp_micros", 0) // 1000000,
        }
