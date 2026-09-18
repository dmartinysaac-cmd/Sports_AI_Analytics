"""Team routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services import TeamService

router = APIRouter()

@router.get("/teams")
async def get_teams(db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    return await service.get_teams()
