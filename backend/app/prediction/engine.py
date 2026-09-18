"""
Prediction Engine - Core statistical models for goals, corners, cards, and player shots.
Uses Poisson distribution as the base model with extensible architecture.
"""
import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class PredictionInput:
    """Input data for prediction models."""
    home_team_form: Dict
    away_team_form: Dict
    h2h_stats: Dict
    referee_stats: Optional[Dict] = None
    player_stats: Optional[List[Dict]] = None
    venue: str = "home"


@dataclass
class GoalPredictionResult:
    expected_home_goals: float
    expected_away_goals: float
    expected_total_goals: float
    distribution: Dict[str, float]
    probabilities: Dict[str, float]


@dataclass
class CornerPredictionResult:
    expected_home_corners: float
    expected_away_corners: float
    expected_total_corners: float
    probabilities: Dict[str, float]


@dataclass
class CardPredictionResult:
    expected_home_cards: float
    expected_away_cards: float
    expected_total_cards: float
    probabilities: Dict[str, float]


@dataclass
class PlayerShotResult:
    player_id: int
    player_name: str
    expected_shots: float
    expected_shots_on_target: float
    probabilities: Dict[str, float]
    status: str = "OK"


class GoalPredictionModel:
    """
    Poisson-based goal prediction model.
    Calculates expected goals using team form, H2H, and home/away factors.
    """

    def __init__(self):
        self.home_advantage = 1.15  # Historical home advantage factor

    def predict(self, input_data: PredictionInput) -> GoalPredictionResult:
        """Generate goal prediction using Poisson model."""
        home_form = input_data.home_team_form
        away_form = input_data.away_team_form
        h2h = input_data.h2h_stats

        # Calculate expected goals based on attack/defense strength
        home_attack = home_form.get("goals_avg_last_5", 1.3)
        home_defense = home_form.get("conceded_avg_last_5", 1.0)
        away_attack = away_form.get("goals_avg_last_5", 1.1)
        away_defense = away_form.get("conceded_avg_last_5", 1.2)

        # League average (approximate)
        league_avg = 1.35

        # Expected goals calculation
        home_strength = (home_attack / league_avg) * (away_defense / league_avg) * self.home_advantage
        away_strength = (away_attack / league_avg) * (home_defense / league_avg) / self.home_advantage

        # Adjust with H2H if sufficient data
        if h2h.get("total_matches", 0) >= 5:
            h2h_factor = h2h.get("avg_goals", 2.5) / 2.5
            home_strength *= (0.7 + 0.3 * h2h_factor)
            away_strength *= (0.7 + 0.3 * h2h_factor)

        expected_home = max(0.3, min(4.0, home_strength * league_avg))
        expected_away = max(0.2, min(3.5, away_strength * league_avg))
        expected_total = expected_home + expected_away

        # Generate distribution using Poisson
        distribution = self._poisson_distribution(expected_total, max_goals=6)

        # Calculate probabilities
        probabilities = self._calculate_probabilities(expected_home, expected_away)

        logger.info(f"Goal prediction: Home={expected_home:.2f}, Away={expected_away:.2f}, Total={expected_total:.2f}")

        return GoalPredictionResult(
            expected_home_goals=round(expected_home, 2),
            expected_away_goals=round(expected_away, 2),
            expected_total_goals=round(expected_total, 2),
            distribution=distribution,
            probabilities=probabilities,
        )

    def _poisson_distribution(self, lam: float, max_goals: int = 6) -> Dict[str, float]:
        """Calculate Poisson probability distribution."""
        dist = {}
        cumulative = 0.0
        for i in range(max_goals):
            prob = stats.poisson.pmf(i, lam)
            dist[str(i)] = round(prob, 3)
            cumulative += prob
        dist["5+"] = round(1.0 - cumulative, 3)
        return dist

    def _calculate_probabilities(self, home_lambda: float, away_lambda: float) -> Dict[str, float]:
        """Calculate over/under, BTTS, and 1X2 probabilities."""
        total_lambda = home_lambda + away_lambda

        # Over/Under goals
        over_05 = 1 - stats.poisson.cdf(0, total_lambda)
        over_15 = 1 - stats.poisson.cdf(1, total_lambda)
        over_25 = 1 - stats.poisson.cdf(2, total_lambda)
        over_35 = 1 - stats.poisson.cdf(3, total_lambda)

        # BTTS calculation using bivariate Poisson approximation
        btts_yes = (1 - stats.poisson.cdf(0, home_lambda)) * (1 - stats.poisson.cdf(0, away_lambda))
        # Adjust for correlation
        btts_yes = min(0.95, btts_yes * 1.1)

        # 1X2 probabilities using Skellam distribution approximation
        diff_lambda = home_lambda - away_lambda
        # P(home win) = P(X > Y) where X~Pois(home), Y~Pois(away)
        home_win = 0.0
        draw = 0.0
        for i in range(8):
            for j in range(8):
                p = stats.poisson.pmf(i, home_lambda) * stats.poisson.pmf(j, away_lambda)
                if i > j:
                    home_win += p
                elif i == j:
                    draw += p

        away_win = 1.0 - home_win - draw

        return {
            "over_05": round(min(0.99, over_05), 3),
            "over_15": round(min(0.99, over_15), 3),
            "over_25": round(min(0.99, over_25), 3),
            "over_35": round(min(0.99, over_35), 3),
            "under_05": round(max(0.01, 1 - over_05), 3),
            "under_15": round(max(0.01, 1 - over_15), 3),
            "under_25": round(max(0.01, 1 - over_25), 3),
            "under_35": round(max(0.01, 1 - over_35), 3),
            "btts_yes": round(btts_yes, 3),
            "btts_no": round(1 - btts_yes, 3),
            "home_win": round(home_win, 3),
            "draw": round(draw, 3),
            "away_win": round(max(0.01, away_win), 3),
        }


