import { useDashboard, useMatches, useCompetitions } from '../hooks/useQueries';
import { Link } from 'react-router-dom';
import { Calendar, Trophy, Users, UserCircle, Shield, TrendingUp, Clock, ArrowRight } from 'lucide-react';
import { format } from 'date-fns';

function StatCard({ icon: Icon, label, value, color, link }: { icon: any; label: string; value: number | string; color: string; link?: string }) {
  const content = (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {link && <ArrowRight className="w-4 h-4 text-gray-500" />}
      </div>
      <p className="text-3xl font-bold text-white mb-1">{value}</p>
      <p className="text-sm text-gray-400">{label}</p>
    </div>
  );
  return link ? <Link to={link}>{content}</Link> : content;
}

function MatchCard({ match }: { match: any }) {
  const isFinished = match.status === 'finished';
  const date = new Date(match.match_date);

  return (
    <Link
      to={`/matches/${match.id}`}
      className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-emerald-500/30 transition-all duration-200 group"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-gray-500 font-medium">{match.competition_name}</span>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          isFinished ? 'bg-gray-800 text-gray-400' : 'bg-emerald-500/10 text-emerald-400'
        }`}>
          {isFinished ? 'Finalizado' : 'Próximo'}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="font-semibold text-white text-sm">{match.home_team_name}</p>
          <p className="text-xs text-gray-500 mt-0.5">Local</p>
        </div>
        <div className="px-4">
          {isFinished ? (
            <div className="text-center">
              <p className="text-xl font-bold text-white">{match.home_score} - {match.away_score}</p>
              <p className="text-xs text-gray-500 mt-1">Final</p>
            </div>
          ) : (
            <div className="text-center">
              <p className="text-sm font-medium text-emerald-400">VS</p>
              <p className="text-xs text-gray-500 mt-1">{format(date, 'HH:mm')}</p>
            </div>
          )}
        </div>
        <div className="flex-1 text-right">
          <p className="font-semibold text-white text-sm">{match.away_team_name}</p>
          <p className="text-xs text-gray-500 mt-0.5">Visitante</p>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-gray-800 flex items-center justify-between">
        <span className="text-xs text-gray-500">{format(date, 'dd MMM yyyy', { locale: undefined })}</span>
        <span className="text-xs text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity">
          Ver análisis →
        </span>
      </div>
    </Link>
  );
}

export default function Dashboard() {
  const { data: dashboard, isLoading: dashLoading } = useDashboard();
  const { data: matches } = useMatches();
  const { data: competitions } = useCompetitions();

  if (dashLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const upcomingMatches = matches?.filter(m => m.status === 'scheduled') || [];
  const recentMatches = matches?.filter(m => m.status === 'finished') || [];

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Trophy} label="Competiciones" value={dashboard?.total_competitions || competitions?.length || 0} color="bg-gradient-to-br from-yellow-500 to-orange-500" link="/statistics" />
        <StatCard icon={Users} label="Equipos" value={dashboard?.total_teams || 0} color="bg-gradient-to-br from-blue-500 to-indigo-500" link="/teams" />
        <StatCard icon={UserCircle} label="Jugadores" value={dashboard?.total_players || 0} color="bg-gradient-to-br from-purple-500 to-pink-500" link="/players" />
        <StatCard icon={Shield} label="Árbitros" value={dashboard?.total_referees || 0} color="bg-gradient-to-br from-emerald-500 to-teal-500" link="/referees" />
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">Análisis Inteligente</h3>
            <p className="text-sm text-gray-400">Modelos estadísticos Poisson + interpretación con Qwen AI</p>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <span className="text-sm text-emerald-400 font-medium">Modelo activo</span>
          </div>
        </div>
      </div>

      {/* Upcoming Matches */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-emerald-400" />
            Próximos Partidos
          </h3>
          <Link to="/matches" className="text-sm text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
            Ver todos <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {upcomingMatches.slice(0, 3).map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
        </div>
      </div>

      {/* Recent Results */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-cyan-400" />
            Resultados Recientes
          </h3>
          <Link to="/matches" className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
            Ver todos <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentMatches.slice(0, 3).map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-white">Scraping Engine</span>
          </div>
          <p className="text-xs text-gray-400">Scrapling activo • Última ejecución: hace 2h</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-white">Prediction Engine</span>
          </div>
          <p className="text-xs text-gray-400">Poisson v2.1 • 156 partidos analizados</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-white">Qwen AI</span>
          </div>
          <p className="text-xs text-gray-400">qwen-2.5-72b • Interpretaciones activas</p>
        </div>
      </div>
    </div>
  );
}
