import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-4xl">⚡</div>
              <div>
                <h1 className="text-3xl font-bold text-white">
                  SmartCharge AI
                </h1>
                <p className="text-sm text-gray-400">
                  Intelligent EV Charging Optimizer powered by IBM Bob
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm text-gray-400">Status</div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  <span className="text-green-400 font-semibold">Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Dashboard />
      </main>

      {/* Footer */}
      <footer className="bg-slate-800 border-t border-slate-700 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-gray-400">
            <p>
              SmartCharge AI - Optimizing EV charging with renewable energy and cost savings
            </p>
            <p className="mt-2 text-xs text-gray-500">
              Powered by IBM Bob • Built for the IBM Bob Hackathon Challenge
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

// Made with Bob
