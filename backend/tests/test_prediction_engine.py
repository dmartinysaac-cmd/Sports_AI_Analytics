"""
Tests for the Prediction Engine.
Mathematical tests with controlled data to verify model correctness.
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.prediction.engine import (
    PredictionEngine, GoalPredictionModel, CornerPredictionModel,
    CardPredictionModel, PlayerShotsPredictionModel, PredictionInput
)


class TestGoalPredictionModel:
    """Tests for the Poisson-based goal prediction model."""

    def setup_method(self):
        self.model = GoalPredictionModel()

    def test_expected_goals_are_positive(self):
        """Expected goals must always be positive."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.3, "sample_size": 20},
            h2h_stats={"total_matches": 10, "avg_goals": 2.5},
        )
        result = self.model.predict(input_data)
        assert result.expected_home_goals > 0
        assert result.expected_away_goals > 0
        assert result.expected_total_goals > 0

    def test_total_equals_sum(self):
        """Total expected goals must equal home + away."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 2.0, "conceded_avg_last_5": 0.8, "sample_size": 15},
            away_team_form={"goals_avg_last_5": 1.0, "conceded_avg_last_5": 1.5, "sample_size": 15},
            h2h_stats={"total_matches": 5, "avg_goals": 2.8},
        )
        result = self.model.predict(input_data)
        assert abs(result.expected_total_goals - (result.expected_home_goals + result.expected_away_goals)) < 0.01

    def test_probabilities_sum_to_one(self):
        """1X2 probabilities must sum to approximately 1."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.3, "sample_size": 20},
            h2h_stats={"total_matches": 10, "avg_goals": 2.5},
        )
        result = self.model.predict(input_data)
        total = result.probabilities["home_win"] + result.probabilities["draw"] + result.probabilities["away_win"]
        assert abs(total - 1.0) < 0.05  # Allow small floating point error

    def test_over_under_complementary(self):
        """Over and under probabilities must be complementary."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.3, "sample_size": 20},
            h2h_stats={"total_matches": 10, "avg_goals": 2.5},
        )
        result = self.model.predict(input_data)
        assert abs(result.probabilities["over_25"] + result.probabilities["under_25"] - 1.0) < 0.01
        assert abs(result.probabilities["over_15"] + result.probabilities["under_15"] - 1.0) < 0.01

    def test_btts_complementary(self):
        """BTTS yes/no must sum to 1."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.3, "sample_size": 20},
            h2h_stats={"total_matches": 10, "avg_goals": 2.5},
        )
        result = self.model.predict(input_data)
        assert abs(result.probabilities["btts_yes"] + result.probabilities["btts_no"] - 1.0) < 0.01

    def test_distribution_sums_to_one(self):
        """Goal distribution must sum to approximately 1."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.3, "sample_size": 20},
            h2h_stats={"total_matches": 10, "avg_goals": 2.5},
        )
        result = self.model.predict(input_data)
        total = sum(result.distribution.values())
        assert abs(total - 1.0) < 0.05

    def test_home_advantage(self):
        """Home team should have advantage when form is equal."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            h2h_stats={"total_matches": 0},
        )
        result = self.model.predict(input_data)
        assert result.expected_home_goals > result.expected_away_goals

    def test_strong_team_scores_higher(self):
        """A stronger team should have higher expected goals."""
        strong_input = PredictionInput(
            home_team_form={"goals_avg_last_5": 2.5, "conceded_avg_last_5": 0.5, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 0.8, "conceded_avg_last_5": 2.0, "sample_size": 20},
            h2h_stats={"total_matches": 0},
        )
        weak_input = PredictionInput(
            home_team_form={"goals_avg_last_5": 0.8, "conceded_avg_last_5": 2.0, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 2.5, "conceded_avg_last_5": 0.5, "sample_size": 20},
            h2h_stats={"total_matches": 0},
        )
        strong_result = self.model.predict(strong_input)
        weak_result = self.model.predict(weak_input)
        assert strong_result.expected_home_goals > weak_result.expected_home_goals


