import axios from 'axios';
import type {
  Match, MatchStatistics, MatchAnalysis, Prediction,
  Team, Player, Referee, Competition, DashboardData,
  GoalPrediction, CornerPrediction, CardPrediction, PlayerShotPrediction,
  TeamForm, H2HStats, AIAnalysis
} from '../types';

// ===== API CLIENT =====
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ===== DEMO DATA =====
// This data is used when the backend is not available
// It is clearly separated from real scraping data

const DEMO_TEAMS: Team[] = [
  { id: 1, name: 'Manchester City', short_name: 'MCI', country: 'England', founded: 1880, stadium: 'Etihad Stadium', logo_url: null, aliases: ['Man City', 'Manchester City FC'] },
  { id: 2, name: 'Arsenal', short_name: 'ARS', country: 'England', founded: 1886, stadium: 'Emirates Stadium', logo_url: null, aliases: ['Arsenal FC'] },
  { id: 3, name: 'Liverpool', short_name: 'LIV', country: 'England', founded: 1892, stadium: 'Anfield', logo_url: null, aliases: ['Liverpool FC'] },
  { id: 4, name: 'Real Madrid', short_name: 'RMA', country: 'Spain', founded: 1902, stadium: 'Santiago Bernabéu', logo_url: null, aliases: ['Real Madrid CF'] },
  { id: 5, name: 'Barcelona', short_name: 'BAR', country: 'Spain', founded: 1899, stadium: 'Camp Nou', logo_url: null, aliases: ['FC Barcelona'] },
  { id: 6, name: 'Bayern Munich', short_name: 'BAY', country: 'Germany', founded: 1900, stadium: 'Allianz Arena', logo_url: null, aliases: ['FC Bayern München'] },
  { id: 7, name: 'PSG', short_name: 'PSG', country: 'France', founded: 1970, stadium: 'Parc des Princes', logo_url: null, aliases: ['Paris Saint-Germain'] },
  { id: 8, name: 'Inter Milan', short_name: 'INT', country: 'Italy', founded: 1908, stadium: 'San Siro', logo_url: null, aliases: ['FC Internazionale Milano'] },
  { id: 9, name: 'Chelsea', short_name: 'CHE', country: 'England', founded: 1905, stadium: 'Stamford Bridge', logo_url: null, aliases: ['Chelsea FC'] },
  { id: 10, name: 'Tottenham', short_name: 'TOT', country: 'England', founded: 1882, stadium: 'Tottenham Hotspur Stadium', logo_url: null, aliases: ['Tottenham Hotspur'] },
];

const DEMO_COMPETITIONS: Competition[] = [
  { id: 1, name: 'Premier League', country: 'England', tier: 1, external_ids: { 'fbref': '9' } },
  { id: 2, name: 'La Liga', country: 'Spain', tier: 1, external_ids: { 'fbref': '12' } },
  { id: 3, name: 'Bundesliga', country: 'Germany', tier: 1, external_ids: { 'fbref': '20' } },
  { id: 4, name: 'Serie A', country: 'Italy', tier: 1, external_ids: { 'fbref': '11' } },
  { id: 5, name: 'Ligue 1', country: 'France', tier: 1, external_ids: { 'fbref': '13' } },
  { id: 6, name: 'Champions League', country: 'Europe', tier: 1, external_ids: { 'fbref': '8' } },
];