class CornerPredictionModel:
    """Corner prediction model based on team corner statistics."""

    def predict(self, input_data: PredictionInput) -> CornerPredictionResult:
        home_form = input_data.home_form if hasattr(input_data, 'home_form') else input_data.home_team_form
        away_form = input_data.away_form if hasattr(input_data, 'away_form') else input_data.away_team_form

        home_corners_for = home_form.get("corners_avg", 5.2)
        away_corners_for = away_form.get("corners_avg", 4.1)

        # Home advantage for corners
        expected_home = home_corners_for * 1.08
        expected_away = away_corners_for * 0.95
        expected_total = expected_home + expected_away

        # Probabilities using Poisson
        total_lambda = expected_total
        probs = {
            "over_75": round(1 - stats.poisson.cdf(7, total_lambda), 3),
            "over_85": round(1 - stats.poisson.cdf(8, total_lambda), 3),
            "over_95": round(1 - stats.poisson.cdf(9, total_lambda), 3),
            "over_105": round(1 - stats.poisson.cdf(10, total_lambda), 3),
            "over_115": round(1 - stats.poisson.cdf(11, total_lambda), 3),
        }

        return CornerPredictionResult(
            expected_home_corners=round(expected_home, 1),
            expected_away_corners=round(expected_away, 1),
            expected_total_corners=round(expected_total, 1),
            probabilities=probs,
        )


class CardPredictionModel:
    """Card prediction model incorporating referee statistics."""

    def predict(self, input_data: PredictionInput) -> CardPredictionResult:
        home_form = input_data.home_team_form
        away_form = input_data.away_team_form
        referee = input_data.referee_stats or {}

        # Base card rates from team data
        home_cards_avg = home_form.get("cards_avg", 1.8)
        away_cards_avg = away_form.get("cards_avg", 2.1)

        # Referee adjustment
        ref_avg_cards = referee.get("avg_yellow_cards", 3.8)
        league_avg_cards = 3.8
        ref_factor = ref_avg_cards / league_avg_cards

        expected_home = home_cards_avg * ref_factor * 1.0
        expected_away = away_cards_avg * ref_factor * 1.05
        expected_total = expected_home + expected_away

        total_lambda = expected_total
        probs = {
            "over_25": round(1 - stats.poisson.cdf(2, total_lambda), 3),
            "over_35": round(1 - stats.poisson.cdf(3, total_lambda), 3),
            "over_45": round(1 - stats.poisson.cdf(4, total_lambda), 3),
            "over_55": round(1 - stats.poisson.cdf(5, total_lambda), 3),
        }

        return CardPredictionResult(
            expected_home_cards=round(expected_home, 1),
            expected_away_cards=round(expected_away, 1),
            expected_total_cards=round(expected_total, 1),
            probabilities=probs,
        )


