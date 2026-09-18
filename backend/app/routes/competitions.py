"""Competition routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services import CompetitionService

router = APIRouter()

@router.get("/competitions")
async def get_competitions(db: AsyncSession = Depends(get_db)):
    service = CompetitionService(db)
    return await service.get_competitions()