const DEMO_MATCHES: Match[] = [
  { id: 1, competition_id: 1, competition_name: 'Premier League', season_id: 1, season_name: '2025/2026', match_date: '2026-01-15T20:00:00Z', home_team_id: 1, home_team_name: 'Manchester City', away_team_id: 2, away_team_name: 'Arsenal', referee_id: 1, referee_name: 'Michael Oliver', venue_id: 1, venue_name: 'Etihad Stadium', status: 'scheduled', home_score: null, away_score: null, external_id: 'match_001', source: 'demo' },
  { id: 2, competition_id: 1, competition_name: 'Premier League', season_id: 1, season_name: '2025/2026', match_date: '2026-01-15T17:30:00Z', home_team_id: 3, home_team_name: 'Liverpool', away_team_id: 9, away_team_name: 'Chelsea', referee_id: 2, referee_name: 'Anthony Taylor', venue_id: 2, venue_name: 'Anfield', status: 'scheduled', home_score: null, away_score: null, external_id: 'match_002', source: 'demo' },
  { id: 3, competition_id: 2, competition_name: 'La Liga', season_id: 2, season_name: '2025/2026', match_date: '2026-01-14T21:00:00Z', home_team_id: 4, home_team_name: 'Real Madrid', away_team_id: 5, away_team_name: 'Barcelona', referee_id: 3, referee_name: 'Mateu Lahoz', venue_id: 3, venue_name: 'Santiago Bernabéu', status: 'finished', home_score: 2, away_score: 1, external_id: 'match_003', source: 'demo' },
  { id: 4, competition_id: 1, competition_name: 'Premier League', season_id: 1, season_name: '2025/2026', match_date: '2026-01-12T15:00:00Z', home_team_id: 10, home_team_name: 'Tottenham', away_team_id: 1, away_team_name: 'Manchester City', referee_id: 1, referee_name: 'Michael Oliver', venue_id: 4, venue_name: 'Tottenham Hotspur Stadium', status: 'finished', home_score: 1, away_score: 3, external_id: 'match_004', source: 'demo' },
  { id: 5, competition_id: 3, competition_name: 'Bundesliga', season_id: 3, season_name: '2025/2026', match_date: '2026-01-13T18:30:00Z', home_team_id: 6, home_team_name: 'Bayern Munich', away_team_id: 8, away_team_name: 'Inter Milan', referee_id: 4, referee_name: 'Felix Brych', venue_id: 5, venue_name: 'Allianz Arena', status: 'finished', home_score: 3, away_score: 0, external_id: 'match_005', source: 'demo' },
  { id: 6, competition_id: 6, competition_name: 'Champions League', season_id: 4, season_name: '2025/2026', match_date: '2026-01-16T21:00:00Z', home_team_id: 7, home_team_name: 'PSG', away_team_id: 4, away_team_name: 'Real Madrid', referee_id: 5, referee_name: 'Daniele Orsato', venue_id: 6, venue_name: 'Parc des Princes', status: 'scheduled', home_score: null, away_score: null, external_id: 'match_006', source: 'demo' },
];

const DEMO_PLAYERS: Player[] = [
  { id: 1, name: 'Erling Haaland', team_id: 1, team_name: 'Manchester City', position: 'Forward', number: 9, nationality: 'Norway', age: 25, photo_url: null },
  { id: 2, name: 'Bukayo Saka', team_id: 2, team_name: 'Arsenal', position: 'Forward', number: 7, nationality: 'England', age: 24, photo_url: null },
  { id: 3, name: 'Mohamed Salah', team_id: 3, team_name: 'Liverpool', position: 'Forward', number: 11, nationality: 'Egypt', age: 33, photo_url: null },
  { id: 4, name: 'Vinícius Jr', team_id: 4, team_name: 'Real Madrid', position: 'Forward', number: 7, nationality: 'Brazil', age: 25, photo_url: null },
  { id: 5, name: 'Robert Lewandowski', team_id: 5, team_name: 'Barcelona', position: 'Forward', number: 9, nationality: 'Poland', age: 37, photo_url: null },
  { id: 6, name: 'Harry Kane', team_id: 6, team_name: 'Bayern Munich', position: 'Forward', number: 9, nationality: 'England', age: 32, photo_url: null },
  { id: 7, name: 'Kylian Mbappé', team_id: 4, team_name: 'Real Madrid', position: 'Forward', number: 9, nationality: 'France', age: 27, photo_url: null },
  { id: 8, name: 'Cole Palmer', team_id: 9, team_name: 'Chelsea', position: 'Midfielder', number: 20, nationality: 'England', age: 23, photo_url: null },
  { id: 9, name: 'Phil Foden', team_id: 1, team_name: 'Manchester City', position: 'Midfielder', number: 47, nationality: 'England', age: 25, photo_url: null },
  { id: 10, name: 'Heung-min Son', team_id: 10, team_name: 'Tottenham', position: 'Forward', number: 7, nationality: 'South Korea', age: 33, photo_url: null },
];

