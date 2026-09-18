import { useMatches, usePrediction } from '../hooks/useQueries';
import { Link } from 'react-router-dom';
import { Brain, Target, TrendingUp, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { useState } from 'react';

export default function Predictions() {
  const { data: matches } = useMatches();
  const [selectedMatch, setSelectedMatch] = useState<number>(1);
  const { data: prediction } = usePrediction(selectedMatch);

  const upcomingMatches = matches?.filter(m => m.status === 'scheduled') || [];

  return (
    <div className="space-y-6">
      {/* Info Banner */}
      <div className="bg-gradient-to-r from-purple-500/5 to-indigo-500/5 border border-purple-500/20 rounded-xl p-5">
        <div className="flex items-start gap-3">
          <Brain className="w-5 h-5 text-purple-400 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-white mb-1">Sistema de Predicción</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Las predicciones se generan usando un modelo Poisson bivariado que combina forma reciente del equipo,
              estadísticas H2H, rendimiento local/visitante, y datos del árbitro. Qwen AI proporciona interpretación
              contextual. <strong className="text-yellow-400">Nunca se inventan datos.</strong> Si la información es
              insuficiente, se indica explícitamente.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Match Selector */}
        <div className="lg:col-span-1">
          <h3 className="text-sm font-semibold text-white mb-3">Seleccionar Partido</h3>
          <div className="space-y-2">
            {(upcomingMatches.length > 0 ? upcomingMatches : matches?.slice(0, 5) || []).map((m) => (
              <button
                key={m.id}
                onClick={() => setSelectedMatch(m.id)}
                className={`w-full text-left p-4 rounded-xl border transition-all ${
                  selectedMatch === m.id
                    ? 'bg-emerald-500/10 border-emerald-500/30'
                    : 'bg-gray-900 border-gray-800 hover:border-gray-700'
                }`}
              >
                <p className="text-xs text-gray-500 mb-1">{m.competition_name}</p>
                <p className="text-sm text-white font-medium">{m.home_team_name} vs {m.away_team_name}</p>
                <p className="text-xs text-gray-400 mt-1">{new Date(m.match_date).toLocaleDateString('es-ES')}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Prediction Details */}
        <div className="lg:col-span-2 space-y-4">
          {prediction ? (
            <>
              {/* Data Quality */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-center gap-4">
                <div className={`w-3 h-3 rounded-full ${
                  prediction.data_quality === 'HIGH' ? 'bg-emerald-400' :
                  prediction.data_quality === 'MEDIUM' ? 'bg-yellow-400' :
                  prediction.data_quality === 'LOW' ? 'bg-orange-400' : 'bg-red-400'
                }`} />
                <div className="flex-1">
                  <p className="text-sm text-white">Calidad de datos: <span className="font-semibold">{prediction.data_quality}</span></p>
                  <p className="text-xs text-gray-400">Muestra: {prediction.sample_size} partidos • Modelo: {prediction.model_name} v{prediction.model_version}</p>
                </div>
              </div>

              {/* Goals */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4 text-emerald-400" /> Predicción de Goles
                </h4>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-2xl font-bold text-emerald-400">{prediction.goals.expected_home_goals.toFixed(2)}</p>
                    <p className="text-xs text-gray-400">xG Local</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-2xl font-bold text-white">{prediction.goals.expected_total_goals.toFixed(2)}</p>
                    <p className="text-xs text-gray-400">Total Esperado</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-3">
                    <p className="text-2xl font-bold text-cyan-400">{prediction.goals.expected_away_goals.toFixed(2)}</p>
                    <p className="text-xs text-gray-400">xG Visitante</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-400 mb-2">Probabilidades Over/Under</p>
                    {Object.entries(prediction.goals.probabilities).filter(([k]) => k.startsWith('over')).map(([key, val]) => (
                      <div key={key} className="flex justify-between text-xs mb-1">
                        <span className="text-gray-400">{key.replace('_', ' ').toUpperCase()}</span>
                        <span className="text-emerald-400">{(val * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 mb-2">Resultado Esperado</p>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Victoria Local</span>
                      <span className="text-emerald-400">{(prediction.goals.probabilities.home_win * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Empate</span>
                      <span className="text-yellow-400">{(prediction.goals.probabilities.draw * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">Victoria Visitante</span>
                      <span className="text-cyan-400">{(prediction.goals.probabilities.away_win * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-400">BTTS Sí</span>
                      <span className="text-purple-400">{(prediction.goals.probabilities.btts_yes * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Corners */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <h4 className="text-sm font-semibold text-white mb-3">🎯 Córners</h4>
                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div className="text-center bg-gray-800/50 rounded-lg p-2">
                    <p className="text-lg font-bold text-emerald-400">{prediction.corners.expected_home_corners.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Local</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-2">
                    <p className="text-lg font-bold text-white">{prediction.corners.expected_total_corners.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Total</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-2">
                    <p className="text-lg font-bold text-cyan-400">{prediction.corners.expected_away_corners.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Visitante</p>
                  </div>
                </div>
                {Object.entries(prediction.corners.probabilities).map(([k, v]) => (
                  <div key={k} className="flex justify-between text-xs mb-1">
                    <span className="text-gray-400">Over {k.replace('over_', '').replace(/(\d)(\d)/, '$1.$2')}</span>
                    <span className="text-cyan-400">{(v * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>

              {/* Cards */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <h4 className="text-sm font-semibold text-white mb-3">🟨 Tarjetas</h4>
                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div className="text-center bg-gray-800/50 rounded-lg p-2">
                    <p className="text-lg font-bold text-yellow-400">{prediction.cards.expected_home_cards.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Local</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-2">
                    <p className="text-lg font-bold text-white">{prediction.cards.expected_total_cards.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Total</p>
                  </div>
                  <div className="text-center bg-gray-800/50 rounded-lg p-2">
                    <p className="text-lg font-bold text-orange-400">{prediction.cards.expected_away_cards.toFixed(1)}</p>
                    <p className="text-xs text-gray-400">Visitante</p>
                  </div>
                </div>
                {Object.entries(prediction.cards.probabilities).map(([k, v]) => (
                  <div key={k} className="flex justify-between text-xs mb-1">
                    <span className="text-gray-400">Over {k.replace('over_', '').replace(/(\d)(\d)/, '$1.$2')}</span>
                    <span className="text-yellow-400">{(v * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>

              {/* Disclaimer */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 flex items-start gap-3">
                <Info className="w-4 h-4 text-gray-500 mt-0.5" />
                <p className="text-xs text-gray-500 leading-relaxed">
                  <strong>Nota importante:</strong> Estas predicciones son estimaciones estadísticas basadas en datos históricos.
                  No constituyen consejos de apuestas. Los modelos tienen incertidumbre inherente y los resultados reales
                  pueden variar significativamente. La calidad de los datos y el tamaño de muestra afectan la confiabilidad.
                </p>
              </div>
            </>
          ) : (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
              <Brain className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">Selecciona un partido para ver predicciones</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
