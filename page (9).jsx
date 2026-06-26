'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import PortfolioCard from '@/components/PortfolioCard';
import TradeHistory from '@/components/TradeHistory';
import { api } from '@/lib/api';
import { 
  Loader2, TrendingUp, TrendingDown, Calendar, 
  BarChart3, Target, Award, ArrowUpRight, ArrowDownRight 
} from 'lucide-react';

export default function PortfolioPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadData();
  }, [router, period]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [portfolioRes, tradesRes, perfRes] = await Promise.all([
        api.getPortfolio(),
        api.getTradeHistory(100),
        api.getPerformance(period),
      ]);

      setPortfolio(portfolioRes);
      setTrades(tradesRes.trades || []);
      setPerformance(perfRes.metrics);
    } catch (error) {
      console.error('Error loading portfolio data:', error);
      if (error.message?.includes('401')) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  const isProfit = portfolio?.total_return >= 0;

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      <Navbar />

      <main className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-4 lg:p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-white">Portfolio</h1>
              <p className="text-gray-400 text-sm mt-1">Track your paper trading performance</p>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <select
                value={period}
                onChange={(e) => setPeriod(Number(e.target.value))}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
              >
                <option value={7}>Last 7 Days</option>
                <option value={30}>Last 30 Days</option>
                <option value={90}>Last 90 Days</option>
                <option value={365}>Last Year</option>
              </select>
            </div>
          </div>

          {/* Portfolio Overview */}
          <div className="mb-6">
            <PortfolioCard portfolio={portfolio} />
          </div>

          {/* Performance Metrics */}
          {performance && performance.total_trades > 0 && (
            <div className="card mb-6">
              <div className="flex items-center gap-2 mb-6">
                <BarChart3 className="w-5 h-5 text-blue-400" />
                <h3 className="font-semibold text-white">Performance Metrics</h3>
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard 
                  label="Total Trades"
                  value={performance.total_trades}
                  icon={<Target className="w-4 h-4" />}
                  color="blue"
                />
                <MetricCard 
                  label="Win Rate"
                  value={`${performance.win_rate}%`}
                  icon={<Award className="w-4 h-4" />}
                  color="emerald"
                />
                <MetricCard 
                  label="Profit Factor"
                  value={performance.profit_factor}
                  icon={<TrendingUp className="w-4 h-4" />}
                  color="purple"
                />
                <MetricCard 
                  label="Total P&L"
                  value={`₹${performance.total_pnl?.toLocaleString('en-IN')}`}
                  icon={performance.total_pnl >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  color={performance.total_pnl >= 0 ? 'emerald' : 'red'}
                />
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gray-900/50 rounded-lg p-4">
                  <p className="text-xs text-gray-500 mb-1">Winning Trades</p>
                  <p className="text-xl font-bold text-emerald-400">{performance.winning_trades}</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-4">
                  <p className="text-xs text-gray-500 mb-1">Losing Trades</p>
                  <p className="text-xl font-bold text-red-400">{performance.losing_trades}</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-4">
                  <p className="text-xs text-gray-500 mb-1">Avg Profit</p>
                  <p className="text-xl font-bold text-emerald-400">₹{performance.avg_profit?.toLocaleString('en-IN')}</p>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-4">
                  <p className="text-xs text-gray-500 mb-1">Avg Loss</p>
                  <p className="text-xl font-bold text-red-400">₹{performance.avg_loss?.toLocaleString('en-IN')}</p>
                </div>
              </div>

              {performance.largest_profit > 0 && (
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="bg-gray-900/50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">Largest Profit</p>
                    <p className="text-lg font-bold text-emerald-400">₹{performance.largest_profit?.toLocaleString('en-IN')}</p>
                  </div>
                  <div className="bg-gray-900/50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">Largest Loss</p>
                    <p className="text-lg font-bold text-red-400">₹{performance.largest_loss?.toLocaleString('en-IN')}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Holdings Detail */}
          {portfolio?.holdings && portfolio.holdings.length > 0 && (
            <div className="card mb-6">
              <h3 className="font-semibold text-white mb-4">Holdings Detail</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-xs text-gray-500 border-b border-gray-800">
                      <th className="pb-3 pr-4">Symbol</th>
                      <th className="pb-3 pr-4">Quantity</th>
                      <th className="pb-3 pr-4">Avg Buy</th>
                      <th className="pb-3 pr-4">Current</th>
                      <th className="pb-3 pr-4">Value</th>
                      <th className="pb-3 pr-4">P&L</th>
                      <th className="pb-3">P&L %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.holdings.map((holding) => (
                      <tr key={holding.symbol} className="border-b border-gray-800/50 last:border-0">
                        <td className="py-3 pr-4">
                          <span className="font-medium text-white">{holding.symbol}</span>
                        </td>
                        <td className="py-3 pr-4 text-gray-300">{holding.quantity}</td>
                        <td className="py-3 pr-4 text-gray-300">₹{holding.avg_buy_price}</td>
                        <td className="py-3 pr-4 text-gray-300">₹{holding.current_price}</td>
                        <td className="py-3 pr-4 text-white font-medium">₹{Number(holding.total_value).toLocaleString('en-IN')}</td>
                        <td className="py-3 pr-4">
                          <span className={holding.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                            {holding.unrealized_pnl >= 0 ? '+' : ''}₹{Number(holding.unrealized_pnl).toLocaleString('en-IN')}
                          </span>
                        </td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            holding.unrealized_pnl_pct >= 0 
                              ? 'bg-emerald-500/10 text-emerald-400' 
                              : 'bg-red-500/10 text-red-400'
                          }`}>
                            {holding.unrealized_pnl_pct >= 0 ? '+' : ''}{holding.unrealized_pnl_pct}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Trade History */}
          <TradeHistory trades={trades} />
        </div>
      </main>
    </div>
  );
}

function MetricCard({ label, value, icon, color }) {
  const colorClasses = {
    blue: 'text-blue-400 bg-blue-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    red: 'text-red-400 bg-red-500/10',
    purple: 'text-purple-400 bg-purple-500/10',
  };

  return (
    <div className="bg-gray-900/50 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-6 h-6 rounded flex items-center justify-center ${colorClasses[color]}`}>
          {icon}
        </div>
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <p className="text-xl font-bold text-white">{value}</p>
    </div>
  );
}
