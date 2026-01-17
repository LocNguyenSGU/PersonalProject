from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import timedelta
from app.auth.jwt import create_access_token, verify_admin, verify_password
from app.config import settings
from app.utils.logger import logger

# Admin routes
router = APIRouter(prefix="/api/admin", tags=["admin"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 28800  # 8 hours in seconds

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Admin login endpoint
    Returns JWT token for authenticated admin access
    
    In production, username/password should be stored in environment variables
    or a secure user management system
    """
    try:
        # Simple authentication (for MVP - enhance in production)
        # In production, compare against hashed password from database
        admin_username = settings.ADMIN_USERNAME
        admin_password = settings.ADMIN_PASSWORD
        
        if request.username != admin_username or request.password != admin_password:
            logger.warning(f"Failed login attempt for user: {request.username}")
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": "admin", "username": request.username},
            expires_delta=timedelta(hours=8)
        )
        
        logger.info(f"Admin login successful: {request.username}")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=28800
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/trigger-analysis", dependencies=[Depends(verify_admin)])
async def trigger_analysis():
    """
    Manually trigger analysis job (protected endpoint)
    Requires valid JWT token in Authorization header
    """
    try:
        # TODO: Implement manual analysis trigger
        logger.info("Manual analysis triggered by admin")
        return {"status": "triggered", "message": "Analysis job queued"}
    except Exception as e:
        logger.error(f"Failed to trigger analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger analysis")

@router.get("/segments", dependencies=[Depends(verify_admin)])
async def get_segments():
    """Get user segment distribution"""
    try:
        from sqlalchemy import select, func
        from app.database.models import UserSegment
        from app.database.db import get_async_session
        
        async with get_async_session() as session:
            # Get total users
            total_stmt = select(func.count(UserSegment.id))
            total_result = await session.execute(total_stmt)
            total_users = total_result.scalar() or 0
            
            # Get distribution
            dist_stmt = select(
                UserSegment.segment,
                func.count(UserSegment.id).label('count')
            ).group_by(UserSegment.segment)
            
            dist_result = await session.execute(dist_stmt)
            distribution = {row.segment: row.count for row in dist_result}
            
            return {
                "total_users": total_users,
                "distribution": distribution
            }
    except Exception as e:
        logger.error(f"Failed to fetch segments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch segments")

@router.get("/events", dependencies=[Depends(verify_admin)])
async def get_events(hours: int = 24):
    """Get event statistics"""
    try:
        from sqlalchemy import select, func
        from app.database.models import AnalyticsRaw
        from app.database.db import get_async_session
        from datetime import datetime, timedelta
        
        async with get_async_session() as session:
            # Get events from last N hours
            since = datetime.utcnow() - timedelta(hours=hours)
            
            # Total events
            total_stmt = select(func.count(AnalyticsRaw.id)).where(
                AnalyticsRaw.created_at > since
            )
            total_result = await session.execute(total_stmt)
            total_events = total_result.scalar() or 0
            
            # Top events
            top_stmt = select(
                AnalyticsRaw.event_name,
                func.count(AnalyticsRaw.id).label('count')
            ).where(
                AnalyticsRaw.created_at > since
            ).group_by(AnalyticsRaw.event_name).order_by(func.count(AnalyticsRaw.id).desc())
            
            top_result = await session.execute(top_stmt)
            top_events = {row.event_name: row.count for row in top_result}
            
            return {
                "total_events": total_events,
                "top_events": top_events,
                "period_hours": hours
            }
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")

@router.get("/events/search", dependencies=[Depends(verify_admin)])
async def search_events(
    event_name: str = None,
    user_pseudo_id: str = None,
    hours: int = 24,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """
    Advanced event search with filtering, pagination, and sorting
    
    Query Parameters:
    - event_name: Filter by specific event name (optional)
    - user_pseudo_id: Filter by user ID (optional)
    - hours: Time window in hours (default: 24)
    - limit: Max results per page (default: 100, max: 1000)
    - offset: Pagination offset (default: 0)
    - sort_by: Sort field (created_at, event_name, event_timestamp)
    - sort_order: asc or desc (default: desc)
    """
    try:
        from sqlalchemy import select, desc, asc
        from app.database.models import AnalyticsRaw
        from app.database.db import get_async_session
        from datetime import datetime, timedelta
        
        # Validate inputs
        if limit > 1000:
            limit = 1000
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
        if sort_by not in ["created_at", "event_name", "event_timestamp"]:
            sort_by = "created_at"
        
        async with get_async_session() as session:
            # Build query
            since = datetime.utcnow() - timedelta(hours=hours)
            stmt = select(AnalyticsRaw).where(AnalyticsRaw.created_at > since)
            
            # Apply filters
            if event_name:
                stmt = stmt.where(AnalyticsRaw.event_name == event_name)
            if user_pseudo_id:
                stmt = stmt.where(AnalyticsRaw.user_pseudo_id == user_pseudo_id)
            
            # Apply sorting
            sort_column = getattr(AnalyticsRaw, sort_by)
            if sort_order == "desc":
                stmt = stmt.order_by(desc(sort_column))
            else:
                stmt = stmt.order_by(asc(sort_column))
            
            # Get total count (before pagination)
            from sqlalchemy import func
            count_stmt = select(func.count()).select_from(stmt.subquery())
            count_result = await session.execute(count_stmt)
            total_count = count_result.scalar() or 0
            
            # Apply pagination
            stmt = stmt.limit(limit).offset(offset)
            
            # Execute query
            result = await session.execute(stmt)
            events = result.scalars().all()
            
            # Format response
            events_data = []
            for event in events:
                events_data.append({
                    "id": event.id,
                    "event_name": event.event_name,
                    "user_pseudo_id": event.user_pseudo_id,
                    "event_params": event.event_params,
                    "event_timestamp": event.event_timestamp,
                    "created_at": event.created_at.isoformat() if event.created_at else None
                })
            
            return {
                "events": events_data,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + len(events_data)) < total_count,
                "filters": {
                    "event_name": event_name,
                    "user_pseudo_id": user_pseudo_id,
                    "hours": hours
                },
                "sort": {
                    "by": sort_by,
                    "order": sort_order
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to search events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search events: {str(e)}")

@router.get("/events/user/{user_pseudo_id}", dependencies=[Depends(verify_admin)])
async def get_user_events(user_pseudo_id: str, limit: int = 50):
    """Get all events for a specific user"""
    try:
        from sqlalchemy import select
        from app.database.models import AnalyticsRaw
        from app.database.db import get_async_session
        
        async with get_async_session() as session:
            stmt = select(AnalyticsRaw).where(
                AnalyticsRaw.user_pseudo_id == user_pseudo_id
            ).order_by(AnalyticsRaw.created_at.desc()).limit(limit)
            
            result = await session.execute(stmt)
            events = result.scalars().all()
            
            events_data = []
            for event in events:
                events_data.append({
                    "id": event.id,
                    "event_name": event.event_name,
                    "event_params": event.event_params,
                    "event_timestamp": event.event_timestamp,
                    "created_at": event.created_at.isoformat() if event.created_at else None
                })
            
            return {
                "user_pseudo_id": user_pseudo_id,
                "events": events_data,
                "total": len(events_data)
            }
            
    except Exception as e:
        logger.error(f"Failed to fetch user events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user events")

@router.get("/events/types", dependencies=[Depends(verify_admin)])
async def get_event_types():
    """Get list of all event types in database"""
    try:
        from sqlalchemy import select, distinct
        from app.database.models import AnalyticsRaw
        from app.database.db import get_async_session
        
        async with get_async_session() as session:
            stmt = select(distinct(AnalyticsRaw.event_name)).order_by(AnalyticsRaw.event_name)
            result = await session.execute(stmt)
            event_types = [row[0] for row in result.all()]
            
            return {
                "event_types": event_types,
                "total": len(event_types)
            }
            
    except Exception as e:
        logger.error(f"Failed to fetch event types: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch event types")

@router.get("/rules", dependencies=[Depends(verify_admin)])
async def get_rules():
    """Get personalization rules"""
    try:
        from sqlalchemy import select, func
        from app.database.models import PersonalizationRules
        from app.database.db import get_async_session
        
        async with get_async_session() as session:
            # Count total rules
            count_stmt = select(func.count(PersonalizationRules.id))
            count_result = await session.execute(count_stmt)
            total_rules = count_result.scalar() or 0
            
            # Get all rules
            rules_stmt = select(PersonalizationRules)
            rules_result = await session.execute(rules_stmt)
            rules = rules_result.scalars().all()
            
            rules_data = []
            for rule in rules:
                rules_data.append({
                    "segment": rule.segment,
                    "priority_sections": rule.priority_sections,
                    "featured_projects": rule.featured_projects,
                    "highlight_skills": rule.highlight_skills,
                    "reasoning": rule.reasoning,
                    "xai_explanation": rule.xai_explanation,
                    "created_at": rule.created_at.isoformat() if rule.created_at else None
                })
            
            return {
                "total_rules": total_rules,
                "rules": rules_data
            }
    except Exception as e:
        logger.error(f"Failed to fetch rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch rules")

@router.get("/insights", dependencies=[Depends(verify_admin)])
async def get_insights():
    """Get xAI insights from recent segments"""
    try:
        from sqlalchemy import select
        from app.database.models import UserSegment
        from app.database.db import get_async_session
        
        async with get_async_session() as session:
            # Get recent segments with xAI explanations
            stmt = select(UserSegment).where(
                UserSegment.xai_explanation.isnot(None)
            ).order_by(UserSegment.analyzed_at.desc()).limit(10)
            
            result = await session.execute(stmt)
            segments = result.scalars().all()
            
            insights = []
            for segment in segments:
                insights.append({
                    "segment": segment.segment,
                    "reasoning": segment.reasoning,
                    "xai_explanation": segment.xai_explanation,
                    "confidence": segment.confidence,
                    "analyzed_at": segment.analyzed_at.isoformat() if segment.analyzed_at else None
                })
            
            return {
                "insights": insights,
                "total": len(insights)
            }
    except Exception as e:
        logger.error(f"Failed to fetch insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch insights")

class RuleOverrideRequest(BaseModel):
    segment: str
    priority_sections: list[str] = []
    featured_projects: list[str] = []
    highlight_skills: list[str] = []
    css_overrides: dict = {}
    reasoning: str = ""

@router.post("/rules", dependencies=[Depends(verify_admin)])
async def create_or_update_rule(request: RuleOverrideRequest):
    """
    Create or update personalization rules for a segment
    Allows manual override of AI-generated rules
    """
    try:
        from sqlalchemy import select
        from app.database.models import PersonalizationRules
        from app.database.db import get_async_session
        from datetime import datetime
        
        async with get_async_session() as session:
            # Check if rule exists for this segment
            stmt = select(PersonalizationRules).where(
                PersonalizationRules.segment == request.segment
            )
            result = await session.execute(stmt)
            existing_rule = result.scalar_one_or_none()
            
            if existing_rule:
                # Update existing rule
                existing_rule.priority_sections = request.priority_sections
                existing_rule.featured_projects = request.featured_projects
                existing_rule.highlight_skills = request.highlight_skills
                existing_rule.css_overrides = request.css_overrides
                existing_rule.reasoning = request.reasoning or f"Manual override at {datetime.utcnow().isoformat()}"
                existing_rule.xai_explanation = {
                    "what": "Manual rule override by admin",
                    "why": "Admin intervention to customize personalization",
                    "so_what": "These rules override AI-generated suggestions",
                    "recommendation": "Monitor engagement metrics to validate manual changes"
                }
                
                logger.info(f"Updated rule for segment {request.segment}")
                action = "updated"
            else:
                # Create new rule
                new_rule = PersonalizationRules(
                    segment=request.segment,
                    priority_sections=request.priority_sections,
                    featured_projects=request.featured_projects,
                    highlight_skills=request.highlight_skills,
                    css_overrides=request.css_overrides,
                    reasoning=request.reasoning or f"Manual creation at {datetime.utcnow().isoformat()}",
                    xai_explanation={
                        "what": "Manual rule creation by admin",
                        "why": "Admin intervention to define segment personalization",
                        "so_what": "New personalization rules applied to segment",
                        "recommendation": "Monitor engagement and iterate based on data"
                    }
                )
                session.add(new_rule)
                logger.info(f"Created new rule for segment {request.segment}")
                action = "created"
            
            await session.commit()
            
            return {
                "status": "success",
                "action": action,
                "segment": request.segment,
                "message": f"Rule {action} successfully"
            }
            
    except Exception as e:
        logger.error(f"Failed to create/update rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save rule: {str(e)}")

@router.delete("/rules/{segment}", dependencies=[Depends(verify_admin)])
async def delete_rule(segment: str):
    """Delete personalization rule for a segment"""
    try:
        from sqlalchemy import select, delete
        from app.database.models import PersonalizationRules
        from app.database.db import get_async_session
        
        async with get_async_session() as session:
            # Check if rule exists
            stmt = select(PersonalizationRules).where(
                PersonalizationRules.segment == segment
            )
            result = await session.execute(stmt)
            existing_rule = result.scalar_one_or_none()
            
            if not existing_rule:
                raise HTTPException(status_code=404, detail=f"No rule found for segment {segment}")
            
            # Delete rule
            delete_stmt = delete(PersonalizationRules).where(
                PersonalizationRules.segment == segment
            )
            await session.execute(delete_stmt)
            await session.commit()
            
            logger.info(f"Deleted rule for segment {segment}")
            
            return {
                "status": "success",
                "action": "deleted",
                "segment": segment,
                "message": "Rule deleted successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {str(e)}")
