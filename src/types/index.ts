// ===== CORE TYPES =====
export interface Competition {
  id: number;
  name: string;
  country: string;
  tier: number;
  external_ids: Record<string, string>;
}

export interface Season {
  id: number;
  competition_id: number;
  name: string;
  start_date: string;
  end_date: string;
}

export interface Team {
  id: number;
  name: string;
  short_name: string;
  country: string;
  founded: number | null;
  stadium: string | null;
  logo_url: string | null;
  aliases: string[];
}

export interface Player {
  id: number;
  name: string;
  team_id: number;
  team_name: string;
  position: string;
  number: number | null;
  nationality: string | null;
  age: number | null;
  photo_url: string | null;
}

export interface Referee {
  id: number;
  name: string;
  nationality: string | null;
  matches_total: number;
  avg_yellow_cards: number;
  avg_red_cards: number;
  avg_fouls: number;
}

export interface Venue {
  id: number;
  name: string;
  city: string;
  capacity: number | null;
}

// ===== MATCH TYPES =====
export interface Match {
  id: number;
  competition_id: number;
  competition_name: string;
  season_id: number;
  season_name: string;
  match_date: string;
  home_team_id: number;
  home_team_name: string;
  away_team_id: number;
  away_team_name: string;
  referee_id: number | null;
  referee_name: string | null;
  venue_id: number | null;
  venue_name: string | null;
  status: 'scheduled' | 'live' | 'finished' | 'postponed' | 'cancelled';
  home_score: number | null;
  away_score: number | null;
  external_id: string | null;
  source: string | null;
}

export interface MatchStatistics {
  match_id: number;
  home_shots: number | null;
  away_shots: number | null;
  home_shots_on_target: number | null;
  away_shots_on_target: number | null;
  home_possession: number | null;
  away_possession: number | null;
  home_corners: number | null;
  away_corners: number | null;
  home_fouls: number | null;
  away_fouls: number | null;
  home_yellow_cards: number | null;
  away_yellow_cards: number | null;
  home_red_cards: number | null;
  away_red_cards: number | null;
  home_xg: number | null;
  away_xg: number | null;
}

export interface MatchEvent {
  id: number;
  match_id: number;
  event_type: 'goal' | 'yellow_card' | 'red_card' | 'substitution' | 'corner' | 'shot';
  minute: number;
  player_id: number | null;
  player_name: string | null;
  team_id: number;
  detail: string | null;
}

// ===== PREDICTION TYPES =====
export interface GoalPrediction {
  expected_home_goals: number;
  expected_away_goals: number;
  expected_total_goals: number;
  distribution: Record<string, number>;
  probabilities: {
    over_05: number;
    over_15: number;
    over_25: number;
    over_35: number;
    under_05: number;
    under_15: number;
    under_25: number;
    under_35: number;
    btts_yes: number;
    btts_no: number;
    home_win: number;
    draw: number;
    away_win: number;
  };
}

export interface CornerPrediction {
  expected_home_corners: number;
  expected_away_corners: number;
  expected_total_corners: number;
  probabilities: {
    over_75: number;
    over_85: number;
    over_95: number;
    over_105: number;
    over_115: number;
  };
}

export interface CardPrediction {
  expected_home_cards: number;
  expected_away_cards: number;
  expected_total_cards: number;
  probabilities: {
    over_25: number;
    over_35: number;
    over_45: number;
    over_55: number;
  };
}

export interface PlayerShotPrediction {
  player_id: number;
  player_name: string;
  expected_shots: number;
  expected_shots_on_target: number;
  probabilities: {
    over_05: number;
    over_15: number;
    over_25: number;
    over_35: number;
  };
  status: 'OK' | 'INSUFFICIENT_DATA';
}

export interface Prediction {
  id: number;
  match_id: number;
  model_name: string;
  model_version: string;
  feature_version: string;
  goals: GoalPrediction;
  corners: CornerPrediction;
  cards: CardPrediction;
  players: PlayerShotPrediction[];
  created_at: string;
  data_quality: 'HIGH' | 'MEDIUM' | 'LOW' | 'INSUFFICIENT';
  sample_size: number;
}

// ===== ANALYSIS TYPES =====
export interface TeamForm {
  team_id: number;
  team_name: string;
  goals_avg_last_5: number;
  goals_avg_last_10: number;
  conceded_avg_last_5: number;
  conceded_avg_last_10: number;
  shots_avg: number;
  corners_avg: number;
  cards_avg: number;
  wins: number;
  draws: number;
  losses: number;
  form_last_5: string;
}

export interface H2HStats {
  total_matches: number;
  home_wins: number;
  draws: number;
  away_wins: number;
  avg_goals: number;
  avg_corners: number;
  avg_cards: number;
  last_5_results: string[];
}

export interface AIAnalysis {
  match_id: number;
  interpretation: string;
  key_factors: string[];
  risks: string[];
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  data_notes: string[];
  generated_at: string;
  model_used: string;
}

export interface MatchAnalysis {
  match: Match;
  statistics: MatchStatistics | null;
  home_form: TeamForm;
  away_form: TeamForm;
  h2h: H2HStats;
  prediction: Prediction | null;
  ai_analysis: AIAnalysis | null;
}

// ===== DASHBOARD TYPES =====
export interface DashboardData {
  upcoming_matches: Match[];
  recent_matches: Match[];
  total_competitions: number;
  total_teams: number;
  total_players: number;
  total_referees: number;
  last_updated: string;
}

// ===== API RESPONSE TYPES =====
export interface ApiResponse<T> {
  data: T;
  meta?: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

export interface DataQuality {
  level: 'HIGH' | 'MEDIUM' | 'LOW' | 'INSUFFICIENT';
  sample_size: number;
  last_updated: string;
  model_version: string;
  feature_version: string;
  notes: string[];
}
