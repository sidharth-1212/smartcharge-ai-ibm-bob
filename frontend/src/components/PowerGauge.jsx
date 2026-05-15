import React from 'react';

const PowerGauge = ({ label, value, max, unit, color, icon }) => {
  const percentage = Math.min((value / max) * 100, 100);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const colorClasses = {
    solar: 'text-solar stroke-solar',
    grid: 'text-grid stroke-grid',
    battery: 'text-battery stroke-battery',
  };

  const bgColorClasses = {
    solar: 'bg-solar/10',
    grid: 'bg-grid/10',
    battery: 'bg-battery/10',
  };

  return (
    <div className={`card ${bgColorClasses[color]} border-${color}/20`}>
      <div className="flex flex-col items-center">
        <h3 className="text-lg font-semibold text-gray-300 mb-4">{label}</h3>
        
        <div className="relative w-48 h-48">
          <svg className="transform -rotate-90 w-48 h-48">
            {/* Background circle */}
            <circle
              cx="96"
              cy="96"
              r={radius}
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              className="text-slate-700"
            />
            {/* Progress circle */}
            <circle
              cx="96"
              cy="96"
              r={radius}
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className={`${colorClasses[color]} transition-all duration-500 ease-out`}
              strokeLinecap="round"
            />
          </svg>
          
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {icon && <div className="text-4xl mb-2">{icon}</div>}
            <div className={`text-3xl font-bold ${colorClasses[color]}`}>
              {value.toFixed(1)}
            </div>
            <div className="text-sm text-gray-400">{unit}</div>
            <div className="text-xs text-gray-500 mt-1">
              {percentage.toFixed(0)}%
            </div>
          </div>
        </div>
        
        <div className="mt-4 text-center">
          <div className="text-sm text-gray-400">
            Max: {max} {unit}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PowerGauge;

// Made with Bob
