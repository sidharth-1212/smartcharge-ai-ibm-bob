import React, { useState } from 'react';
import { setChargingMode } from '../services/api';

const BobController = ({ decision, onModeChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleModeChange = async (mode) => {
    setLoading(true);
    setError(null);
    try {
      await setChargingMode(mode);
      if (onModeChange) {
        onModeChange(mode);
      }
    } catch (err) {
      setError(err.message);
      console.error('Failed to change mode:', err);
    } finally {
      setLoading(false);
    }
  };

  const getModeColor = (mode) => {
    switch (mode) {
      case 'FAST_CHARGE':
        return 'bg-red-500';
      case 'ECO_MODE':
        return 'bg-green-500';
      case 'PAUSED':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getModeIcon = (mode) => {
    switch (mode) {
      case 'FAST_CHARGE':
        return '⚡';
      case 'ECO_MODE':
        return '🌱';
      case 'PAUSED':
        return '⏸️';
      default:
        return '❓';
    }
  };

  if (!decision) {
    return (
      <div className="card">
        <h2 className="card-title">Bob's Decision Engine</h2>
        <div className="text-center text-gray-400 py-8">
          Waiting for Bob's decision...
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-title flex items-center gap-2">
        <span>🤖</span>
        Bob's Decision Engine
      </h2>

      {/* Current Mode */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Current Mode</span>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getModeColor(decision.recommended_mode)} text-white flex items-center gap-2`}>
            <span>{getModeIcon(decision.recommended_mode)}</span>
            {decision.recommended_mode}
          </span>
        </div>
      </div>

      {/* Confidence Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Confidence</span>
          <span className="text-lg font-bold text-white">
            {(decision.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${decision.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Reasoning */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Reasoning</h3>
        <p className="text-white text-sm leading-relaxed bg-slate-900/50 p-3 rounded-lg">
          {decision.reasoning}
        </p>
      </div>

      {/* Estimated Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-slate-900/50 p-3 rounded-lg">
          <div className="text-xs text-gray-400 mb-1">Estimated Cost</div>
          <div className="text-lg font-bold text-green-400">
            ${decision.estimated_cost?.toFixed(2) || '0.00'}
          </div>
        </div>
        <div className="bg-slate-900/50 p-3 rounded-lg">
          <div className="text-xs text-gray-400 mb-1">Estimated Time</div>
          <div className="text-lg font-bold text-blue-400">
            {decision.estimated_time_minutes || 'N/A'} min
          </div>
        </div>
      </div>

      {/* Manual Override Buttons */}
      <div className="border-t border-slate-700 pt-4">
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Manual Override</h3>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => handleModeChange('FAST_CHARGE')}
            disabled={loading || decision.recommended_mode === 'FAST_CHARGE'}
            className="btn-danger text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⚡ Fast
          </button>
          <button
            onClick={() => handleModeChange('ECO_MODE')}
            disabled={loading || decision.recommended_mode === 'ECO_MODE'}
            className="btn-success text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🌱 Eco
          </button>
          <button
            onClick={() => handleModeChange('PAUSED')}
            disabled={loading || decision.recommended_mode === 'PAUSED'}
            className="btn-warning text-sm py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⏸️ Pause
          </button>
        </div>
        {error && (
          <div className="mt-2 text-xs text-red-400 text-center">
            {error}
          </div>
        )}
      </div>

      {/* Timestamp */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        Last updated: {new Date(decision.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default BobController;

// Made with Bob