class TestCornerPredictionModel:
    """Tests for corner prediction model."""

    def setup_method(self):
        self.model = CornerPredictionModel()

    def test_corners_are_positive(self):
        input_data = PredictionInput(
            home_team_form={"corners_avg": 5.5, "goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"corners_avg": 4.0, "goals_avg_last_5": 1.0, "conceded_avg_last_5": 1.5, "sample_size": 20},
            h2h_stats={},
        )
        result = self.model.predict(input_data)
        assert result.expected_home_corners > 0
        assert result.expected_away_corners > 0
        assert result.expected_total_corners > 0

    def test_probabilities_are_valid(self):
        input_data = PredictionInput(
            home_team_form={"corners_avg": 5.5, "goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"corners_avg": 4.0, "goals_avg_last_5": 1.0, "conceded_avg_last_5": 1.5, "sample_size": 20},
            h2h_stats={},
        )
        result = self.model.predict(input_data)
        for key, value in result.probabilities.items():
            assert 0 <= value <= 1, f"Probability {key}={value} out of range"


class TestCardPredictionModel:
    """Tests for card prediction model."""

    def setup_method(self):
        self.model = CardPredictionModel()

    def test_cards_are_positive(self):
        input_data = PredictionInput(
            home_team_form={"cards_avg": 2.0, "goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"cards_avg": 2.5, "goals_avg_last_5": 1.0, "conceded_avg_last_5": 1.5, "sample_size": 20},
            h2h_stats={},
            referee_stats={"avg_yellow_cards": 4.0},
        )
        result = self.model.predict(input_data)
        assert result.expected_home_cards > 0
        assert result.expected_away_cards > 0

    def test_referee_increases_cards(self):
        """A stricter referee should increase expected cards."""
        lenient = PredictionInput(
            home_team_form={"cards_avg": 2.0, "goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"cards_avg": 2.0, "goals_avg_last_5": 1.0, "conceded_avg_last_5": 1.5, "sample_size": 20},
            h2h_stats={},
            referee_stats={"avg_yellow_cards": 2.5},
        )
        strict = PredictionInput(
            home_team_form={"cards_avg": 2.0, "goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "sample_size": 20},
            away_team_form={"cards_avg": 2.0, "goals_avg_last_5": 1.0, "conceded_avg_last_5": 1.5, "sample_size": 20},
            h2h_stats={},
            referee_stats={"avg_yellow_cards": 5.5},
        )
        lenient_result = self.model.predict(lenient)
        strict_result = self.model.predict(strict)
        assert strict_result.expected_total_cards > lenient_result.expected_total_cards


class TestPlayerShotsPredictionModel:
    """Tests for player shots prediction model."""

    def setup_method(self):
        self.model = PlayerShotsPredictionModel()

    def test_insufficient_data(self):
        """Should return INSUFFICIENT_DATA when sample is too small."""
        result = self.model.predict({
            "player_id": 1, "player_name": "Test Player",
            "shots_avg": 3.0, "shots_on_target_avg": 1.5,
            "sample_size": 2, "minutes": 200, "expected_minutes": 75,
        })
        assert result.status == "INSUFFICIENT_DATA"
        assert result.expected_shots == 0.0

    def test_sufficient_data(self):
        """Should return valid prediction with enough data."""
        result = self.model.predict({
            "player_id": 1, "player_name": "Test Player",
            "shots_avg": 3.5, "shots_on_target_avg": 1.5,
            "sample_size": 10, "minutes": 800, "expected_minutes": 80,
        })
        assert result.status == "OK"
        assert result.expected_shots > 0
        assert result.expected_shots_on_target > 0

    def test_minute_adjustment(self):
        """Fewer expected minutes should reduce expected shots."""
        full = self.model.predict({
            "player_id": 1, "player_name": "Test",
            "shots_avg": 4.0, "shots_on_target_avg": 2.0,
            "sample_size": 10, "expected_minutes": 90,
        })
        partial = self.model.predict({
            "player_id": 1, "player_name": "Test",
            "shots_avg": 4.0, "shots_on_target_avg": 2.0,
            "sample_size": 10, "expected_minutes": 45,
        })
        assert full.expected_shots > partial.expected_shots


class TestPredictionEngine:
    """Integration tests for the full prediction engine."""

    def setup_method(self):
        self.engine = PredictionEngine()

    def test_full_prediction(self):
        """Test complete prediction pipeline."""
        input_data = PredictionInput(
            home_team_form={"goals_avg_last_5": 2.0, "conceded_avg_last_5": 0.8, "corners_avg": 5.5, "cards_avg": 1.8, "sample_size": 20},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.5, "corners_avg": 4.0, "cards_avg": 2.2, "sample_size": 20},
            h2h_stats={"total_matches": 10, "avg_goals": 2.5},
            referee_stats={"avg_yellow_cards": 4.0},
            player_stats=[
                {"player_id": 1, "player_name": "Striker", "shots_avg": 3.5, "shots_on_target_avg": 1.5, "sample_size": 15, "expected_minutes": 80},
            ],
        )
        result = self.engine.predict(input_data)

        assert "goals" in result
        assert "corners" in result
        assert "cards" in result
        assert "players" in result
        assert "metadata" in result

        assert result["goals"]["expected_home_goals"] > 0
        assert result["corners"]["expected_total_corners"] > 0
        assert result["cards"]["expected_total_cards"] > 0
        assert len(result["players"]) == 1
        assert result["metadata"]["data_quality"] == "HIGH"

    def test_data_quality_levels(self):
        """Test data quality classification."""
        # HIGH quality
        high_input = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "corners_avg": 5, "cards_avg": 2, "sample_size": 25},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.3, "corners_avg": 4, "cards_avg": 2, "sample_size": 25},
            h2h_stats={},
        )
        result = self.engine.predict(high_input)
        assert result["metadata"]["data_quality"] == "HIGH"

        # LOW quality
        low_input = PredictionInput(
            home_team_form={"goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.0, "corners_avg": 5, "cards_avg": 2, "sample_size": 7},
            away_team_form={"goals_avg_last_5": 1.2, "conceded_avg_last_5": 1.3, "corners_avg": 4, "cards_avg": 2, "sample_size": 7},
            h2h_stats={},
        )
        result = self.engine.predict(low_input)
        assert result["metadata"]["data_quality"] == "LOW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
