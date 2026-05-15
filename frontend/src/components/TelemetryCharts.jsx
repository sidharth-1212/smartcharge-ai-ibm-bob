import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const TelemetryCharts = ({ history }) => {
  // Ensure history is an array
  const historyArray = Array.isArray(history) ? history : [];
  
  if (historyArray.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title">Telemetry History</h2>
        <div className="text-center text-gray-400 py-8">
          Waiting for historical data...
        </div>
      </div>
    );
  }

  // Prepare data for charts
  // 1. Reverse the array so time flows left-to-right (oldest to newest)
  // 2. Slice to keep the last 50 points
  // 3. Map the data safely handling both flat and nested JSON responses
  const chartData = [...historyArray]
    .reverse()
    .slice(-50)
    .map((item) => ({
      // Add seconds so the 5-second simulator ticks actually show up!
      time: new Date(item.timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }),
      solar: item.solar?.generation_kw ?? item.solar_generation_kw ?? 0,
      grid: item.grid?.price_per_kwh ?? item.grid_price_per_kwh ?? 0,
      battery: item.ev_battery?.soc_percent ?? item.battery_soc_percent ?? 0,
    }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 p-3 rounded-lg shadow-lg">
          <p className="text-white font-semibold mb-2">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value.toFixed(2)} {entry.unit}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <h2 className="card-title">📊 Telemetry History</h2>

      {/* Solar Generation Chart */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-300 mb-3">
          ☀️ Solar Generation
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="time"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              label={{ value: 'kW', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: '#94a3b8' }} />
            <Line
              type="monotone"
              dataKey="solar"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              name="Solar"
              unit="kW"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Grid Price Chart */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-300 mb-3">
          ⚡ Grid Price
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="time"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              label={{ value: '$/kWh', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: '#94a3b8' }} />
            <Line
              type="monotone"
              dataKey="grid"
              stroke="#f97316"
              strokeWidth={2}
              dot={false}
              name="Grid Price"
              unit="$/kWh"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Battery SOC Chart */}
      <div>
        <h3 className="text-lg font-semibold text-gray-300 mb-3">
          🔋 Battery State of Charge
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="time"
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#94a3b8"
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
              label={{ value: '%', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: '#94a3b8' }} />
            <Line
              type="monotone"
              dataKey="battery"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              name="Battery SOC"
              unit="%"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TelemetryCharts;