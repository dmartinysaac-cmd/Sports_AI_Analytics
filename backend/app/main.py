"""
Sports AI Analytics - FastAPI Application
Main entry point for the backend API.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.routes import dashboard, matches, teams, players, referees, competitions, analysis
from app.scheduler.tasks import setup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup and shutdown."""
    setup_logging()
    # Setup scheduler for automatic data updates
    scheduler = setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="Sports AI Analytics API",
    description="API para análisis estadístico deportivo con modelos predictivos y IA",
    version="2.1.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(matches.router, prefix="/api/v1", tags=["Matches"])
app.include_router(teams.router, prefix="/api/v1", tags=["Teams"])
app.include_router(players.router, prefix="/api/v1", tags=["Players"])
app.include_router(referees.router, prefix="/api/v1", tags=["Referees"])
app.include_router(competitions.router, prefix="/api/v1", tags=["Competitions"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.1.0", "model": "poisson_v2"}
