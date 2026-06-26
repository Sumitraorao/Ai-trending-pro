'use client';

import { Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

export default function RiskMeter({ metrics }) {
  if (!metrics) {
    return (
      <div className="card animate-pulse">
        <div className="h-32 bg-gray-800 rounded-lg" />
      </div>
    );
  }

  const { risk_level, trading_enabled, daily_pnl_pct, consecutive_losses, max_daily_loss_pct } = metrics;

  const getRiskColor = (level) => {
    switch (level) {
      case 'LOW': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'MEDIUM': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'HIGH': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'CRITICAL': return 'text-red-500 bg-red-500/20 border-red-500/30';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getRiskIcon = (level) => {
    switch (level) {
      case 'LOW': return <CheckCircle className="w-5 h-5" />;
      case 'MEDIUM': return <AlertTriangle className="w-5 h-5" />;
      case 'HIGH':
      case 'CRITICAL': return <XCircle className="w-5 h-5" />;
      default: return <Shield className="w-5 h-5" />;
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-white">Risk Management</h3>
        </div>
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${getRiskColor(risk_level)}`}>
          {getRiskIcon(risk_level)}
          {risk_level}
        </div>
      </div>

      {/* Trading Status */}
      <div className={`p-3 rounded-lg mb-4 ${
        trading_enabled ? 'bg-emerald-500/5 border border-emerald-500/20' : 'bg-red-500/5 border border-red-500/20'
      }`}>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${trading_enabled ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
          <span className={`text-sm font-medium ${trading_enabled ? 'text-emerald-400' : 'text-red-400'}`}>
            {trading_enabled ? 'Trading Active' : 'Trading Halted'}
          </span>
        </div>
        {!trading_enabled && (
          <p className="text-xs text-red-400 mt-1 ml-4">
            Trading stopped due to excessive losses. Reset required.
          </p>
        )}
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-900/50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Daily P&L</p>
          <p className={`text-lg font-semibold ${daily_pnl_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {daily_pnl_pct >= 0 ? '+' : ''}{daily_pnl_pct}%
          </p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Consecutive Losses</p>
          <p className={`text-lg font-semibold ${consecutive_losses >= 2 ? 'text-red-400' : 'text-white'}`}>
            {consecutive_losses}
          </p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Max Daily Loss</p>
          <p className="text-lg font-semibold text-white">{max_daily_loss_pct}%</p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Max Single Trade</p>
          <p className="text-lg font-semibold text-white">5%</p>
        </div>
      </div>
    </div>
  );
}
