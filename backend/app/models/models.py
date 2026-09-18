"""
SQLAlchemy ORM models for the Sports AI Analytics database.
Complete schema with all entities, relationships, and constraints.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, UniqueConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# ===== ENUMS =====
class MatchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class DataQuality(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"


class ScrapingStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    DUPLICATE = "duplicate"


# ===== CORE ENTITIES =====
class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=False)
    tier = Column(Integer, default=1)
    external_ids = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seasons = relationship("Season", back_populates="competition")
    matches = relationship("Match", back_populates="competition")

    __table_args__ = (
        Index("ix_competitions_name_country", "name", "country"),
    )


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    name = Column(String(50), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    competition = relationship("Competition", back_populates="seasons")
    matches = relationship("Match", back_populates="season")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    short_name = Column(String(20))
    country = Column(String(100))
    founded = Column(Integer)
    stadium = Column(String(200))
    logo_url = Column(String(500))
    external_ids = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    aliases = relationship("TeamAlias", back_populates="team")
    players = relationship("Player", back_populates="team")

    __table_args__ = (
        Index("ix_teams_name", "name"),
    )


class TeamAlias(Base):
    __tablename__ = "team_aliases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    alias = Column(String(200), nullable=False, unique=True)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="aliases")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    position = Column(String(50))
    number = Column(Integer)
    nationality = Column(String(100))
    age = Column(Integer)
    photo_url = Column(String(500))
    external_ids = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="players")
    aliases = relationship("PlayerAlias", back_populates="player")
    match_stats = relationship("PlayerMatchStatistics", back_populates="player")

    __table_args__ = (
        Index("ix_players_name", "name"),
    )


class PlayerAlias(Base):
    __tablename__ = "player_aliases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    alias = Column(String(200), nullable=False, unique=True)
    confidence = Float = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", back_populates="aliases")


class Referee(Base):
    __tablename__ = "referees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    nationality = Column(String(100))
    external_ids = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    matches = relationship("Match", back_populates="referee")
    match_stats = relationship("RefereeMatchStatistics", back_populates="referee")

    __table_args__ = (
        Index("ix_referees_name", "name"),
    )


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100))
    capacity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== MATCH ENTITIES =====
class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    match_date = Column(DateTime, nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    referee_id = Column(Integer, ForeignKey("referees.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))
    status = Column(SQLEnum(MatchStatus), default=MatchStatus.SCHEDULED)
    home_score = Column(Integer)
    away_score = Column(Integer)
    external_id = Column(String(200))
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    competition = relationship("Competition", back_populates="matches")
    season = relationship("Season", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    referee = relationship("Referee", back_populates="matches")
    venue = relationship("Venue")
    events = relationship("MatchEvent", back_populates="match")
    statistics = relationship("MatchStatistics", uselist=False, back_populates="match")
    predictions = relationship("Prediction", back_populates="match")

    __table_args__ = (
        Index("ix_matches_date", "match_date"),
        Index("ix_matches_status", "status"),
        Index("ix_matches_external", "external_id", "source"),
        UniqueConstraint("external_id", "source", name="uq_match_external"),
    )


class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    minute = Column(Integer)
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    detail = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="events")


class MatchStatistics(Base):
    __tablename__ = "match_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)
    home_shots = Column(Integer)
    away_shots = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    home_possession = Column(Float)
    away_possession = Column(Float)
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    home_fouls = Column(Integer)
    away_fouls = Column(Integer)
    home_yellow_cards = Column(Integer)
    away_yellow_cards = Column(Integer)
    home_red_cards = Column(Integer)
    away_red_cards = Column(Integer)
    home_xg = Column(Float)
    away_xg = Column(Float)
    home_offsides = Column(Integer)
    away_offsides = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    match = relationship("Match", back_populates="statistics")


class PlayerMatchStatistics(Base):
    __tablename__ = "player_match_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    position = Column(String(50))
    minutes = Column(Integer)
    started = Column(Boolean, default=False)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    expected_goals = Column(Float)
    passes = Column(Integer)
    fouls = Column(Integer)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", back_populates="match_stats")
    match = relationship("Match")

    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_player_match"),
    )


class RefereeMatchStatistics(Base):
    __tablename__ = "referee_match_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    referee_id = Column(Integer, ForeignKey("referees.id"), nullable=False)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    fouls = Column(Integer)
    penalties = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    referee = relationship("Referee", back_populates="match_stats")


# ===== SCRAPING ENTITIES =====
class RawScrapingData(Base):
    __tablename__ = "raw_scraping_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    external_id = Column(String(200))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    content = Column(Text)
    content_hash = Column(String(64), nullable=False)
    status = Column(SQLEnum(ScrapingStatus), default=ScrapingStatus.PENDING)
    parser_version = Column(String(20))
    scraper_version = Column(String(20))
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_raw_data_hash", "content_hash"),
        Index("ix_raw_data_source_external", "source", "external_id"),
    )


class ScrapingRun(Base):
    __tablename__ = "scraping_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    status = Column(String(50))
    items_scraped = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    items_errors = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    base_url = Column(String(500))
    scraper_class = Column(String(200))
    is_active = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== PREDICTION ENTITIES =====
class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    feature_version = Column(String(20), nullable=False)
    features = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("match_id", "feature_version", name="uq_feature_match_version"),
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    config = Column(JSON)
    metrics = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    feature_version = Column(String(20), nullable=False)
    inputs = Column(JSON)
    outputs = Column(JSON, nullable=False)
    data_quality = Column(SQLEnum(DataQuality), default=DataQuality.MEDIUM)
    sample_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="predictions")

    __table_args__ = (
        Index("ix_predictions_match", "match_id"),
    )


class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    actual_result = Column(JSON)
    metrics = Column(JSON)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
