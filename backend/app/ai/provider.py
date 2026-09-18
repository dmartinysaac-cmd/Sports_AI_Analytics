"""
AI Integration Layer - Provider interface and Qwen implementation.
Modular architecture allowing different AI providers.
"""
from typing import Dict, Any, Optional, Protocol
from dataclasses import dataclass
from loguru import logger
import json
import httpx

from app.core.config import settings


# ===== INTERFACE =====
class AIAnalysisProvider(Protocol):
    """Interface for AI analysis providers."""

    async def analyze(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive structured statistical data and return interpretation.
        Must NOT invent data. Must distinguish between observed data,
        statistical estimates, and AI interpretation.
        """
        ...


# ===== DATA CLASSES =====
@dataclass
class AIAnalysisResult:
    interpretation: str
    key_factors: list
    risks: list
    confidence_level: str
    data_notes: list
    model_used: str


# ===== PROMPT BUILDER =====
class PromptBuilder:
    """Builds structured prompts for AI analysis."""

    SYSTEM_PROMPT = """Eres un analista deportivo estadístico experto.

Analiza EXCLUSIVAMENTE la información estructurada proporcionada.

REGLAS ESTRICTAS:
1. No inventes datos ni estadísticas.
2. No reemplaces probabilidades estadísticas calculadas por el sistema.
3. Distingue claramente entre:
   - DATOS OBSERVADOS: información histórica confirmada
   - ESTIMACIONES ESTADÍSTICAS: resultados de modelos matemáticos
   - INTERPRETACIÓN IA: tu análisis basado en los datos anteriores

4. Si un dato no está disponible, indícalo explícitamente como "Dato no disponible".
5. Indica el tamaño de muestra cuando sea relevante.
6. Señala la incertidumbre cuando la muestra sea pequeña.
7. No afirmes certeza absoluta.
8. No conviertas correlación en causalidad.
9. No inventes lesiones, alineaciones, árbitros, estadísticas ni resultados.
10. Si los datos son insuficientes, dilo explícitamente.

FORMATO DE RESPUESTA:
- interpretation: Análisis general (2-3 párrafos)
- key_factors: Lista de factores clave observados
- risks: Lista de riesgos y limitaciones
- confidence_level: HIGH/MEDIUM/LOW
- data_notes: Notas sobre calidad y disponibilidad de datos"""

    def build_prompt(self, data: Dict[str, Any]) -> str:
        """Build the user prompt from structured data."""
        prompt_parts = [
            "Analiza el siguiente partido basado en los datos estadísticos proporcionados:\n"
        ]

        # Match info
        if "match" in data:
            m = data["match"]
            prompt_parts.append(f"PARTIDO: {m.get('home_team', 'Local')} vs {m.get('away_team', 'Visitante')}")
            prompt_parts.append(f"Competición: {m.get('competition', 'N/A')}")
            prompt_parts.append(f"Fecha: {m.get('date', 'N/A')}\n")

        # Team form
        if "team_form" in data:
            prompt_parts.append("FORMA DE EQUIPOS:")
            for side, form in data["team_form"].items():
                prompt_parts.append(f"  {side}: Forma últimos 5={form.get('form_last_5', 'N/A')}, "
                                   f"Goles/prom={form.get('goals_avg_last_5', 'N/A')}, "
                                   f"Recibidos={form.get('conceded_avg_last_5', 'N/A')}")
            prompt_parts.append("")

        # Goals prediction
        if "goals_prediction" in data:
            gp = data["goals_prediction"]
            prompt_parts.append("PREDICCIÓN DE GOLES (modelo estadístico):")
            prompt_parts.append(f"  xG Local: {gp.get('expected_home_goals', 'N/A')}")
            prompt_parts.append(f"  xG Visitante: {gp.get('expected_away_goals', 'N/A')}")
            prompt_parts.append(f"  Over 2.5: {gp.get('probabilities', {}).get('over_25', 'N/A')}")
            prompt_parts.append(f"  BTTS: {gp.get('probabilities', {}).get('btts_yes', 'N/A')}\n")

        # Corners prediction
        if "corners_prediction" in data:
            cp = data["corners_prediction"]
            prompt_parts.append("PREDICCIÓN DE CÓRNERS (modelo estadístico):")
            prompt_parts.append(f"  Total esperado: {cp.get('expected_total_corners', 'N/A')}")
            prompt_parts.append(f"  Over 9.5: {cp.get('probabilities', {}).get('over_95', 'N/A')}\n")

        # Cards prediction
        if "cards_prediction" in data:
            cp = data["cards_prediction"]
            prompt_parts.append("PREDICCIÓN DE TARJETAS (modelo estadístico):")
            prompt_parts.append(f"  Total esperado: {cp.get('expected_total_cards', 'N/A')}")
            if "referee" in data:
                prompt_parts.append(f"  Árbitro: {data['referee'].get('name', 'N/A')} "
                                   f"(promedio tarjetas: {data['referee'].get('avg_yellow_cards', 'N/A')})\n")

        # H2H
        if "h2h" in data:
            h = data["h2h"]
            prompt_parts.append(f"HISTORIAL H2H: {h.get('total_matches', 0)} partidos, "
                               f"Goles promedio: {h.get('avg_goals', 'N/A')}\n")

        # Data quality
        if "metadata" in data:
            prompt_parts.append(f"METADATOS: Calidad={data['metadata'].get('data_quality', 'N/A')}, "
                               f"Muestra={data['metadata'].get('sample_size', 'N/A')} partidos")

        return "\n".join(prompt_parts)


# ===== QWEN RESPONSE PARSER =====
class QwenResponseParser:
    """Parses Qwen AI responses into structured format."""

    def parse(self, raw_response: str) -> AIAnalysisResult:
        """Parse the AI response into structured data."""
        try:
            # Try JSON parse first
            data = json.loads(raw_response)
            return AIAnalysisResult(
                interpretation=data.get("interpretation", "Análisis no disponible"),
                key_factors=data.get("key_factors", []),
                risks=data.get("risks", []),
                confidence_level=data.get("confidence_level", "MEDIUM"),
                data_notes=data.get("data_notes", []),
                model_used=data.get("model_used", "qwen"),
            )
        except json.JSONDecodeError:
            # Fallback: extract structured info from text
            return AIAnalysisResult(
                interpretation=raw_response[:500] if raw_response else "Análisis no disponible",
                key_factors=self._extract_list(raw_response, "factores"),
                risks=self._extract_list(raw_response, "riesgos"),
                confidence_level="MEDIUM",
                data_notes=["Respuesta parseada de texto libre"],
                model_used="qwen",
            )

    def _extract_list(self, text: str, keyword: str) -> list:
        """Extract list items from text response."""
        items = []
        lines = text.split("\n")
        capture = False
        for line in lines:
            if keyword.lower() in line.lower():
                capture = True
                continue
            if capture and line.strip().startswith(("-", "•", "*")):
                items.append(line.strip().lstrip("-•* ").strip())
            elif capture and line.strip() == "":
                capture = False
        return items[:5]  # Limit to 5 items


# ===== QWEN PROVIDER =====
class QwenProvider:
    """
    Qwen AI provider implementation.
    Sends structured data and receives interpretation.
    """

    def __init__(self):
        self.base_url = settings.QWEN_BASE_URL
        self.model = settings.QWEN_MODEL
        self.api_key = settings.QWEN_API_KEY
        self.timeout = settings.QWEN_TIMEOUT
        self.max_tokens = settings.QWEN_MAX_TOKENS
        self.prompt_builder = PromptBuilder()
        self.response_parser = QwenResponseParser()

    async def analyze(self, structured_data: Dict[str, Any]) -> AIAnalysisResult:
        """Send structured data to Qwen and get interpretation."""
        logger.info(f"Sending analysis request to Qwen ({self.model})")

        system_prompt = PromptBuilder.SYSTEM_PROMPT
        user_prompt = self.prompt_builder.build_prompt(structured_data)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": self.max_tokens,
                        "temperature": 0.3,  # Low temperature for factual responses
                    },
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                result = self.response_parser.parse(content)
                result.model_used = self.model

                logger.info(f"Qwen analysis complete. Confidence: {result.confidence_level}")
                return result

        except httpx.TimeoutException:
            logger.error("Qwen request timed out")
            return self._fallback_response("Timeout en la solicitud al modelo AI")
        except httpx.HTTPStatusError as e:
            logger.error(f"Qwen HTTP error: {e.response.status_code}")
            return self._fallback_response(f"Error HTTP: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Qwen error: {str(e)}")
            return self._fallback_response(f"Error: {str(e)}")

    def _fallback_response(self, error_msg: str) -> AIAnalysisResult:
        """Return a fallback response when AI is unavailable."""
        return AIAnalysisResult(
            interpretation=f"No se pudo generar el análisis con IA. {error_msg}. "
                          f"Los datos estadísticos del modelo siguen disponibles.",
            key_factors=["Análisis AI no disponible - usar solo datos estadísticos"],
            risks=[error_msg],
            confidence_level="LOW",
            data_notes=["Modelo AI no disponible en este momento"],
            model_used=f"{self.model} (error)",
        )


# ===== PROVIDER FACTORY =====
def get_ai_provider() -> "QwenProvider":
    """Factory function to get the configured AI provider."""
    provider_name = settings.AI_PROVIDER.lower()
    if provider_name == "qwen":
        return QwenProvider()
    else:
        logger.warning(f"Unknown AI provider: {provider_name}, defaulting to Qwen")
        return QwenProvider()
