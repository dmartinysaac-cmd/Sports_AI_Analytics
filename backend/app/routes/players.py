"""Player routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.services import PlayerService

router = APIRouter()

@router.get("/players")
async def get_players(position: Optional[str] = None, team_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    service = PlayerService(db)
    return await service.get_players(position=position, team_id=team_id)

@router.get("/players/{player_id}")
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    service = PlayerService(db)
    player = await service.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
