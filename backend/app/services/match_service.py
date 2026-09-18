"""
Service layer - Match Service
Handles match-related business logic.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from app.models.models import Match, MatchStatistics, Prediction, Team, Competition, Season, Referee, Venue
from loguru import logger


class MatchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_matches(
        self,
        status: Optional[str] = None,
        competition_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """Get matches with optional filters."""
        query = select(Match).join(Team, Match.home_team_id == Team.id)
        query = query.join(Competition, Match.competition_id == Competition.id)

        if status:
            query = query.where(Match.status == status)
        if competition_id:
            query = query.where(Match.competition_id == competition_id)

        query = query.order_by(Match.match_date.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        matches = result.scalars().all()

        # Build response with related data
        response = []
        for m in matches:
            home_team = await self.db.get(Team, m.home_team_id)
            away_team = await self.db.get(Team, m.away_team_id)
            comp = await self.db.get(Competition, m.competition_id)
            ref = await self.db.get(Referee, m.referee_id) if m.referee_id else None
            venue = await self.db.get(Venue, m.venue_id) if m.venue_id else None

            response.append({
                "id": m.id,
                "competition_id": m.competition_id,
                "competition_name": comp.name if comp else "Unknown",
                "season_id": m.season_id,
                "season_name": None,
                "match_date": m.match_date,
                "home_team_id": m.home_team_id,
                "home_team_name": home_team.name if home_team else "Unknown",
                "away_team_id": m.away_team_id,
                "away_team_name": away_team.name if away_team else "Unknown",
                "referee_id": m.referee_id,
                "referee_name": ref.name if ref else None,
                "venue_id": m.venue_id,
                "venue_name": venue.name if venue else None,
                "status": m.status,
                "home_score": m.home_score,
                "away_score": m.away_score,
                "external_id": m.external_id,
                "source": m.source,
            })
        return response

    async def get_match(self, match_id: int) -> Optional[dict]:
        """Get a single match by ID."""
        match = await self.db.get(Match, match_id)
        if not match:
            return None

        home_team = await self.db.get(Team, match.home_team_id)
        away_team = await self.db.get(Team, match.away_team_id)
        comp = await self.db.get(Competition, match.competition_id)
        ref = await self.db.get(Referee, match.referee_id) if match.referee_id else None
        venue = await self.db.get(Venue, match.venue_id) if match.venue_id else None

        return {
            "id": match.id,
            "competition_id": match.competition_id,
            "competition_name": comp.name if comp else "Unknown",
            "season_id": match.season_id,
            "season_name": None,
            "match_date": match.match_date,
            "home_team_id": match.home_team_id,
            "home_team_name": home_team.name if home_team else "Unknown",
            "away_team_id": match.away_team_id,
            "away_team_name": away_team.name if away_team else "Unknown",
            "referee_id": match.referee_id,
            "referee_name": ref.name if ref else None,
            "venue_id": match.venue_id,
            "venue_name": venue.name if venue else None,
            "status": match.status,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "external_id": match.external_id,
            "source": match.source,
        }

    async def get_match_statistics(self, match_id: int) -> Optional[dict]:
        """Get statistics for a match."""
        query = select(MatchStatistics).where(MatchStatistics.match_id == match_id)
        result = await self.db.execute(query)
        stats = result.scalar_one_or_none()
        if not stats:
            return None
        return {
            "match_id": stats.match_id,
            "home_shots": stats.home_shots,
            "away_shots": stats.away_shots,
            "home_shots_on_target": stats.home_shots_on_target,
            "away_shots_on_target": stats.away_shots_on_target,
            "home_possession": stats.home_possession,
            "away_possession": stats.away_possession,
            "home_corners": stats.home_corners,
            "away_corners": stats.away_corners,
            "home_fouls": stats.home_fouls,
            "away_fouls": stats.away_fouls,
            "home_yellow_cards": stats.home_yellow_cards,
            "away_yellow_cards": stats.away_yellow_cards,
            "home_red_cards": stats.home_red_cards,
            "away_red_cards": stats.away_red_cards,
            "home_xg": stats.home_xg,
            "away_xg": stats.away_xg,
        }

    async def get_latest_prediction(self, match_id: int) -> Optional[dict]:
        """Get the latest prediction for a match."""
        query = (
            select(Prediction)
            .where(Prediction.match_id == match_id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        pred = result.scalar_one_or_none()
        if not pred:
            return None
        return {
            "id": pred.id,
            "match_id": pred.match_id,
            "model_name": pred.model_name,
            "model_version": pred.model_version,
            "feature_version": pred.feature_version,
            "goals": pred.outputs.get("goals", {}),
            "corners": pred.outputs.get("corners", {}),
            "cards": pred.outputs.get("cards", {}),
            "players": pred.outputs.get("players", []),
            "created_at": pred.created_at,
            "data_quality": pred.data_quality,
            "sample_size": pred.sample_size or 0,
        }