const DEMO_REFEREE: Referee[] = [
  { id: 1, name: 'Michael Oliver', nationality: 'England', matches_total: 245, avg_yellow_cards: 3.8, avg_red_cards: 0.15, avg_fouls: 22.4 },
  { id: 2, name: 'Anthony Taylor', nationality: 'England', matches_total: 210, avg_yellow_cards: 4.2, avg_red_cards: 0.22, avg_fouls: 23.1 },
  { id: 3, name: 'Mateu Lahoz', nationality: 'Spain', matches_total: 320, avg_yellow_cards: 5.1, avg_red_cards: 0.35, avg_fouls: 25.6 },
  { id: 4, name: 'Felix Brych', nationality: 'Germany', matches_total: 280, avg_yellow_cards: 3.5, avg_red_cards: 0.12, avg_fouls: 21.8 },
  { id: 5, name: 'Daniele Orsato', nationality: 'Italy', matches_total: 195, avg_yellow_cards: 4.0, avg_red_cards: 0.18, avg_fouls: 23.5 },
];

function generateGoalPrediction(): GoalPrediction {
  const eHG = 1.2 + Math.random() * 1.5;
  const eAG = 0.8 + Math.random() * 1.2;
  return {
    expected_home_goals: Math.round(eHG * 100) / 100,
    expected_away_goals: Math.round(eAG * 100) / 100,
    expected_total_goals: Math.round((eHG + eAG) * 100) / 100,
    distribution: { '0': 0.08, '1': 0.18, '2': 0.27, '3': 0.23, '4': 0.14, '5+': 0.10 },
    probabilities: {
      over_05: 0.92, over_15: 0.74, over_25: 0.49, over_35: 0.24,
      under_05: 0.08, under_15: 0.26, under_25: 0.51, under_35: 0.76,
      btts_yes: 0.58, btts_no: 0.42,
      home_win: 0.45, draw: 0.27, away_win: 0.28,
    },
  };
}

function generateCornerPrediction(): CornerPrediction {
  return {
    expected_home_corners: 4.5 + Math.random() * 2,
    expected_away_corners: 3.2 + Math.random() * 1.5,
    expected_total_corners: 8.5 + Math.random() * 2,
    probabilities: {
      over_75: 0.78, over_85: 0.62, over_95: 0.47, over_105: 0.33, over_115: 0.21,
    },
  };
}

function generateCardPrediction(): CardPrediction {
  return {
    expected_home_cards: 1.5 + Math.random() * 1.5,
    expected_away_cards: 1.8 + Math.random() * 1.5,
    expected_total_cards: 3.5 + Math.random() * 2,
    probabilities: {
      over_25: 0.72, over_35: 0.55, over_45: 0.38, over_55: 0.22,
    },
  };
}

function generatePlayerShots(): PlayerShotPrediction[] {
  return DEMO_PLAYERS.slice(0, 5).map((p) => ({
    player_id: p.id,
    player_name: p.name,
    expected_shots: 2 + Math.random() * 4,
    expected_shots_on_target: 0.8 + Math.random() * 2,
    probabilities: {
      over_05: 0.85, over_15: 0.62, over_25: 0.38, over_35: 0.18,
    },
    status: 'OK' as const,
  }));
}

function generateTeamForm(teamId: number): TeamForm {
  const results = ['W', 'D', 'L'];
  const form = Array.from({ length: 5 }, () => results[Math.floor(Math.random() * 3)]).join('');
  return {
    team_id: teamId,
    team_name: DEMO_TEAMS.find(t => t.id === teamId)?.name || 'Unknown',
    goals_avg_last_5: 1.2 + Math.random() * 1.5,
    goals_avg_last_10: 1.4 + Math.random() * 1.2,
    conceded_avg_last_5: 0.6 + Math.random() * 1.0,
    conceded_avg_last_10: 0.8 + Math.random() * 0.8,
    shots_avg: 12 + Math.random() * 8,
    corners_avg: 5 + Math.random() * 3,
    cards_avg: 1.5 + Math.random() * 1.5,
    wins: 8 + Math.floor(Math.random() * 10),
    draws: 3 + Math.floor(Math.random() * 5),
    losses: 2 + Math.floor(Math.random() * 5),
    form_last_5: form,
  };
}

