"""Analysis routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.analysis_service import AnalysisService

router = APIRouter()

@router.get("/matches/{match_id}/analysis")
async def get_match_analysis(match_id: int, db: AsyncSession = Depends(get_db)):
    service = AnalysisService(db)
    result = await service.get_full_analysis(match_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result

@router.post("/analysis/{match_id}/generate")
async def generate_analysis(match_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger prediction and AI analysis generation for a match."""
    service = AnalysisService(db)
    result = await service.generate_analysis(match_id)
    return {"status": "success", "match_id": match_id, "analysis": result}
