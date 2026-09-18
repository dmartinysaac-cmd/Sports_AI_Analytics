import { useTeams } from '../hooks/useQueries';
import { Users, MapPin, Calendar } from 'lucide-react';

export default function Teams() {
  const { data: teams, isLoading } = useTeams();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {teams?.map((team) => (
          <div key={team.id} className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-emerald-500/30 transition-all duration-200">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 rounded-xl flex items-center justify-center">
                <span className="text-xl font-bold text-emerald-400">{team.short_name}</span>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white">{team.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <MapPin className="w-3 h-3 text-gray-500" />
                  <span className="text-xs text-gray-400">{team.country}</span>
                </div>
                {team.founded && (
                  <div className="flex items-center gap-2 mt-1">
                    <Calendar className="w-3 h-3 text-gray-500" />
                    <span className="text-xs text-gray-400">Fundado: {team.founded}</span>
                  </div>
                )}
                {team.stadium && (
                  <p className="text-xs text-gray-500 mt-2">🏟️ {team.stadium}</p>
                )}
              </div>
            </div>
            {team.aliases.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-800">
                <p className="text-xs text-gray-500 mb-1">Alias conocidos:</p>
                <div className="flex flex-wrap gap-1">
                  {team.aliases.map((alias, i) => (
                    <span key={i} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">
                      {alias}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {!teams?.length && (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No hay equipos disponibles</p>
        </div>
      )}
    </div>
  );
}
