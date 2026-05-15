import React, { useEffect, useRef } from 'react';

const EventLog = ({ decisions = [] }) => {
  const logEndRef = useRef(null);

  // Ensure decisions is always an array
  const decisionsArray = Array.isArray(decisions) ? decisions : [];

  useEffect(() => {
    // Auto-scroll to bottom when new decisions arrive
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [decisionsArray]);

  const getModeColor = (mode) => {
    switch (mode) {
      case 'FAST_CHARGE':
        return 'text-red-400';
      case 'ECO_MODE':
        return 'text-green-400';
      case 'PAUSED':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
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

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (!decisions || decisions.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title">Decision Log</h2>
        <div className="text-center text-gray-400 py-8">
          No decisions yet...
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="card-title flex items-center justify-between">
        <span>📋 Decision Log</span>
        <span className="text-sm font-normal text-gray-400">
          Last {decisionsArray.length} decisions
        </span>
      </h2>

      <div className="space-y-2 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
        {decisionsArray.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>No decisions yet</p>
            <p className="text-sm mt-2">Waiting for backend connection...</p>
          </div>
        ) : (
          decisionsArray.map((decision, index) => (
          <div
            key={decision.id || index}
            className="bg-slate-900/50 p-3 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xl">{getModeIcon(decision.recommended_mode)}</span>
                <span className={`font-semibold ${getModeColor(decision.recommended_mode)}`}>
                  {decision.recommended_mode}
                </span>
              </div>
              <span className="text-xs text-gray-500">
                {formatTime(decision.timestamp)}
              </span>
            </div>
            
            <p className="text-sm text-gray-300 leading-relaxed">
              {decision.reasoning}
            </p>
            
            <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
              <span>
                Confidence: <span className="text-blue-400 font-semibold">
                  {(decision.confidence * 100).toFixed(0)}%
                </span>
              </span>
              {decision.estimated_cost && (
                <span>
                  Cost: <span className="text-green-400 font-semibold">
                    ${decision.estimated_cost.toFixed(2)}
                  </span>
                </span>
              )}
            </div>
          </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #1e293b;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #475569;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #64748b;
        }
      `}</style>
    </div>
  );
};

export default EventLog;

// Made with Bob
