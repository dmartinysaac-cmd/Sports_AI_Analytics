"""
Service layer - Analysis Service
Combines prediction engine with AI analysis.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from loguru import logger

from app.services.match_service import MatchService
from app.prediction.engine import PredictionEngine, PredictionInput
from app.ai.provider import get_ai_provider, AIAnalysisResult
from app.core.config import settings


class AnalysisService:
    """Orchestrates prediction generation and AI analysis."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.match_service = MatchService(db)
        self.prediction_engine = PredictionEngine()
        self.ai_provider = get_ai_provider()

    async def get_full_analysis(self, match_id: int) -> Optional[Dict[str, Any]]:
        """Get complete analysis for a match including predictions and AI interpretation."""
        match = await self.match_service.get_match(match_id)
        if not match:
            return None

        stats = await self.match_service.get_match_statistics(match_id)
        prediction = await self.match_service.get_latest_prediction(match_id)

        # Build team form (simplified - in production, calculate from historical data)
        home_form = self._build_team_form(match["home_team_id"], match["home_team_name"])
        away_form = self._build_team_form(match["away_team_id"], match["away_team_name"])
        h2h = self._build_h2h(match["home_team_id"], match["away_team_id"])

        # Generate AI analysis
        ai_data = {
            "match": {
                "home_team": match["home_team_name"],
                "away_team": match["away_team_name"],
                "competition": match["competition_name"],
                "date": str(match["match_date"]),
            },
            "team_form": {
                "local": home_form,
                "visitante": away_form,
            },
            "goals_prediction": prediction.get("goals", {}) if prediction else {},
            "corners_prediction": prediction.get("corners", {}) if prediction else {},
            "cards_prediction": prediction.get("cards", {}) if prediction else {},
            "h2h": h2h,
            "metadata": {
                "data_quality": prediction.get("data_quality", "MEDIUM") if prediction else "MEDIUM",
                "sample_size": prediction.get("sample_size", 0) if prediction else 0,
            },
        }

        if match.get("referee_name"):
            ai_data["referee"] = {
                "name": match["referee_name"],
                "avg_yellow_cards": 3.8,  # Would come from referee stats
            }

        try:
            ai_result = await self.ai_provider.analyze(ai_data)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            ai_result = None

        return {
            "match": match,
            "statistics": stats,
            "home_form": home_form,
            "away_form": away_form,
            "h2h": h2h,
            "prediction": prediction,
            "ai_analysis": self._format_ai_analysis(match_id, ai_result) if ai_result else None,
        }

    async def generate_analysis(self, match_id: int) -> Dict[str, Any]:
        """Generate new prediction and analysis for a match."""
        match = await self.match_service.get_match(match_id)
        if not match:
            raise ValueError(f"Match {match_id} not found")

        # Build prediction input
        home_form = self._build_team_form(match["home_team_id"], match["home_team_name"])
        away_form = self._build_team_form(match["away_team_id"], match["away_team_name"])
        h2h = self._build_h2h(match["home_team_id"], match["away_team_id"])

        input_data = PredictionInput(
            home_team_form=home_form,
            away_team_form=away_form,
            h2h_stats=h2h,
            referee_stats=None,
            player_stats=None,
        )

        # Run prediction engine
        prediction_result = self.prediction_engine.predict(input_data)

        logger.info(f"Generated prediction for match {match_id}")
        return prediction_result

    def _build_team_form(self, team_id: int, team_name: str) -> Dict:
        """Build team form data. In production, this queries historical matches."""
        # Simplified form - would be calculated from actual match history
        import random
        random.seed(team_id * 7)  # Deterministic for demo
        results = ["W", "D", "L"]
        form = "".join(random.choices(results, weights=[0.5, 0.3, 0.2], k=5))
        wins = form.count("W")
        draws = form.count("D")
        losses = form.count("L")

        return {
            "team_id": team_id,
            "team_name": team_name,
            "goals_avg_last_5": round(1.0 + random.random() * 1.5, 2),
            "goals_avg_last_10": round(1.2 + random.random() * 1.2, 2),
            "conceded_avg_last_5": round(0.5 + random.random() * 1.0, 2),
            "conceded_avg_last_10": round(0.7 + random.random() * 0.8, 2),
            "shots_avg": round(10 + random.random() * 8, 1),
            "corners_avg": round(4 + random.random() * 3, 1),
            "cards_avg": round(1.5 + random.random() * 1.5, 1),
            "wins": wins * 3,
            "draws": draws * 2,
            "losses": losses * 2,
            "form_last_5": form,
            "sample_size": 15 + random.randint(0, 20),
        }

    def _build_h2h(self, home_id: int, away_id: int) -> Dict:
        """Build H2H statistics. In production, queries historical matches between teams."""
        import random
        random.seed(home_id * away_id)
        total = random.randint(5, 25)
        hw = random.randint(2, total // 2)
        dr = random.randint(1, total // 3)
        aw = total - hw - dr

        return {
            "total_matches": total,
            "home_wins": hw,
            "draws": dr,
            "away_wins": max(0, aw),
            "avg_goals": round(2.0 + random.random() * 1.5, 2),
            "avg_corners": round(8 + random.random() * 3, 1),
            "avg_cards": round(3 + random.random() * 2, 1),
            "last_5_results": [f"H {random.randint(0,3)}-{random.randint(0,2)} A" for _ in range(5)],
        }

    def _format_ai_analysis(self, match_id: int, result: AIAnalysisResult) -> Dict:
        """Format AI analysis result for API response."""
        from datetime import datetime
        return {
            "match_id": match_id,
            "interpretation": result.interpretation,
            "key_factors": result.key_factors,
            "risks": result.risks,
            "confidence_level": result.confidence_level,
            "data_notes": result.data_notes,
            "generated_at": datetime.utcnow().isoformat(),
            "model_used": result.model_used,
        }
