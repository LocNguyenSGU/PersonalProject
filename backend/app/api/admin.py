from fastapi import APIRouter

# Admin routes (will be populated in Phase 2)
router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/trigger-analysis")
async def trigger_analysis():
    """Manually trigger analysis job (dev only)"""
    # TODO: Implement in Phase 2
    return {"status": "triggered"}
