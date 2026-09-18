# 🏆 Sports AI Analytics

Plataforma profesional de análisis estadístico deportivo con inteligencia artificial para fútbol.

## 🏗️ Arquitectura

```
FUENTES → SCRAPLING → RAW DATA → NORMALIZACIÓN → POSTGRESQL
    → FEATURE ENGINEERING → MODELOS ESTADÍSTICOS → PREDICTION ENGINE
    → QWEN AI → FASTAPI → REACT + TYPESCRIPT
```

## 🛠️ Tecnologías

### Backend
- **Python 3.12+** con **FastAPI**
- **SQLAlchemy 2.0** + **Alembic** para ORM y migraciones
- **PostgreSQL 16** como base de datos
- **Scrapling** (D4Vinci) para web scraping
- **SciPy/NumPy/Pandas** para análisis estadístico
- **Scikit-learn/Statsmodels** para modelos predictivos
- **Qwen** como sistema de interpretación IA
- **APScheduler** para actualización automática

### Frontend
- **React 18** + **TypeScript**
- **Vite** como build tool
- **Tailwind CSS** para estilos
- **TanStack Query** para gestión de estado
- **Recharts** para visualización de datos
- **React Router** para navegación

### Infraestructura
- **Docker** + **Docker Compose**
- Variables de entorno con `.env`

## 📁 Estructura del Proyecto

```
sports-ai-platform/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py        # Settings (pydantic-settings)
│   │   │   ├── database.py      # SQLAlchemy engine & sessions
│   │   │   └── logging.py       # Loguru configuration
│   │   ├── models/
│   │   │   └── models.py        # SQLAlchemy ORM models
│   │   ├── schemas/
│   │   │   └── schemas.py       # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── match_service.py
│   │   │   ├── analysis_service.py
│   │   │   └── __init__.py      # Team, Player, Referee, Dashboard services
│   │   ├── routes/
│   │   │   └── __init__.py      # All API route definitions
│   │   ├── prediction/
│   │   │   └── engine.py        # Goal, Corner, Card, Player models
│   │   ├── ai/
│   │   │   └── provider.py      # AIAnalysisProvider, QwenProvider
│   │   ├── scraping/
│   │   │   └── pipeline.py      # Fetcher, Spider, Parser, Normalizer
│   │   └── scheduler/
│   │       └── tasks.py         # APScheduler jobs
│   ├── tests/
│   │   ├── test_prediction_engine.py
│   │   ├── test_scraping.py
│   │   └── test_ai_provider.py
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/ (src/)
│   ├── App.tsx                  # Router & providers
│   ├── types/index.ts           # TypeScript types
│   ├── services/api.ts          # API client + demo data
│   ├── hooks/useQueries.ts      # TanStack Query hooks
│   ├── layouts/MainLayout.tsx   # Sidebar layout
│   └── pages/
│       ├── Dashboard.tsx
│       ├── Matches.tsx
│       ├── MatchDetail.tsx      # Full analysis view
│       ├── Teams.tsx
│       ├── Players.tsx
│       ├── Referees.tsx
│       ├── Statistics.tsx
│       └── Predictions.tsx
│
└── docs/
```

## 🚀 Instalación

### Con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd sports-ai-platform

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar servicios
docker compose up --build

# 4. Acceder
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Sin Docker

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend  # (o la raíz del proyecto para el build Vite)
npm install
npm run dev
```

## ⚙️ Configuración

### Variables de Entorno (.env)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL PostgreSQL async | `postgresql+asyncpg://...` |
| `AI_PROVIDER` | Proveedor IA | `qwen` |
| `QWEN_MODEL` | Modelo Qwen | `qwen-2.5-72b` |
| `QWEN_BASE_URL` | URL del servidor Qwen | `http://localhost:8080/v1` |
| `QWEN_API_KEY` | API Key | (vacío) |
| `SCRAPING_ENABLED` | Activar scraping | `true` |
| `SCRAPING_INTERVAL_MINUTES` | Intervalo scraping | `60` |
| `SCHEDULER_ENABLED` | Activar scheduler | `true` |