class PlayerShotsPredictionModel:
    """Player shots prediction model."""

    MIN_SAMPLE_SIZE = 5  # Minimum matches to make prediction

    def predict(self, player_data: Dict) -> PlayerShotResult:
        """Predict shots for a single player."""
        minutes = player_data.get("minutes", 0)
        shots_avg = player_data.get("shots_avg", 0)
        sot_avg = player_data.get("shots_on_target_avg", 0)
        sample_size = player_data.get("sample_size", 0)

        if sample_size < self.MIN_SAMPLE_SIZE or shots_avg == 0:
            return PlayerShotResult(
                player_id=player_data.get("player_id", 0),
                player_name=player_data.get("player_name", "Unknown"),
                expected_shots=0.0,
                expected_shots_on_target=0.0,
                probabilities={"over_05": 0, "over_15": 0, "over_25": 0, "over_35": 0},
                status="INSUFFICIENT_DATA",
            )

        # Adjust for expected minutes
        expected_minutes = player_data.get("expected_minutes", 75)
        minute_factor = expected_minutes / 90.0

        expected_shots = shots_avg * minute_factor
        expected_sot = sot_avg * minute_factor

        # Poisson probabilities
        probs = {
            "over_05": round(1 - stats.poisson.cdf(0, expected_shots), 3),
            "over_15": round(1 - stats.poisson.cdf(1, expected_shots), 3),
            "over_25": round(1 - stats.poisson.cdf(2, expected_shots), 3),
            "over_35": round(1 - stats.poisson.cdf(3, expected_shots), 3),
        }

        return PlayerShotResult(
            player_id=player_data.get("player_id", 0),
            player_name=player_data.get("player_name", "Unknown"),
            expected_shots=round(expected_shots, 1),
            expected_shots_on_target=round(expected_sot, 1),
            probabilities=probs,
            status="OK",
        )


class PredictionEngine:
    """
    Main prediction engine that combines all models.
    Generates comprehensive predictions for a match.
    """

    def __init__(self):
        self.goal_model = GoalPredictionModel()
        self.corner_model = CornerPredictionModel()
        self.card_model = CardPredictionModel()
        self.player_model = PlayerShotsPredictionModel()

    def predict(self, input_data: PredictionInput) -> Dict:
        """Generate complete prediction for a match."""
        logger.info(f"Running prediction engine for match")

        goals = self.goal_model.predict(input_data)
        corners = self.corner_model.predict(input_data)
        cards = self.card_model.predict(input_data)

        # Player predictions
        player_predictions = []
        if input_data.player_stats:
            for player in input_data.player_stats:
                result = self.player_model.predict(player)
                player_predictions.append({
                    "player_id": result.player_id,
                    "player_name": result.player_name,
                    "expected_shots": result.expected_shots,
                    "expected_shots_on_target": result.expected_shots_on_target,
                    "probabilities": result.probabilities,
                    "status": result.status,
                })

        # Determine data quality
        sample_size = input_data.home_team_form.get("sample_size", 0)
        if sample_size >= 20:
            data_quality = "HIGH"
        elif sample_size >= 10:
            data_quality = "MEDIUM"
        elif sample_size >= 5:
            data_quality = "LOW"
        else:
            data_quality = "INSUFFICIENT"

        result = {
            "goals": {
                "expected_home_goals": goals.expected_home_goals,
                "expected_away_goals": goals.expected_away_goals,
                "expected_total_goals": goals.expected_total_goals,
                "distribution": goals.distribution,
                "probabilities": goals.probabilities,
            },
            "corners": {
                "expected_home_corners": corners.expected_home_corners,
                "expected_away_corners": corners.expected_away_corners,
                "expected_total_corners": corners.expected_total_corners,
                "probabilities": corners.probabilities,
            },
            "cards": {
                "expected_home_cards": cards.expected_home_cards,
                "expected_away_cards": cards.expected_away_cards,
                "expected_total_cards": cards.expected_total_cards,
                "probabilities": cards.probabilities,
            },
            "players": player_predictions,
            "metadata": {
                "data_quality": data_quality,
                "sample_size": sample_size,
            },
        }

        logger.info(f"Prediction complete. Quality: {data_quality}, Sample: {sample_size}")
        return result
