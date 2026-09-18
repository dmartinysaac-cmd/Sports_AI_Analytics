import { useParams, Link } from 'react-router-dom';
import { useMatchAnalysis } from '../hooks/useQueries';
import { format } from 'date-fns';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
  PieChart, Pie, Cell
} from 'recharts';
import {
  ArrowLeft, Target, Activity, AlertTriangle, Brain, TrendingUp,
  Shield, Users, Award, Info
} from 'lucide-react';

const COLORS = ['#10b981', '#06b6d4', '#8b5cf6', '#f59e0b', '#ef4444', '#6366f1'];

function QualityBadge({ quality }: { quality: string }) {
  const colors: Record<string, string> = {
    HIGH: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    LOW: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    INSUFFICIENT: 'bg-red-500/10 text-red-400 border-red-500/20',
  };
  return (
    <span className={`text-xs px-2 py-1 rounded-full border ${colors[quality] || colors.MEDIUM}`}>
      Calidad: {quality}
    </span>
  );
}

function FormBadge({ form }: { form: string }) {
  return (
    <div className="flex gap-1">
      {form.split('').map((r, i) => (
        <span
          key={i}
          className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold ${
            r === 'W' ? 'bg-emerald-500/20 text-emerald-400' :
            r === 'D' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-red-500/20 text-red-400'
          }`}
        >
          {r}
        </span>
      ))}
    </div>
  );
}

function StatBar({ label, home, away, homeVal, awayVal }: { label: string; home: number; away: number; homeVal: string; awayVal: string }) {
  const total = home + away || 1;
  const homePct = (home / total) * 100;
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-white font-medium">{homeVal}</span>
        <span className="text-gray-400 text-xs">{label}</span>
        <span className="text-white font-medium">{awayVal}</span>
      </div>
      <div className="flex h-2 rounded-full overflow-hidden bg-gray-800">
        <div className="bg-emerald-500 transition-all" style={{ width: `${homePct}%` }} />
        <div className="bg-cyan-500 transition-all" style={{ width: `${100 - homePct}%` }} />
      </div>
    </div>
  );
}

export default function MatchDetail() {
  const { id } = useParams<{ id: string }>();
  const matchId = parseInt(id || '0');
  const { data: analysis, isLoading } = useMatchAnalysis(matchId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Partido no encontrado</p>
        <Link to="/matches" className="text-emerald-400 mt-2 inline-block">Volver a partidos</Link>
      </div>
    );
  }

  const { match, statistics, home_form, away_form, h2h, prediction, ai_analysis } = analysis;
  const date = new Date(match.match_date);

  // Chart data
  const goalDistribution = prediction?.goals?.distribution
    ? Object.entries(prediction.goals.distribution).map(([key, value]) => ({
        goals: key, probability: Math.round(value * 100),
      }))
    : [];

  const resultProb = prediction?.goals?.probabilities
    ? [
        { name: 'Local', value: Math.round(prediction.goals.probabilities.home_win * 100) },
        { name: 'Empate', value: Math.round(prediction.goals.probabilities.draw * 100) },
        { name: 'Visitante', value: Math.round(prediction.goals.probabilities.away_win * 100) },
      ]
    : [];

  const radarData = [
    { stat: 'Goles', home: Math.round((home_form?.goals_avg_last_5 || 0) * 20), away: Math.round((away_form?.goals_avg_last_5 || 0) * 20) },
    { stat: 'Tiros', home: Math.round((home_form?.shots_avg || 0) * 3), away: Math.round((away_form?.shots_avg || 0) * 3) },
    { stat: 'Córners', home: Math.round((home_form?.corners_avg || 0) * 8), away: Math.round((away_form?.corners_avg || 0) * 8) },
    { stat: 'Defensa', home: 100 - Math.round((home_form?.conceded_avg_last_5 || 0) * 30), away: 100 - Math.round((away_form?.conceded_avg_last_5 || 0) * 30) },
    { stat: 'Forma', home: Math.round((home_form?.wins || 0) * 5), away: Math.round((away_form?.wins || 0) * 5) },
  ];

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link to="/matches" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" /> Volver a partidos
      </Link>

      {/* Match Header */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8">
        <div className="text-center mb-4">
          <span className="text-sm text-gray-400">{match.competition_name} • {match.season_name}</span>
          <p className="text-xs text-gray-500 mt-1">{format(date, "dd 'de' MMMM yyyy, HH:mm")} • {match.venue_name}</p>
        </div>

        <div className="flex items-center justify-center gap-8">
          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-gradient-to-br from-emerald-500/20 to-emerald-500/5 rounded-2xl flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl font-bold text-emerald-400">{match.home_team_name.charAt(0)}</span>
            </div>
            <h2 className="text-xl font-bold text-white">{match.home_team_name}</h2>
            <p className="text-xs text-gray-500 mt-1">Local</p>
          </div>

          <div className="text-center px-6">
            {match.status === 'finished' ? (
              <div>
                <p className="text-4xl font-bold text-white">{match.home_score} - {match.away_score}</p>
                <p className="text-sm text-gray-400 mt-2">Final</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-emerald-400">VS</p>
                <p className="text-sm text-gray-400 mt-2">{format(date, 'HH:mm')}</p>
              </div>
            )}
          </div>

          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-500/20 to-cyan-500/5 rounded-2xl flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl font-bold text-cyan-400">{match.away_team_name.charAt(0)}</span>
            </div>
            <h2 className="text-xl font-bold text-white">{match.away_team_name}</h2>
            <p className="text-xs text-gray-500 mt-1">Visitante</p>
          </div>
        </div>

        {match.referee_name && (
          <div className="text-center mt-4 pt-4 border-t border-gray-800">
            <span className="text-sm text-gray-400">Árbitro: <span className="text-white">{match.referee_name}</span></span>
          </div>
        )}
      </div>

      {/* Data Quality */}
      {prediction && (
        <div className="flex items-center gap-4 bg-gray-900 border border-gray-800 rounded-xl p-4">
          <QualityBadge quality={prediction.data_quality} />
          <span className="text-xs text-gray-400">Modelo: {prediction.model_name} v{prediction.model_version}</span>
          <span className="text-xs text-gray-400">Muestra: {prediction.sample_size} partidos</span>
          <span className="text-xs text-gray-400">Features: v{prediction.feature_version}</span>
        </div>
      )}

      {/* Form & H2H */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Home Form */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-emerald-400 mb-3">{home_form?.team_name} - Forma</h3>
          <FormBadge form={home_form?.form_last_5 || 'WWDLW'} />
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-400">Goles/prom (últ. 5)</span><span className="text-white">{home_form?.goals_avg_last_5?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Goles/prom (últ. 10)</span><span className="text-white">{home_form?.goals_avg_last_10?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Recibidos/prom</span><span className="text-white">{home_form?.conceded_avg_last_5?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Tiros/prom</span><span className="text-white">{home_form?.shots_avg?.toFixed(1)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Córners/prom</span><span className="text-white">{home_form?.corners_avg?.toFixed(1)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">V/E/D</span><span className="text-white">{home_form?.wins}/{home_form?.draws}/{home_form?.losses}</span></div>
          </div>
        </div>

        {/* H2H */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-purple-400 mb-3">Historial H2H</h3>
          <div className="text-center mb-4">
            <p className="text-2xl font-bold text-white">{h2h?.total_matches}</p>
            <p className="text-xs text-gray-400">partidos jugados</p>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-400">Victorias local</span><span className="text-white">{h2h?.home_wins}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Empates</span><span className="text-white">{h2h?.draws}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Victorias visitante</span><span className="text-white">{h2h?.away_wins}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Goles promedio</span><span className="text-white">{h2h?.avg_goals?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Córners promedio</span><span className="text-white">{h2h?.avg_corners?.toFixed(1)}</span></div>
          </div>
          <div className="mt-4 pt-3 border-t border-gray-800">
            <p className="text-xs text-gray-500 mb-2">Últimos resultados:</p>
            <div className="space-y-1">
              {h2h?.last_5_results?.slice(0, 3).map((r, i) => (
                <p key={i} className="text-xs text-gray-400">{r}</p>
              ))}
            </div>
          </div>
        </div>

        {/* Away Form */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-cyan-400 mb-3">{away_form?.team_name} - Forma</h3>
          <FormBadge form={away_form?.form_last_5 || 'WDLWW'} />
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-400">Goles/prom (últ. 5)</span><span className="text-white">{away_form?.goals_avg_last_5?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Goles/prom (últ. 10)</span><span className="text-white">{away_form?.goals_avg_last_10?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Recibidos/prom</span><span className="text-white">{away_form?.conceded_avg_last_5?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Tiros/prom</span><span className="text-white">{away_form?.shots_avg?.toFixed(1)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Córners/prom</span><span className="text-white">{away_form?.corners_avg?.toFixed(1)}</span></div>
            <div className="flex justify-between"><span className="text-gray-400">V/E/D</span><span className="text-white">{away_form?.wins}/{away_form?.draws}/{away_form?.losses}</span></div>
          </div>
        </div>
      </div>

      {/* Statistics Comparison */}
      {statistics && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            Estadísticas del Partido
          </h3>
          <StatBar label="Tiros" home={statistics.home_shots || 0} away={statistics.away_shots || 0} homeVal={String(statistics.home_shots)} awayVal={String(statistics.away_shots)} />
          <StatBar label="Tiros al arco" home={statistics.home_shots_on_target || 0} away={statistics.away_shots_on_target || 0} homeVal={String(statistics.home_shots_on_target)} awayVal={String(statistics.away_shots_on_target)} />
          <StatBar label="Posesión %" home={statistics.home_possession || 0} away={statistics.away_possession || (100 - (statistics.home_possession || 0))} homeVal={`${statistics.home_possession}%`} awayVal={`${statistics.away_possession || 100 - (statistics.home_possession || 0)}%`} />
          <StatBar label="Córners" home={statistics.home_corners || 0} away={statistics.away_corners || 0} homeVal={String(statistics.home_corners)} awayVal={String(statistics.away_corners)} />
          <StatBar label="Faltas" home={statistics.home_fouls || 0} away={statistics.away_fouls || 0} homeVal={String(statistics.home_fouls)} awayVal={String(statistics.away_fouls)} />
          <StatBar label="xG" home={Math.round((statistics.home_xg || 0) * 10)} away={Math.round((statistics.away_xg || 0) * 10)} homeVal={(statistics.home_xg || 0).toFixed(2)} awayVal={(statistics.away_xg || 0).toFixed(2)} />
        </div>
      )}

      {/* Predictions */}
      {prediction && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-emerald-400" />
            Predicciones Estadísticas
          </h3>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Goals Prediction */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h4 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" /> Predicción de Goles
              </h4>
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="text-center bg-gray-800/50 rounded-lg p-3">
                  <p className="text-xl font-bold text-emerald-400">{prediction.goals.expected_home_goals.toFixed(2)}</p>
                  <p className="text-xs text-gray-400">xG Local</p>
                </div>
                <div className="text-center bg-gray-800/50 rounded-lg p-3">
                  <p className="text-xl font-bold text-white">{prediction.goals.expected_total_goals.toFixed(2)}</p>
                  <p className="text-xs text-gray-400">Total</p>
                </div>
                <div className="text-center bg-gray-800/50 rounded-lg p-3">
                  <p className="text-xl font-bold text-cyan-400">{prediction.goals.expected_away_goals.toFixed(2)}</p>
                  <p className="text-xs text-gray-400">xG Visitante</p>
                </div>
              </div>

              {/* Goal Distribution Chart */}
              <div className="h-40">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={goalDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="goals" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }} />
                    <Bar dataKey="probability" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Over/Under */}
              <div className="mt-4 grid grid-cols-2 gap-2">
                <div className="bg-gray-800/30 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-2">Over/Under Goles</p>
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs"><span className="text-gray-400">Over 1.5</span><span className="text-emerald-400">{(prediction.goals.probabilities.over_15 * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between text-xs"><span className="text-gray-400">Over 2.5</span><span className="text-emerald-400">{(prediction.goals.probabilities.over_25 * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between text-xs"><span className="text-gray-400">Over 3.5</span><span className="text-emerald-400">{(prediction.goals.probabilities.over_35 * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between text-xs"><span className="text-gray-400">BTTS</span><span className="text-cyan-400">{(prediction.goals.probabilities.btts_yes * 100).toFixed(0)}%</span></div>
                  </div>
                </div>
                <div className="bg-gray-800/30 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-2">Resultado</p>
                  <div className="h-28">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={resultProb} cx="50%" cy="50%" innerRadius={25} outerRadius={45} dataKey="value" label={({ name, value }) => `${name} ${value}%`}>
                          {resultProb.map((_, index) => (
                            <Cell key={index} fill={COLORS[index]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', fontSize: '12px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>

            {/* Corners & Cards */}
            <div className="space-y-4">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h4 className="text-sm font-semibold text-white mb-4">🎯 Predicción de Córners</h4>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-lg font-bold text-emerald-400">{prediction.corners.expected_home_corners.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Local</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-lg font-bold text-white">{prediction.corners.expected_total_corners.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Total</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-lg font-bold text-cyan-400">{prediction.corners.expected_away_corners.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Visitante</p>
                  </div>
                </div>
                <div className="space-y-2">
                  {Object.entries(prediction.corners.probabilities).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-xs text-gray-400">Over {key.replace('over_', '').replace(/(\d)(\d)/, '$1.$2')}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
                          <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${value * 100}%` }} />
                        </div>
                        <span className="text-xs text-cyan-400 w-10 text-right">{(value * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h4 className="text-sm font-semibold text-white mb-4">🟨 Predicción de Tarjetas</h4>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-lg font-bold text-yellow-400">{prediction.cards.expected_home_cards.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Local</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-lg font-bold text-white">{prediction.cards.expected_total_cards.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Total</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-lg font-bold text-orange-400">{prediction.cards.expected_away_cards.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Visitante</p>
                  </div>
                </div>
                <div className="space-y-2">
                  {Object.entries(prediction.cards.probabilities).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-xs text-gray-400">Over {key.replace('over_', '').replace(/(\d)(\d)/, '$1.$2')}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
                          <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${value * 100}%` }} />
                        </div>
                        <span className="text-xs text-yellow-400 w-10 text-right">{(value * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Player Shots */}
          {prediction.players && prediction.players.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h4 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Users className="w-4 h-4 text-purple-400" /> Tiros de Jugadores
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-800">
                      <th className="text-left py-2 text-gray-400 font-medium">Jugador</th>
                      <th className="text-center py-2 text-gray-400 font-medium">xTiros</th>
                      <th className="text-center py-2 text-gray-400 font-medium">xSOT</th>
                      <th className="text-center py-2 text-gray-400 font-medium">O0.5</th>
                      <th className="text-center py-2 text-gray-400 font-medium">O1.5</th>
                      <th className="text-center py-2 text-gray-400 font-medium">O2.5</th>
                      <th className="text-center py-2 text-gray-400 font-medium">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {prediction.players.map((p) => (
                      <tr key={p.player_id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                        <td className="py-2.5 text-white">{p.player_name}</td>
                        <td className="py-2.5 text-center text-emerald-400">{p.expected_shots.toFixed(1)}</td>
                        <td className="py-2.5 text-center text-cyan-400">{p.expected_shots_on_target.toFixed(1)}</td>
                        <td className="py-2.5 text-center text-gray-300">{(p.probabilities.over_05 * 100).toFixed(0)}%</td>
                        <td className="py-2.5 text-center text-gray-300">{(p.probabilities.over_15 * 100).toFixed(0)}%</td>
                        <td className="py-2.5 text-center text-gray-300">{(p.probabilities.over_25 * 100).toFixed(0)}%</td>
                        <td className="py-2.5 text-center">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            p.status === 'OK' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-yellow-500/10 text-yellow-400'
                          }`}>
                            {p.status === 'OK' ? '✓' : '⚠ Datos insuf.'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Radar Chart */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Award className="w-5 h-5 text-emerald-400" />
          Comparación de Equipos
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="stat" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <PolarRadiusAxis tick={{ fill: '#6b7280', fontSize: 10 }} />
              <Radar name={home_form?.team_name} dataKey="home" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
              <Radar name={away_form?.team_name} dataKey="away" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.2} />
              <Legend />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Analysis */}
      {ai_analysis && (
        <div className="bg-gradient-to-br from-purple-500/5 to-indigo-500/5 border border-purple-500/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            Análisis de Qwen AI
            <span className="text-xs bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded-full border border-purple-500/20">
              {ai_analysis.model_used}
            </span>
          </h3>

          <div className="prose prose-inverse max-w-none">
            <p className="text-gray-300 text-sm leading-relaxed">{ai_analysis.interpretation}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-gray-900/50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-emerald-400 mb-2 flex items-center gap-1">
                <TrendingUp className="w-4 h-4" /> Factores Clave
              </h4>
              <ul className="space-y-1">
                {ai_analysis.key_factors.map((f, i) => (
                  <li key={i} className="text-xs text-gray-400">• {f}</li>
                ))}
              </ul>
            </div>
            <div className="bg-gray-900/50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-orange-400 mb-2 flex items-center gap-1">
                <AlertTriangle className="w-4 h-4" /> Riesgos
              </h4>
              <ul className="space-y-1">
                {ai_analysis.risks.map((r, i) => (
                  <li key={i} className="text-xs text-gray-400">• {r}</li>
                ))}
              </ul>
            </div>
            <div className="bg-gray-900/50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-cyan-400 mb-2 flex items-center gap-1">
                <Info className="w-4 h-4" /> Notas de Datos
              </h4>
              <ul className="space-y-1">
                {ai_analysis.data_notes.map((n, i) => (
                  <li key={i} className="text-xs text-gray-400">• {n}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-800 flex items-center justify-between">
            <span className={`text-xs px-2 py-1 rounded-full border ${
              ai_analysis.confidence_level === 'HIGH' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
              ai_analysis.confidence_level === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
              'bg-red-500/10 text-red-400 border-red-500/20'
            }`}>
              Confianza: {ai_analysis.confidence_level}
            </span>
            <span className="text-xs text-gray-500">
              Generado: {new Date(ai_analysis.generated_at).toLocaleString('es-ES')}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
