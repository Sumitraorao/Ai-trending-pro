'use client';

import { History, ArrowUpRight, ArrowDownRight, Clock } from 'lucide-react';

export default function TradeHistory({ trades }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <History className="w-5 h-5 text-gray-400" />
          <h3 className="font-semibold text-white">Recent Trades</h3>
        </div>
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No trades yet</p>
          <p className="text-sm mt-1">Start trading to see your history here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-gray-400" />
          <h3 className="font-semibold text-white">Recent Trades</h3>
        </div>
        <span className="text-xs text-gray-500">{trades.length} trades</span>
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {trades.map((trade) => {
          const isBuy = trade.action === 'BUY';
          const isProfit = trade.profit_loss > 0;
          const isOpen = trade.status === 'OPEN';

          return (
            <div
              key={trade.id}
              className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50 hover:bg-gray-800/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  isBuy ? 'bg-emerald-500/10' : 'bg-red-500/10'
                }`}>
                  {isBuy ? (
                    <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-red-400" />
                  )}
                </div>
                <div>
                  <p className="font-medium text-white text-sm">{trade.symbol}</p>
                  <p className="text-xs text-gray-500">
                    {isBuy ? 'Bought' : 'Sold'} {trade.quantity} @ ₹{trade.entry_price}
                    {trade.exit_price && ` → ₹${trade.exit_price}`}
                  </p>
                </div>
              </div>
              <div className="text-right">
                {!isOpen && trade.profit_loss !== null && (
                  <p className={`text-sm font-semibold ${isProfit ? 'text-emerald-400' : 'text-red-400'}`}>
                    {isProfit ? '+' : ''}₹{Number(trade.profit_loss).toLocaleString('en-IN')}
                  </p>
                )}
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  isOpen 
                    ? 'bg-amber-500/10 text-amber-400' 
                    : isProfit 
                      ? 'bg-emerald-500/10 text-emerald-400' 
                      : 'bg-red-500/10 text-red-400'
                }`}>
                  {trade.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
