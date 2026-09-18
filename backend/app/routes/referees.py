"""Referee routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services import RefereeService

router = APIRouter()

@router.get("/referees")
async def get_referees(db: AsyncSession = Depends(get_db)):
    service = RefereeService(db)
    return await service.get_referees()

@router.get("/referees/{referee_id}")
async def get_referee(referee_id: int, db: AsyncSession = Depends(get_db)):
    service = RefereeService(db)
    referee = await service.get_referee(referee_id)
    if not referee:
        raise HTTPException(status_code=404, detail="Referee not found")
    return referee
