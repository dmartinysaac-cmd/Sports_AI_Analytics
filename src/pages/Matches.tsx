import { useMatches } from '../hooks/useQueries';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { Calendar, Filter, Search } from 'lucide-react';
import { useState } from 'react';

export default function Matches() {
  const { data: matches, isLoading } = useMatches();
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredMatches = matches?.filter(m => {
    const matchesStatus = statusFilter === 'all' || m.status === statusFilter;
    const matchesSearch = searchTerm === '' ||
      m.home_team_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.away_team_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.competition_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  }) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Buscar equipo o competición..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
          />
        </div>
        <div className="flex gap-2">
          {['all', 'scheduled', 'finished'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                statusFilter === status
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-gray-900 text-gray-400 border border-gray-800 hover:border-gray-700'
              }`}
            >
              {status === 'all' ? 'Todos' : status === 'scheduled' ? 'Próximos' : 'Finalizados'}
            </button>
          ))}
        </div>
      </div>

      {/* Match List */}
      <div className="space-y-3">
        {filteredMatches.map((match) => {
          const date = new Date(match.match_date);
          const isFinished = match.status === 'finished';

          return (
            <Link
              key={match.id}
              to={`/matches/${match.id}`}
              className="block bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-emerald-500/30 transition-all duration-200 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  <div className="text-center min-w-[80px]">
                    <p className="text-xs text-gray-500 font-medium">{match.competition_name}</p>
                    <p className="text-xs text-gray-600 mt-0.5">{format(date, 'dd/MM/yyyy')}</p>
                    <p className="text-xs text-gray-600">{format(date, 'HH:mm')}</p>
                  </div>

                  <div className="flex-1 flex items-center justify-center gap-6">
                    <div className="text-right flex-1">
                      <p className="font-semibold text-white">{match.home_team_name}</p>
                    </div>

                    <div className="px-4 py-2 bg-gray-800 rounded-lg min-w-[80px] text-center">
                      {isFinished ? (
                        <p className="text-lg font-bold text-white">{match.home_score} - {match.away_score}</p>
                      ) : (
                        <p className="text-sm font-medium text-emerald-400">VS</p>
                      )}
                    </div>

                    <div className="flex-1">
                      <p className="font-semibold text-white">{match.away_team_name}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`text-xs px-3 py-1 rounded-full ${
                    isFinished ? 'bg-gray-800 text-gray-400' : 'bg-emerald-500/10 text-emerald-400'
                  }`}>
                    {isFinished ? 'Final' : 'Programado'}
                  </span>
                  {match.referee_name && (
                    <span className="text-xs text-gray-500 hidden lg:block">
                      Árbitro: {match.referee_name}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {filteredMatches.length === 0 && (
        <div className="text-center py-12">
          <Calendar className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No se encontraron partidos</p>
          <p className="text-sm text-gray-500 mt-1">Intenta cambiar los filtros de búsqueda</p>
        </div>
      )}
    </div>
  );
}