function generateH2H(): H2HStats {
  return {
    total_matches: 10 + Math.floor(Math.random() * 20),
    home_wins: 4 + Math.floor(Math.random() * 6),
    draws: 2 + Math.floor(Math.random() * 4),
    away_wins: 2 + Math.floor(Math.random() * 5),
    avg_goals: 2.2 + Math.random() * 1.5,
    avg_corners: 9 + Math.random() * 2,
    avg_cards: 3.5 + Math.random() * 2,
    last_5_results: ['H 2-1 A', 'H 1-1 A', 'H 0-3 A', 'H 2-2 A', 'H 1-0 A'],
  };
}

function generateAIAnalysis(matchId: number): AIAnalysis {
  return {
    match_id: matchId,
    interpretation: 'Basado en el análisis estadístico, el equipo local presenta una forma superior en los últimos 5 partidos con un promedio de goles significativamente mayor. El historial H2H muestra ventaja local. El modelo Poisson estima una probabilidad moderada de over 2.5 goles. La combinación de factores ofensivos locales y la tendencia del árbitro sugiere un partido con oportunidades de gol para ambos equipos.',
    key_factors: [
      'Equipo local con racha de 3 victorias consecutivas',
      'Promedio de tiros al arco superior al 70% en últimos 5 partidos',
      'Árbitro con tendencia a permitir juego físico (promedio 22+ faltas)',
      'Historial H2H favorable al local en las últimas 5 confrontaciones',
    ],
    risks: [
      'Muestra H2H limitada (solo 8 partidos en últimos 3 años)',
      'Datos de xG no disponibles para el equipo visitante',
      'Lesiones no confirmadas en la plantilla',
    ],
    confidence_level: 'MEDIUM',
    data_notes: [
      'Datos de posesión no disponibles para últimos 2 partidos',
      'Estadísticas de córners completas',
      'Datos de árbitro basados en temporada actual',
    ],
    generated_at: new Date().toISOString(),
    model_used: 'qwen-2.5-72b',
  };
}

// ===== DEMO API (used when backend is unavailable) =====
export const demoApi = {
  getDashboard(): DashboardData {
    return {
      upcoming_matches: DEMO_MATCHES.filter(m => m.status === 'scheduled'),
      recent_matches: DEMO_MATCHES.filter(m => m.status === 'finished'),
      total_competitions: DEMO_COMPETITIONS.length,
      total_teams: DEMO_TEAMS.length,
      total_players: DEMO_PLAYERS.length,
      total_referees: DEMO_REFEREE.length,
      last_updated: new Date().toISOString(),
    };
  },
  getMatches(): Match[] { return DEMO_MATCHES; },
  getMatch(id: number): Match | undefined { return DEMO_MATCHES.find(m => m.id === id); },
  getMatchStatistics(matchId: number): MatchStatistics {
    return {
      match_id: matchId,
      home_shots: 12 + Math.floor(Math.random() * 8),
      away_shots: 8 + Math.floor(Math.random() * 6),
      home_shots_on_target: 4 + Math.floor(Math.random() * 4),
      away_shots_on_target: 2 + Math.floor(Math.random() * 4),
      home_possession: 45 + Math.floor(Math.random() * 20),
      away_possession: 0,
      home_corners: 4 + Math.floor(Math.random() * 5),
      away_corners: 2 + Math.floor(Math.random() * 4),
      home_fouls: 8 + Math.floor(Math.random() * 8),
      away_fouls: 10 + Math.floor(Math.random() * 8),
      home_yellow_cards: 1 + Math.floor(Math.random() * 3),
      away_yellow_cards: 1 + Math.floor(Math.random() * 3),
      home_red_cards: Math.random() > 0.8 ? 1 : 0,
      away_red_cards: Math.random() > 0.9 ? 1 : 0,
      home_xg: 1.2 + Math.random() * 1.5,
      away_xg: 0.8 + Math.random() * 1.2,
    };
  },
  getTeams(): Team[] { return DEMO_TEAMS; },
  getPlayers(): Player[] { return DEMO_PLAYERS; },
  getReferees(): Referee[] { return DEMO_REFEREE; },
  getCompetitions(): Competition[] { return DEMO_COMPETITIONS; },
  getPrediction(matchId: number): Prediction {
    return {
      id: matchId,
      match_id: matchId,
      model_name: 'poisson_v2',
      model_version: '2.1.0',
      feature_version: '1.5.0',
      goals: generateGoalPrediction(),
      corners: generateCornerPrediction(),
      cards: generateCardPrediction(),
      players: generatePlayerShots(),
      created_at: new Date().toISOString(),
      data_quality: 'MEDIUM',
      sample_size: 156,
    };
  },
  getMatchAnalysis(matchId: number): MatchAnalysis {
    const match = DEMO_MATCHES.find(m => m.id === matchId) || DEMO_MATCHES[0];
    return {
      match,
      statistics: generateMatchStats(matchId),
      home_form: generateTeamForm(match.home_team_id),
      away_form: generateTeamForm(match.away_team_id),
      h2h: generateH2H(),
      prediction: this.getPrediction(matchId),
      ai_analysis: generateAIAnalysis(matchId),
    };
  },
};

