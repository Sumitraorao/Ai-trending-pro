'use client';

import { Wallet, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function PortfolioCard({ portfolio }) {
  if (!portfolio) {
    return (
      <div className="card animate-pulse">
        <div className="h-20 bg-gray-800 rounded-lg" />
      </div>
    );
  }

  const {
    virtual_balance,
    total_holdings_value,
    total_portfolio_value,
    total_return,
    total_return_pct,
    win_rate,
    total_trades,
    max_drawdown,
  } = portfolio;

  const isProfit = total_return >= 0;

  return (
    <div className="card glow-border">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Wallet className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-white">Portfolio Overview</h3>
        </div>
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
          isProfit ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
        }`}>
          {isProfit ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
          {isProfit ? '+' : ''}{total_return_pct}%
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-900/50 rounded-lg p-4">
          <p className="text-xs text-gray-500 mb-1">Total Value</p>
          <p className="text-2xl font-bold text-white">₹{Number(total_portfolio_value).toLocaleString('en-IN')}</p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4">
          <p className="text-xs text-gray-500 mb-1">Cash Balance</p>
          <p className="text-2xl font-bold text-white">₹{Number(virtual_balance).toLocaleString('en-IN')}</p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4">
          <p className="text-xs text-gray-500 mb-1">Holdings Value</p>
          <p className="text-xl font-semibold text-white">₹{Number(total_holdings_value).toLocaleString('en-IN')}</p>
        </div>
        <div className="bg-gray-900/50 rounded-lg p-4">
          <p className="text-xs text-gray-500 mb-1">P&L</p>
          <p className={`text-xl font-semibold ${isProfit ? 'text-emerald-400' : 'text-red-400'}`}>
            {isProfit ? '+' : ''}₹{Number(total_return).toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{win_rate}%</p>
          <p className="text-xs text-gray-500">Win Rate</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{total_trades}</p>
          <p className="text-xs text-gray-500">Trades</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-red-400">{max_drawdown}%</p>
          <p className="text-xs text-gray-500">Max DD</p>
        </div>
      </div>
    </div>
  );
}
