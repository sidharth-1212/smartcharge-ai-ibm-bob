import React from 'react';
import PowerGauge from './PowerGauge';
import BobController from './BobController';
import EventLog from './EventLog';
import TelemetryCharts from './TelemetryCharts';
import Analytics from './Analytics';
import useTelemetry from '../hooks/useTelemetry';
import useDecisions from '../hooks/useDecisions';

const Dashboard = () => {
  const { telemetry, history: telemetryHistory, loading: telemetryLoading, error: telemetryError } = useTelemetry();
  const { decision, history: decisionHistory, loading: decisionLoading, error: decisionError } = useDecisions();

  const handleModeChange = (mode) => {
    console.log('Mode changed to:', mode);
    // The polling will automatically pick up the new mode
  };

  if (telemetryLoading && decisionLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Error Messages */}
      {(telemetryError || decisionError) && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4">
          <h3 className="text-red-400 font-semibold mb-2">⚠️ Connection Issues</h3>
          <p className="text-sm text-gray-300">
            {telemetryError && `Telemetry: ${telemetryError}`}
            {telemetryError && decisionError && ' | '}
            {decisionError && `Decisions: ${decisionError}`}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Make sure the backend server is running
          </p>
        </div>
      )}

      {/* Power Gauges Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <PowerGauge
          label="Solar Generation"
          value={telemetry?.solar_generation_kw || 0}
          max={10}
          unit="kW"
          color="solar"
          icon="☀️"
        />
        <PowerGauge
          label="Grid Price"
          value={telemetry?.grid_price_per_kwh || 0}
          max={0.5}
          unit="$/kWh"
          color="grid"
          icon="⚡"
        />
        <PowerGauge
          label="Battery SOC"
          value={telemetry?.battery_soc_percent || 0}
          max={100}
          unit="%"
          color="battery"
          icon="🔋"
        />
      </div>

      {/* Bob Controller and Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BobController decision={decision} onModeChange={handleModeChange} />
        <Analytics />
      </div>

      {/* Event Log and Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EventLog decisions={decisionHistory} />
        <TelemetryCharts history={telemetryHistory} />
      </div>

      {/* Status Footer */}
      <div className="text-center text-xs text-gray-500 py-4">
        <div className="flex items-center justify-center gap-4">
          <span className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${telemetryError ? 'bg-red-500' : 'bg-green-500'} animate-pulse`}></span>
            Telemetry: {telemetryError ? 'Disconnected' : 'Connected'}
          </span>
          <span className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${decisionError ? 'bg-red-500' : 'bg-green-500'} animate-pulse`}></span>
            AI: {decisionError ? 'Disconnected' : 'Connected'}
          </span>
          <span>
            Last update: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

// Made with Bob
