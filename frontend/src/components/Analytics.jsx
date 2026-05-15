import React, { useState, useEffect } from 'react';
import { getAnalytics } from '../services/api';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await getAnalytics();
        setAnalytics(data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="card">
        <h2 className="card-title">📈 Analytics</h2>
        <div className="text-center text-gray-400 py-8">
          Loading analytics...
        </div>
      </div>
    );
  }

  const metrics = [
    {
      label: 'Cost Savings Today',
      value: `$${(analytics?.cost_savings_today || 0).toFixed(2)}`,
      icon: '💰',
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      description: 'Saved vs. peak pricing',
    },
    {
      label: 'Renewable Energy',
      value: `${(analytics?.renewable_percentage || 0).toFixed(1)}%`,
      icon: '🌱',
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      description: 'From solar sources',
    },
    {
      label: 'Energy Charged',
      value: `${(analytics?.total_energy_charged || 0).toFixed(1)} kWh`,
      icon: '⚡',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      description: 'Total today',
    },
    {
      label: 'Grid Impact',
      value: (analytics?.grid_impact_score || 0).toFixed(1),
      icon: '🌍',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      description: 'Lower is better',
    },
  ];

  return (
    <div className="card">
      <h2 className="card-title">📈 Analytics & Insights</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className={`${metric.bgColor} p-4 rounded-lg border border-slate-700`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{metric.icon}</span>
                <div>
                  <div className="text-sm text-gray-400">{metric.label}</div>
                  <div className={`text-2xl font-bold ${metric.color}`}>
                    {metric.value}
                  </div>
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {metric.description}
            </div>
          </div>
        ))}
      </div>

      {/* Additional Insights */}
      <div className="mt-6 p-4 bg-slate-900/50 rounded-lg border border-slate-700">
        <h3 className="text-sm font-semibold text-gray-400 mb-3">
          💡 Smart Insights
        </h3>
        <ul className="space-y-2 text-sm text-gray-300">
          <li className="flex items-start gap-2">
            <span className="text-green-400 mt-1">✓</span>
            <span>
              Bob is optimizing your charging to maximize solar usage and minimize costs.
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-400 mt-1">ℹ</span>
            <span>
              {analytics?.renewable_percentage > 50
                ? 'Great job! Over 50% of your energy is from renewable sources.'
                : 'Consider charging during peak solar hours for more renewable energy.'}
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-yellow-400 mt-1">⚠</span>
            <span>
              {analytics?.grid_impact_score < 5
                ? 'Your grid impact is low - excellent!'
                : 'Consider shifting more charging to off-peak hours.'}
            </span>
          </li>
        </ul>
      </div>

      {/* Last Updated */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default Analytics;

// Made with Bob
