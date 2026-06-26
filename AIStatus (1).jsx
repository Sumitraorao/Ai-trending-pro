'use client';

import { Brain, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

export default function AIStatus({ prediction }) {
  if (!prediction) {
    return (
      <div className="card flex items-center justify-center h-32">
        <div className="text-gray-500 flex items-center gap-2">
          <Brain className="w-5 h-5 animate-pulse" />
          <span>Waiting for AI analysis...</span>
        </div>
      </div>
    );
  }

  const { action, confidence, stop_loss, target, current_price, technical_signals } = prediction;

  const getActionColor = (action) => {
    switch (action) {
      case 'BUY': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'SELL': return 'text-red-400 bg-red-500/10 border-red-500/20';
      default: return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'BUY': return <TrendingUp className="w-5 h-5" />;
      case 'SELL': return <TrendingUp className="w-5 h-5 rotate-180" />;
      default: return <AlertTriangle className="w-5 h-5" />;
    }
  };

  return (
    <div className="card glow-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          <h3 className="font-semibold text-white">AI Prediction</h3>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${getActionColor(action)}`}>
          {getActionIcon(action)}
          <span className="font-bold">{action}</span>
        </div>
      </div>

      {/* Confidence Meter */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-400">Confidence</span>
          <span className="text-white font-semibold">{confidence}%</span>
        </div>
        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              confidence > 70 ? 'bg-emerald-500' : confidence > 40 ? 'bg-amber-500' : 'bg-red-500'
            }`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Price Info */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-gray-900/50 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-500 mb-1">Current</p>
          <p className="text-white font-semibold">₹{current_price}</p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-500 mb-1">Stop Loss</p>
          <p className="text-red-400 font-semibold">₹{stop_loss}</p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-3 text-center">
          <p className="text-xs text-gray-500 mb-1">Target</p>
          <p className="text-emerald-400 font-semibold">₹{target}</p>
        </div>
      </div>

      {/* Technical Signals */}
      {technical_signals && technical_signals.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2">Technical Signals</p>
          <div className="flex flex-wrap gap-2">
            {technical_signals.map((signal, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20"
              >
                {signal}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
