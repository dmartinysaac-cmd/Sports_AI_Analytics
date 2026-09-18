import { usePlayers } from '../hooks/useQueries';
import { UserCircle, Search } from 'lucide-react';
import { useState } from 'react';

export default function Players() {
  const { data: players, isLoading } = usePlayers();
  const [search, setSearch] = useState('');
  const [posFilter, setPosFilter] = useState('all');

  const filtered = players?.filter(p => {
    const matchSearch = search === '' || p.name.toLowerCase().includes(search.toLowerCase());
    const matchPos = posFilter === 'all' || p.position.toLowerCase() === posFilter.toLowerCase();
    return matchSearch && matchPos;
  }) || [];

  // Generate mock stats for display
  const playerStats = filtered.map(p => ({
    ...p,
    minutes: 800 + Math.floor(Math.random() * 1500),
    starts: 12 + Math.floor(Math.random() * 15),
    shots: 30 + Math.floor(Math.random() * 60),
    shots_on_target: 12 + Math.floor(Math.random() * 25),
    goals: 3 + Math.floor(Math.random() * 18),
    xg: (5 + Math.random() * 15).toFixed(1),
    cards: Math.floor(Math.random() * 6),
  }));

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
            placeholder="Buscar jugador..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-white text-sm focus:outline-none focus:border-emerald-500"
          />
        </div>
        <div className="flex gap-2">
          {['all', 'Forward', 'Midfielder', 'Defender', 'Goalkeeper'].map(pos => (
            <button
              key={pos}
              onClick={() => setPosFilter(pos)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                posFilter === pos
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-gray-900 text-gray-400 border border-gray-800 hover:border-gray-700'
              }`}
            >
              {pos === 'all' ? 'Todos' : pos}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-800/50">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Jugador</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Equipo</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">Pos</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">Min</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">Tit</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">Tiros</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">SOT</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">Goles</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">xG</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">🟨</th>
              </tr>
            </thead>
            <tbody>
              {playerStats.map((p) => (
                <tr key={p.id} className="border-t border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-purple-400">{p.name.charAt(0)}</span>
                      </div>
                      <div>
                        <p className="text-white font-medium">{p.name}</p>
                        {p.nationality && <p className="text-xs text-gray-500">{p.nationality}</p>}
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-gray-300">{p.team_name}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded">{p.position}</span>
                  </td>
                  <td className="py-3 px-4 text-center text-gray-300">{p.minutes}</td>
                  <td className="py-3 px-4 text-center text-gray-300">{p.starts}</td>
                  <td className="py-3 px-4 text-center text-emerald-400">{p.shots}</td>
                  <td className="py-3 px-4 text-center text-cyan-400">{p.shots_on_target}</td>
                  <td className="py-3 px-4 text-center text-white font-semibold">{p.goals}</td>
                  <td className="py-3 px-4 text-center text-yellow-400">{p.xg}</td>
                  <td className="py-3 px-4 text-center text-yellow-500">{p.cards}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {!filtered.length && (
        <div className="text-center py-12">
          <UserCircle className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No se encontraron jugadores</p>
        </div>
      )}
    </div>
  );
}
