"""Service layer stubs for remaining services."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Team, Player, Referee, Competition, Match, TeamAlias


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_teams(self):
        result = await self.db.execute(select(Team).order_by(Team.name))
        teams = result.scalars().all()
        response = []
        for t in teams:
            aliases_result = await self.db.execute(
                select(TeamAlias).where(TeamAlias.team_id == t.id)
            )
            aliases = [a.alias for a in aliases_result.scalars().all()]
            response.append({
                "id": t.id, "name": t.name, "short_name": t.short_name,
                "country": t.country, "founded": t.founded, "stadium": t.stadium,
                "logo_url": t.logo_url, "aliases": aliases,
            })
        return response


class PlayerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_players(self, position=None, team_id=None):
        query = select(Player)
        if position:
            query = query.where(Player.position == position)
        if team_id:
            query = query.where(Player.team_id == team_id)
        result = await self.db.execute(query.order_by(Player.name))
        players = result.scalars().all()
        response = []
        for p in players:
            team = await self.db.get(Team, p.team_id) if p.team_id else None
            response.append({
                "id": p.id, "name": p.name, "team_id": p.team_id,
                "team_name": team.name if team else None,
                "position": p.position, "number": p.number,
                "nationality": p.nationality, "age": p.age,
            })
        return response

    async def get_player(self, player_id: int):
        player = await self.db.get(Player, player_id)
        if not player:
            return None
        team = await self.db.get(Team, player.team_id) if player.team_id else None
        return {
            "id": player.id, "name": player.name, "team_id": player.team_id,
            "team_name": team.name if team else None,
            "position": player.position, "number": player.number,
            "nationality": player.nationality, "age": player.age,
        }


class RefereeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_referees(self):
        result = await self.db.execute(select(Referee).order_by(Referee.name))
        referees = result.scalars().all()
        return [{
            "id": r.id, "name": r.name, "nationality": r.nationality,
            "matches_total": 0, "avg_yellow_cards": 0.0,
            "avg_red_cards": 0.0, "avg_fouls": 0.0,
        } for r in referees]

    async def get_referee(self, referee_id: int):
        ref = await self.db.get(Referee, referee_id)
        if not ref:
            return None
        return {
            "id": ref.id, "name": ref.name, "nationality": ref.nationality,
            "matches_total": 0, "avg_yellow_cards": 0.0,
            "avg_red_cards": 0.0, "avg_fouls": 0.0,
        }


class CompetitionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_competitions(self):
        result = await self.db.execute(select(Competition).order_by(Competition.name))
        comps = result.scalars().all()
        return [{
            "id": c.id, "name": c.name, "country": c.country,
            "tier": c.tier, "external_ids": c.external_ids or {},
        } for c in comps]


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.match_service = None  # Lazy init

    async def get_dashboard(self):
        from app.services.match_service import MatchService
        ms = MatchService(self.db)

        upcoming = await ms.get_matches(status="scheduled", limit=5)
        recent = await ms.get_matches(status="finished", limit=5)

        teams_count = (await self.db.execute(select(Team))).scalars().all()
        players_count = (await self.db.execute(select(Player))).scalars().all()
        refs_count = (await self.db.execute(select(Referee))).scalars().all()
        comps_count = (await self.db.execute(select(Competition))).scalars().all()

        from datetime import datetime
        return {
            "upcoming_matches": upcoming,
            "recent_matches": recent,
            "total_competitions": len(comps_count),
            "total_teams": len(teams_count),
            "total_players": len(players_count),
            "total_referees": len(refs_count),
            "last_updated": datetime.utcnow().isoformat(),
        }