## 📊 Modelos Predictivos

### Modelo de Goles (Poisson)
- Calcula expected goals usando forma reciente, H2H, y ventaja local
- Genera distribución de goles (0, 1, 2, 3, 4, 5+)
- Probabilidades: Over/Under 0.5-3.5, BTTS, 1X2
- **Interface:** `GoalPredictionModel` (reemplazable)

### Modelo de Córners
- Basado en corners_for, corners_against, home/away
- Probabilidades Over 7.5 - 11.5
- **Interface:** `CornerPredictionModel`

### Modelo de Tarjetas
- Incorpora estadísticas del árbitro como variable
- Probabilidades Over 2.5 - 5.5
- **Interface:** `CardPredictionModel`

### Modelo de Tiros de Jugadores
- Ajusta por minutos esperados
- Requiere mínimo 5 partidos de muestra
- Si datos insuficientes: `status = INSUFFICIENT_DATA`

### Prevención de Data Leakage
- Solo se usan datos disponibles ANTES del partido
- No se incluye información futura en features

## 🤖 Integración Qwen

Qwen recibe datos estructurados (JSON) y genera interpretación:

```
DATOS → ESTADÍSTICA → MODELO → RESULTADOS → QWEN → INTERPRETACIÓN
```

**Reglas:**
- No inventa datos
- Distingue: OBSERVED_DATA, STATISTICAL_ESTIMATE, AI_INTERPRETATION
- Indica datos faltantes explícitamente
- No afirma certeza absoluta

**Configuración:**
```env
AI_PROVIDER=qwen
QWEN_MODEL=qwen-2.5-72b
QWEN_BASE_URL=http://localhost:8080/v1
```

## 🕷️ Scraping

Pipeline: `Fetcher → Spider → Parser → Validator → Normalizer → Database`

- **Deduplicación** por hash de contenido
- **Retries** con timeout configurable
- **Normalización** de nombres (aliases, fuzzy matching)
- **Datos RAW** almacenados para reproducibilidad
- **Incremental** - no re-procesa datos idénticos

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
pytest tests/test_prediction_engine.py -v  # Tests matemáticos
```

### Cobertura de Tests
- ✅ Modelos de predicción (matemáticos con datos controlados)
- ✅ Normalizador y aliases
- ✅ Parser de respuestas AI
- ✅ Pipeline de scraping
- ✅ Integración de PredictionEngine

## 📈 Backtesting

Métricas implementadas:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)
- Log Loss
- Brier Score
- Calibration

## 🔌 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/dashboard` | Dashboard data |
| GET | `/api/v1/matches` | Lista de partidos |
| GET | `/api/v1/matches/{id}` | Detalle de partido |
| GET | `/api/v1/matches/{id}/statistics` | Estadísticas |
| GET | `/api/v1/matches/{id}/predictions` | Predicciones |
| GET | `/api/v1/matches/{id}/analysis` | Análisis completo |
| GET | `/api/v1/teams` | Equipos |
| GET | `/api/v1/players` | Jugadores |
| GET | `/api/v1/referees` | Árbitros |
| GET | `/api/v1/competitions` | Competiciones |
| POST | `/api/v1/analysis/{id}/generate` | Generar análisis |
| GET | `/health` | Health check |

## 📋 Estado del Proyecto

```
Backend: READY (necesita configuración de DB y API keys)
Frontend: READY (funcional con datos demo)
Database: READY (esquema completo definido)
Scraping: READY (pipeline implementado)
Models: READY (Poisson + interfaces extensibles)
Qwen: READY (necesita QWEN_BASE_URL configurado)
Tests: PASS (tests matemáticos incluidos)
Docker: READY (docker-compose configurado)
```

## 📝 Licencia

MIT License
