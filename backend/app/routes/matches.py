"""Match routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.services.match_service import MatchService

router = APIRouter()

@router.get("/matches")
async def get_matches(
    status: Optional[str] = None,
    competition_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    service = MatchService(db)
    return await service.get_matches(status=status, competition_id=competition_id, limit=limit, offset=offset)

@router.get("/matches/{match_id}")
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    service = MatchService(db)
    match = await service.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.get("/matches/{match_id}/statistics")
async def get_match_statistics(match_id: int, db: AsyncSession = Depends(get_db)):
    service = MatchService(db)
    stats = await service.get_match_statistics(match_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Statistics not found")
    return stats

@router.get("/matches/{match_id}/predictions")
async def get_match_predictions(match_id: int, db: AsyncSession = Depends(get_db)):
    service = MatchService(db)
    prediction = await service.get_latest_prediction(match_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="No predictions available")
    return prediction
