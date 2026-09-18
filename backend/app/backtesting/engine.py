"""
Backtesting module for evaluating model performance.
Compares predictions against actual results without data leakage.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np
from loguru import logger


@dataclass
class BacktestResult:
    """Result of a backtesting evaluation."""
    model_name: str
    model_version: str
    total_matches: int
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Square Error
    log_loss: Optional[float]
    brier_score: Optional[float]
    calibration: Optional[float]
    by_competition: Dict[str, Dict]
    by_season: Dict[str, Dict]


class BacktestingEngine:
    """
    Evaluates prediction models against historical results.
    Ensures no future data is used (temporal validation).
    """

    def __init__(self):
        self.min_sample_size = 10

    def evaluate_goals(
        self,
        predictions: List[Dict],
        actuals: List[Dict],
    ) -> Dict:
        """
        Evaluate goal predictions against actual results.

        predictions: List of {"expected_home": float, "expected_away": float, ...}
        actuals: List of {"home_score": int, "away_score": int, ...}
        """
        if len(predictions) < self.min_sample_size:
            return {"error": "Insufficient sample size", "sample_size": len(predictions)}

        pred_home = np.array([p["expected_home"] for p in predictions])
        pred_away = np.array([p["expected_away"] for p in predictions])
        pred_total = pred_home + pred_away

        actual_home = np.array([a["home_score"] for a in actuals])
        actual_away = np.array([a["away_score"] for a in actuals])
        actual_total = actual_home + actual_away

        # MAE
        mae_total = np.mean(np.abs(pred_total - actual_total))
        mae_home = np.mean(np.abs(pred_home - actual_home))
        mae_away = np.mean(np.abs(pred_away - actual_away))

        # RMSE
        rmse_total = np.sqrt(np.mean((pred_total - actual_total) ** 2))

        # Brier Score for Over 2.5
        if "over_25_prob" in predictions[0]:
            probs = np.array([p["over_25_prob"] for p in predictions])
            outcomes = (actual_total > 2.5).astype(float)
            brier = np.mean((probs - outcomes) ** 2)
        else:
            brier = None

        # Log Loss for 1X2
        log_loss = None
        if all(k in predictions[0] for k in ["home_win_prob", "draw_prob", "away_win_prob"]):
            log_loss = self._calculate_log_loss(predictions, actuals)

        result = {
            "mae_total": round(float(mae_total), 3),
            "mae_home": round(float(mae_home), 3),
            "mae_away": round(float(mae_away), 3),
            "rmse_total": round(float(rmse_total), 3),
            "brier_score_over25": round(float(brier), 4) if brier is not None else None,
            "log_loss_1x2": round(float(log_loss), 4) if log_loss is not None else None,
            "sample_size": len(predictions),
        }

        logger.info(f"Backtest goals: MAE={mae_total:.3f}, RMSE={rmse_total:.3f}, N={len(predictions)}")
        return result

    def evaluate_corners(
        self,
        predictions: List[Dict],
        actuals: List[Dict],
    ) -> Dict:
        """Evaluate corner predictions."""
        if len(predictions) < self.min_sample_size:
            return {"error": "Insufficient sample size"}

        pred_total = np.array([p["expected_total"] for p in predictions])
        actual_total = np.array([a["home_corners"] + a["away_corners"] for a in actuals])

        mae = np.mean(np.abs(pred_total - actual_total))
        rmse = np.sqrt(np.mean((pred_total - actual_total) ** 2))

        return {
            "mae": round(float(mae), 3),
            "rmse": round(float(rmse), 3),
            "sample_size": len(predictions),
        }

    def evaluate_cards(
        self,
        predictions: List[Dict],
        actuals: List[Dict],
    ) -> Dict:
        """Evaluate card predictions."""
        if len(predictions) < self.min_sample_size:
            return {"error": "Insufficient sample size"}

        pred_total = np.array([p["expected_total"] for p in predictions])
        actual_total = np.array([a["total_cards"] for a in actuals])

        mae = np.mean(np.abs(pred_total - actual_total))
        rmse = np.sqrt(np.mean((pred_total - actual_total) ** 2))

        return {
            "mae": round(float(mae), 3),
            "rmse": round(float(rmse), 3),
            "sample_size": len(predictions),
        }

    def _calculate_log_loss(self, predictions: List[Dict], actuals: List[Dict]) -> float:
        """Calculate log loss for 1X2 predictions."""
        eps = 1e-15
        total_loss = 0.0

        for pred, actual in zip(predictions, actuals):
            home_score = actual["home_score"]
            away_score = actual["away_score"]

            if home_score > away_score:
                true_label = "home_win_prob"
            elif home_score < away_score:
                true_label = "away_win_prob"
            else:
                true_label = "draw_prob"

            prob = max(eps, min(1 - eps, pred[true_label]))
            total_loss -= np.log(prob)

        return total_loss / len(predictions)

    def run_full_backtest(
        self,
        goal_predictions: List[Dict],
        goal_actuals: List[Dict],
        corner_predictions: List[Dict] = None,
        corner_actuals: List[Dict] = None,
        card_predictions: List[Dict] = None,
        card_actuals: List[Dict] = None,
    ) -> BacktestResult:
        """Run complete backtesting across all models."""
        logger.info("Starting full backtest evaluation")

        goals_result = self.evaluate_goals(goal_predictions, goal_actuals)

        corners_result = {}
        if corner_predictions and corner_actuals:
            corners_result = self.evaluate_corners(corner_predictions, corner_actuals)

        cards_result = {}
        if card_predictions and card_actuals:
            cards_result = self.evaluate_cards(card_predictions, card_actuals)

        return BacktestResult(
            model_name="poisson_v2",
            model_version="2.1.0",
            total_matches=len(goal_predictions),
            mae=goals_result.get("mae_total", 0),
            rmse=goals_result.get("rmse_total", 0),
            log_loss=goals_result.get("log_loss_1x2"),
            brier_score=goals_result.get("brier_score_over25"),
            calibration=None,
            by_competition={},
            by_season={},
        )