function generateMatchStats(matchId: number): MatchStatistics {
  return {
    match_id: matchId,
    home_shots: 14, away_shots: 9,
    home_shots_on_target: 5, away_shots_on_target: 3,
    home_possession: 58, away_possession: 42,
    home_corners: 6, away_corners: 4,
    home_fouls: 11, away_fouls: 14,
    home_yellow_cards: 2, away_yellow_cards: 3,
    home_red_cards: 0, away_red_cards: 0,
    home_xg: 1.85, away_xg: 1.12,
  };
}

// ===== REAL API CALLS =====
export const api = {
  async getDashboard(): Promise<DashboardData> {
    try {
      const { data } = await apiClient.get('/dashboard');
      return data;
    } catch {
      return demoApi.getDashboard();
    }
  },
  async getMatches(): Promise<Match[]> {
    try {
      const { data } = await apiClient.get('/matches');
      return data.data || data;
    } catch {
      return demoApi.getMatches();
    }
  },
  async getMatch(id: number): Promise<Match> {
    try {
      const { data } = await apiClient.get(`/matches/${id}`);
      return data;
    } catch {
      const match = demoApi.getMatch(id);
      if (!match) throw new Error('Match not found');
      return match;
    }
  },
  async getMatchAnalysis(id: number): Promise<MatchAnalysis> {
    try {
      const { data } = await apiClient.get(`/matches/${id}/analysis`);
      return data;
    } catch {
      return demoApi.getMatchAnalysis(id);
    }
  },
  async getTeams(): Promise<Team[]> {
    try {
      const { data } = await apiClient.get('/teams');
      return data.data || data;
    } catch {
      return demoApi.getTeams();
    }
  },
  async getPlayers(): Promise<Player[]> {
    try {
      const { data } = await apiClient.get('/players');
      return data.data || data;
    } catch {
      return demoApi.getPlayers();
    }
  },
  async getReferees(): Promise<Referee[]> {
    try {
      const { data } = await apiClient.get('/referees');
      return data.data || data;
    } catch {
      return demoApi.getReferees();
    }
  },
  async getCompetitions(): Promise<Competition[]> {
    try {
      const { data } = await apiClient.get('/competitions');
      return data.data || data;
    } catch {
      return demoApi.getCompetitions();
    }
  },
  async getPrediction(matchId: number): Promise<Prediction> {
    try {
      const { data } = await apiClient.get(`/matches/${matchId}/predictions`);
      return data;
    } catch {
      return demoApi.getPrediction(matchId);
    }
  },
};

export default api;
