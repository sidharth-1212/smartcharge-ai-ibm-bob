import React, { useState } from 'react';
import { setChargingMode } from '../services/api';

const BobController = ({ decision, onModeChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [override, setOverride] = useState(null); // Tracks the 15-second manual lock

  const handleModeChange = async (mode) => {
    setLoading(true);
    setError(null);
    try {
      await setChargingMode(mode);
      
      // Optimistically update the UI instantly (no 5-second polling delay!)
      setOverride({
        recommended_mode: mode,
        confidence: 1.0,
        reasoning: `👨‍💻 MANUAL OVERRIDE ENGAGED: User forced system into ${mode}. AI load balancing temporarily suspended for 15 seconds.`,
        estimated_cost: 0.0,
        estimated_time_minutes: 0,
        timestamp: new Date().toISOString()
      });

      // Let AI take the wheel back after 15 seconds
      setTimeout(() => setOverride(null), 15000);

      if (onModeChange) onModeChange(mode);
    } catch (err) {
      setError(err.message);
      console.error('Failed to change mode:', err);
    } finally {
      setLoading(false);
    }
  };

  const getModeColor = (mode) => {
    switch (mode) {
      case 'FAST_CHARGE': return 'bg-red-500';
      case 'ECO_MODE': return 'bg-green-500';
      case 'PAUSED': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getModeIcon = (mode) => {
    switch (mode) {
      case 'FAST_CHARGE': return '⚡';
      case 'ECO_MODE': return '🌱';
      case 'PAUSED': return '⏸️';
      default: return '❓';
    }
  };

  // Use the override if active, otherwise fallback to AI live polling
  const displayDecision = override || decision;

  if (!displayDecision) {
    return (
      <div className="card">
        <h2 className="card-title">AI Decision Engine</h2>
        <div className="text-center text-gray-400 py-8">
          Waiting for AI decision...
        </div>
      </div>
    );
  }

  return (
    <div className="card transition-all duration-300">
      <h2 className="card-title flex items-center gap-2">
        <span>🤖</span>
        AI Decision Engine
      </h2>

      {/* Current Mode */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Current Mode</span>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getModeColor(displayDecision.recommended_mode)} text-white flex items-center gap-2 transition-colors duration-300`}>
            <span>{getModeIcon(displayDecision.recommended_mode)}</span>
            {displayDecision.recommended_mode}
          </span>
        </div>
      </div>

      {/* Confidence Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Confidence</span>
          <span className="text-lg font-bold text-white">
            {(displayDecision.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className={`${override ? 'bg-purple-500' : 'bg-blue-500'} h-2 rounded-full transition-all duration-500`}
            style={{ width: `${displayDecision.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Reasoning */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Reasoning</h3>
        <p className={`text-white text-sm leading-relaxed p-3 rounded-lg transition-colors duration-300 ${override ? 'bg-purple-900/40 border border-purple-500/30' : 'bg-slate-900/50 border border-transparent'}`}>
          {displayDecision.reasoning}
        </p>
      </div>

      {/* Manual Override Buttons */}
      <div className="border-t border-slate-700 pt-4">
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Manual Override</h3>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => handleModeChange('FAST_CHARGE')}
            disabled={loading || displayDecision.recommended_mode === 'FAST_CHARGE'}
            className="btn-danger text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⚡ Fast
          </button>
          <button
            onClick={() => handleModeChange('ECO_MODE')}
            disabled={loading || displayDecision.recommended_mode === 'ECO_MODE'}
            className="btn-success text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🌱 Eco
          </button>
          <button
            onClick={() => handleModeChange('PAUSED')}
            disabled={loading || displayDecision.recommended_mode === 'PAUSED'}
            className="btn-warning text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⏸️ Pause
          </button>
        </div>
      </div>
    </div>
  );
};

export default BobController;