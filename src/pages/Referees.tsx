import { useReferees } from '../hooks/useQueries';
import { Shield, Search } from 'lucide-react';
import { useState } from 'react';

export default function Referees() {
  const { data: referees, isLoading } = useReferees();
  const [search, setSearch] = useState('');

  const filtered = referees?.filter(r =>
    search === '' || r.name.toLowerCase().includes(search.toLowerCase())
  ) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          placeholder="Buscar árbitro..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-white text-sm focus:outline-none focus:border-emerald-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((ref) => (
          <div key={ref.id} className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-yellow-500/30 transition-all">
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-500/20 to-orange-500/20 rounded-xl flex items-center justify-center">
                <Shield className="w-6 h-6 text-yellow-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">{ref.name}</h3>
                {ref.nationality && (
                  <p className="text-xs text-gray-400">{ref.nationality}</p>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Partidos</span>
                <span className="text-sm font-semibold text-white">{ref.matches_total}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">🟨 Promedio/partido</span>
                <span className="text-sm font-semibold text-yellow-400">{ref.avg_yellow_cards.toFixed(1)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">🟥 Promedio/partido</span>
                <span className="text-sm font-semibold text-red-400">{ref.avg_red_cards.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Faltas promedio</span>
                <span className="text-sm font-semibold text-orange-400">{ref.avg_fouls.toFixed(1)}</span>
              </div>
            </div>

            {/* Visual indicator */}
            <div className="mt-4 pt-3 border-t border-gray-800">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Severidad:</span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      ref.avg_yellow_cards > 4.5 ? 'bg-red-500' :
                      ref.avg_yellow_cards > 3.5 ? 'bg-yellow-500' :
                      'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, (ref.avg_yellow_cards / 6) * 100)}%` }}
                  />
                </div>
                <span className="text-xs text-gray-400">
                  {ref.avg_yellow_cards > 4.5 ? 'Alta' : ref.avg_yellow_cards > 3.5 ? 'Media' : 'Baja'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {!filtered.length && (
        <div className="text-center py-12">
          <Shield className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No se encontraron árbitros</p>
        </div>
      )}
    </div>
  );
}
