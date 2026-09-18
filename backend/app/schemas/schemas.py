"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MatchStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class DataQualityEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"


# ===== Core Schemas =====
class CompetitionSchema(BaseModel):
    id: int
    name: str
    country: str
    tier: int = 1
    external_ids: Dict[str, str] = {}

    class Config:
        from_attributes = True


class TeamSchema(BaseModel):
    id: int
    name: str
    short_name: Optional[str] = None
    country: Optional[str] = None
    founded: Optional[int] = None
    stadium: Optional[str] = None
    logo_url: Optional[str] = None
    aliases: List[str] = []

    class Config:
        from_attributes = True


class PlayerSchema(BaseModel):
    id: int
    name: str
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    position: Optional[str] = None
    number: Optional[int] = None
    nationality: Optional[str] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True


class RefereeSchema(BaseModel):
    id: int
    name: str
    nationality: Optional[str] = None
    matches_total: int = 0
    avg_yellow_cards: float = 0.0
    avg_red_cards: float = 0.0
    avg_fouls: float = 0.0

    class Config:
        from_attributes = True


# ===== Match Schemas =====
class MatchSchema(BaseModel):
    id: int
    competition_id: int
    competition_name: str
    season_id: Optional[int] = None
    season_name: Optional[str] = None
    match_date: datetime
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    referee_id: Optional[int] = None
    referee_name: Optional[str] = None
    venue_id: Optional[int] = None
    venue_name: Optional[str] = None
    status: MatchStatusEnum
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    external_id: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class MatchStatisticsSchema(BaseModel):
    match_id: int
    home_shots: Optional[int] = None
    away_shots: Optional[int] = None
    home_shots_on_target: Optional[int] = None
    away_shots_on_target: Optional[int] = None
    home_possession: Optional[float] = None
    away_possession: Optional[float] = None
    home_corners: Optional[int] = None
    away_corners: Optional[int] = None
    home_fouls: Optional[int] = None
    away_fouls: Optional[int] = None
    home_yellow_cards: Optional[int] = None
    away_yellow_cards: Optional[int] = None
    home_red_cards: Optional[int] = None
    away_red_cards: Optional[int] = None
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None

    class Config:
        from_attributes = True


# ===== Prediction Schemas =====
class GoalProbabilities(BaseModel):
    over_05: float
    over_15: float
    over_25: float
    over_35: float
    under_05: float
    under_15: float
    under_25: float
    under_35: float
    btts_yes: float
    btts_no: float
    home_win: float
    draw: float
    away_win: float


class GoalPredictionSchema(BaseModel):
    expected_home_goals: float
    expected_away_goals: float
    expected_total_goals: float
    distribution: Dict[str, float]
    probabilities: GoalProbabilities


class CornerProbabilities(BaseModel):
    over_75: float
    over_85: float
    over_95: float
    over_105: float
    over_115: float


class CornerPredictionSchema(BaseModel):
    expected_home_corners: float
    expected_away_corners: float
    expected_total_corners: float
    probabilities: CornerProbabilities


class CardProbabilities(BaseModel):
    over_25: float
    over_35: float
    over_45: float
    over_55: float


class CardPredictionSchema(BaseModel):
    expected_home_cards: float
    expected_away_cards: float
    expected_total_cards: float
    probabilities: CardProbabilities


class PlayerShotProbabilities(BaseModel):
    over_05: float
    over_15: float
    over_25: float
    over_35: float


class PlayerShotPredictionSchema(BaseModel):
    player_id: int
    player_name: str
    expected_shots: float
    expected_shots_on_target: float
    probabilities: PlayerShotProbabilities
    status: str = "OK"


class PredictionSchema(BaseModel):
    id: int
    match_id: int
    model_name: str
    model_version: str
    feature_version: str
    goals: GoalPredictionSchema
    corners: CornerPredictionSchema
    cards: CardPredictionSchema
    players: List[PlayerShotPredictionSchema] = []
    created_at: datetime
    data_quality: DataQualityEnum
    sample_size: int

    class Config:
        from_attributes = True


# ===== Analysis Schemas =====
class TeamFormSchema(BaseModel):
    team_id: int
    team_name: str
    goals_avg_last_5: float
    goals_avg_last_10: float
    conceded_avg_last_5: float
    conceded_avg_last_10: float
    shots_avg: float
    corners_avg: float
    cards_avg: float
    wins: int
    draws: int
    losses: int
    form_last_5: str


class H2HSchema(BaseModel):
    total_matches: int
    home_wins: int
    draws: int
    away_wins: int
    avg_goals: float
    avg_corners: float
    avg_cards: float
    last_5_results: List[str]


class AIAnalysisSchema(BaseModel):
    match_id: int
    interpretation: str
    key_factors: List[str]
    risks: List[str]
    confidence_level: str
    data_notes: List[str]
    generated_at: datetime
    model_used: str


class MatchAnalysisSchema(BaseModel):
    match: MatchSchema
    statistics: Optional[MatchStatisticsSchema] = None
    home_form: TeamFormSchema
    away_form: TeamFormSchema
    h2h: H2HSchema
    prediction: Optional[PredictionSchema] = None
    ai_analysis: Optional[AIAnalysisSchema] = None


# ===== Dashboard Schema =====
class DashboardSchema(BaseModel):
    upcoming_matches: List[MatchSchema]
    recent_matches: List[MatchSchema]
    total_competitions: int
    total_teams: int
    total_players: int
    total_referees: int
    last_updated: datetime
