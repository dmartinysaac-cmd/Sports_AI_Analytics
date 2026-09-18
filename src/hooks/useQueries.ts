import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import type { Match, MatchAnalysis, Team, Player, Referee, Competition, DashboardData, Prediction } from '../types';

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: () => api.getDashboard(),
    staleTime: 60000,
  });
}

export function useMatches() {
  return useQuery<Match[]>({
    queryKey: ['matches'],
    queryFn: () => api.getMatches(),
    staleTime: 30000,
  });
}

export function useMatch(id: number) {
  return useQuery<Match>({
    queryKey: ['match', id],
    queryFn: () => api.getMatch(id),
    enabled: id > 0,
  });
}

export function useMatchAnalysis(id: number) {
  return useQuery<MatchAnalysis>({
    queryKey: ['match-analysis', id],
    queryFn: () => api.getMatchAnalysis(id),
    enabled: id > 0,
    staleTime: 60000,
  });
}

export function useTeams() {
  return useQuery<Team[]>({
    queryKey: ['teams'],
    queryFn: () => api.getTeams(),
  });
}

export function usePlayers() {
  return useQuery<Player[]>({
    queryKey: ['players'],
    queryFn: () => api.getPlayers(),
  });
}

export function useReferees() {
  return useQuery<Referee[]>({
    queryKey: ['referees'],
    queryFn: () => api.getReferees(),
  });
}

export function useCompetitions() {
  return useQuery<Competition[]>({
    queryKey: ['competitions'],
    queryFn: () => api.getCompetitions(),
  });
}

export function usePrediction(matchId: number) {
  return useQuery<Prediction>({
    queryKey: ['prediction', matchId],
    queryFn: () => api.getPrediction(matchId),
    enabled: matchId > 0,
  });
}
