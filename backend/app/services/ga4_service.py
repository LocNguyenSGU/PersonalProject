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

                self._client = BetaAnalyticsDataClient.from_service_account_file(
                    self.credentials_path
                )
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

            from google.analytics.data_v1beta.types import (
                RunReportRequest,
                DateRange,
                Dimension,
                Metric,
                FilterExpression,
                Filter,
            )

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours)

            # Build request
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                    )
                ],
                dimensions=[
                    Dimension(name="eventName"),
                    Dimension(name="customUser:user_pseudo_id"),
                    Dimension(name="eventTimestamp"),
                ],
                metrics=[Metric(name="eventCount")],
                # Filter for custom events only
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="eventName",
                        in_list_filter=Filter.InListFilter(
                            values=[
                                "project_click",
                                "skill_hover",
                                "section_view",
                                "contact_intent",
                                "language_switch",
                                "deep_read",
                                "repeat_view",
                                "scroll_depth",
                                "career_timeline_interact",
                                "download_resume",
                                "external_link_click",
                            ]
                        ),
                    )
                ),
                limit=10000,
            )

            # Execute request
            response = self.client.run_report(request)

            # Format events
            events = []
            for row in response.rows:
                event_name = row.dimension_values[0].value
                user_pseudo_id = row.dimension_values[1].value
                event_timestamp = (
                    int(row.dimension_values[2].value) // 1000000
                )  # Convert micros to seconds

                # Fetch event parameters (requires separate query per event)
                event_params = await self._fetch_event_params(
                    event_name, user_pseudo_id, event_timestamp
                )

                events.append(
                    {
                        "event_name": event_name,
                        "user_pseudo_id": user_pseudo_id,
                        "event_params": event_params,
                        "event_timestamp": event_timestamp,
                        "ga4_event_id": f"{event_name}_{user_pseudo_id}_{event_timestamp}",
                    }
                )

            logger.info(f"Fetched {len(events)} events from GA4")
            return events

        except Exception as e:
            logger.error(f"GA4 fetch failed: {e}")
            # Return empty list to allow graceful degradation
            return []

    async def _fetch_event_params(
        self, event_name: str, user_pseudo_id: str, event_timestamp: int
    ) -> Dict[str, Any]:
        """
        Fetch event parameters for a specific event
        Note: GA4 Data API has limitations on custom parameters - this is a best-effort approach
        """
        try:
            from google.analytics.data_v1beta.types import (
                RunReportRequest,
                DateRange,
                Dimension,
                Metric,
            )

            # Query for custom event parameters
            # Note: Custom parameters must be registered as custom dimensions in GA4
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=datetime.fromtimestamp(event_timestamp).strftime(
                            "%Y-%m-%d"
                        ),
                        end_date=datetime.fromtimestamp(event_timestamp).strftime(
                            "%Y-%m-%d"
                        ),
                    )
                ],
                dimensions=[
                    Dimension(name="customEvent:project_id"),
                    Dimension(name="customEvent:category"),
                    Dimension(name="customEvent:skill_name"),
                    Dimension(name="customEvent:section_name"),
                    Dimension(name="customEvent:duration"),
                    Dimension(name="customEvent:contact_type"),
                ],
                metrics=[Metric(name="eventCount")],
                limit=1,
            )

            response = self.client.run_report(request)

            # Extract parameters from response
            params = {}
            if response.rows:
                row = response.rows[0]
                for i, dim in enumerate(row.dimension_values):
                    if dim.value and dim.value != "(not set)":
                        param_name = request.dimensions[i].name.replace(
                            "customEvent:", ""
                        )
                        params[param_name] = dim.value

            return params

        except Exception as e:
            logger.warning(f"Failed to fetch event params for {event_name}: {e}")
            return {}

    async def get_segment_distribution(self) -> Dict[str, int]:
        """Get user counts by segment from user_segments table"""
        try:
            from sqlalchemy import select, func
            from app.database.models import UserSegment
            from app.database.db import get_async_session

            async with get_async_session() as session:
                # Query segment distribution
                stmt = select(
                    UserSegment.segment, func.count(UserSegment.id).label("count")
                ).group_by(UserSegment.segment)

                result = await session.execute(stmt)
                distribution = {row.segment: row.count for row in result}

                logger.info(f"Segment distribution: {distribution}")
                return distribution

        except Exception as e:
            logger.error(f"Failed to get segment distribution: {e}")
            # Return empty dict on error
            return {}

    def format_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw GA4 event to standard format"""
        return {
            "event_name": event.get("event_name"),
            "user_pseudo_id": event.get("user_id"),
            "event_params": event.get("event_params", {}),
            "event_timestamp": event.get("timestamp_micros", 0) // 1000000,
        }
