"""
Tests for the AI provider (Qwen integration).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.ai.provider import PromptBuilder, QwenResponseParser, AIAnalysisResult


class TestPromptBuilder:
    """Tests for prompt construction."""

    def setup_method(self):
        self.builder = PromptBuilder()

    def test_build_prompt_with_match_data(self):
        data = {
            "match": {
                "home_team": "Manchester City",
                "away_team": "Arsenal",
                "competition": "Premier League",
                "date": "2026-01-15",
            },
            "team_form": {
                "local": {"form_last_5": "WWDWW", "goals_avg_last_5": 2.1, "conceded_avg_last_5": 0.6},
                "visitante": {"form_last_5": "WDWLW", "goals_avg_last_5": 1.5, "conceded_avg_last_5": 1.2},
            },
            "goals_prediction": {
                "expected_home_goals": 1.85,
                "expected_away_goals": 1.12,
                "probabilities": {"over_25": 0.52, "btts_yes": 0.58},
            },
        }
        prompt = self.builder.build_prompt(data)
        assert "Manchester City" in prompt
        assert "Arsenal" in prompt
        assert "1.85" in prompt

    def test_build_prompt_handles_missing_data(self):
        data = {"match": {"home_team": "Test"}}
        prompt = self.builder.build_prompt(data)
        assert "Test" in prompt

    def test_system_prompt_contains_rules(self):
        assert "No inventes" in PromptBuilder.SYSTEM_PROMPT
        assert "DATOS OBSERVADOS" in PromptBuilder.SYSTEM_PROMPT
        assert "ESTIMACIONES ESTADÍSTICAS" in PromptBuilder.SYSTEM_PROMPT


class TestQwenResponseParser:
    """Tests for parsing Qwen AI responses."""

    def setup_method(self):
        self.parser = QwenResponseParser()

    def test_parse_json_response(self):
        import json
        response = json.dumps({
            "interpretation": "El equipo local tiene ventaja estadística.",
            "key_factors": ["Forma superior", "Ventaja local"],
            "risks": ["Muestra limitada"],
            "confidence_level": "MEDIUM",
            "data_notes": ["Datos completos"],
            "model_used": "qwen-2.5-72b",
        })
        result = self.parser.parse(response)
        assert result.interpretation == "El equipo local tiene ventaja estadística."
        assert len(result.key_factors) == 2
        assert result.confidence_level == "MEDIUM"

    def test_parse_text_response_fallback(self):
        response = """Análisis del partido:
        El equipo local muestra mejor forma.

        Factores clave:
        - Mejor racha de victorias
        - Ventaja de local

        Riesgos:
        - Datos limitados del visitante
        """
        result = self.parser.parse(response)
        assert len(result.interpretation) > 0
        assert result.confidence_level == "MEDIUM"

    def test_parse_empty_response(self):
        result = self.parser.parse("")
        assert "no disponible" in result.interpretation.lower() or result.interpretation == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
