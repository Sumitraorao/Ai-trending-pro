'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import PortfolioCard from '@/components/PortfolioCard';
import AIStatus from '@/components/AIStatus';
import TradeHistory from '@/components/TradeHistory';
import RiskMeter from '@/components/RiskMeter';
import { api } from '@/lib/api';
import { 
  TrendingUp, TrendingDown, Activity, Brain, 
  DollarSign, BarChart3, RefreshCw, Loader2 
} from 'lucide-react';

export default function Dashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [marketStatus, setMarketStatus] = useState({ status: 'Loading...' });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadDashboardData();
  }, [router]);

  const loadDashboardData = async () => {
    try {
      setRefreshing(true);
      const [portfolioRes, tradesRes, riskRes] = await Promise.all([
        api.getPortfolio(),
        api.getTradeHistory(10),
        api.getRiskMetrics(),
      ]);

      setPortfolio(portfolioRes);
      setTrades(tradesRes.trades || []);
      setRiskMetrics(riskRes.risk_metrics);
      setMarketStatus({ status: 'Open', time: new Date().toLocaleTimeString() });
    } catch (error) {
      console.error('Error loading dashboard:', error);
      if (error.message?.includes('401')) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard...</p>
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
              <h1 className="text-2xl font-bold text-white">Dashboard</h1>
              <p className="text-gray-400 text-sm mt-1">
                Market Status: <span className="text-emerald-400">{marketStatus.status}</span> | {marketStatus.time}
              </p>
            </div>
            <button
              onClick={loadDashboardData}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-300 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard 
              icon={<DollarSign className="w-5 h-5" />}
              label="Virtual Balance"
              value={`₹${Number(portfolio?.virtual_balance || 0).toLocaleString('en-IN')}`}
              color="blue"
            />
            <StatCard 
              icon={isProfit ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
              label="Total P&L"
              value={`${isProfit ? '+' : ''}₹${Number(portfolio?.total_return || 0).toLocaleString('en-IN')}`}
              color={isProfit ? 'emerald' : 'red'}
              subValue={`${isProfit ? '+' : ''}${portfolio?.total_return_pct || 0}%`}
            />
            <StatCard 
              icon={<Activity className="w-5 h-5" />}
              label="Active Trades"
              value={portfolio?.total_trades || 0}
              color="amber"
            />
            <StatCard 
              icon={<Brain className="w-5 h-5" />}
              label="Win Rate"
              value={`${portfolio?.win_rate || 0}%`}
              color="purple"
            />
          </div>

          {/* Main Grid */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Left Column */}
            <div className="lg:col-span-2 space-y-6">
              <PortfolioCard portfolio={portfolio} />

              {/* Quick Actions */}
              <div className="card">
                <h3 className="font-semibold text-white mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <QuickActionButton 
                    href="/trading"
                    icon={<BarChart3 className="w-5 h-5" />}
                    label="Trade"
                    color="blue"
                  />
                  <QuickActionButton 
                    href="/portfolio"
                    icon={<TrendingUp className="w-5 h-5" />}
                    label="Portfolio"
                    color="emerald"
                  />
                </div>
              </div>

              <TradeHistory trades={trades} />
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              <RiskMeter metrics={riskMetrics} />

              {/* AI Confidence Overview */}
              <div className="card">
                <div className="flex items-center gap-2 mb-4">
                  <Brain className="w-5 h-5 text-purple-400" />
                  <h3 className="font-semibold text-white">AI System</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Model Status</span>
                    <span className="text-sm text-emerald-400 flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      Active
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Strategies</span>
                    <span className="text-sm text-white">4 Active</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Last Update</span>
                    <span className="text-sm text-white">Just now</span>
                  </div>
                </div>
              </div>

              {/* Holdings Summary */}
              {portfolio?.holdings && portfolio.holdings.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-white mb-4">Holdings</h3>
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {portfolio.holdings.map((holding) => (
                      <div key={holding.symbol} className="flex items-center justify-between p-2 rounded-lg bg-gray-900/50">
                        <div>
                          <p className="font-medium text-white text-sm">{holding.symbol}</p>
                          <p className="text-xs text-gray-500">{holding.quantity} shares</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-white">₹{Number(holding.total_value).toLocaleString('en-IN')}</p>
                          <p className={`text-xs ${holding.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {holding.unrealized_pnl >= 0 ? '+' : ''}{holding.unrealized_pnl_pct}%
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ icon, label, value, color, subValue }) {
  const colorClasses = {
    blue: 'text-blue-400 bg-blue-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    red: 'text-red-400 bg-red-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    purple: 'text-purple-400 bg-purple-500/10',
  };

  return (
    <div className="card card-hover">
      <div className="flex items-center gap-3 mb-2">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
          {icon}
        </div>
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <p className="text-xl font-bold text-white">{value}</p>
      {subValue && <p className="text-xs text-gray-500 mt-1">{subValue}</p>}
    </div>
  );
}

function QuickActionButton({ href, icon, label, color }) {
  const colorClasses = {
    blue: 'hover:bg-blue-500/10 hover:border-blue-500/30',
    emerald: 'hover:bg-emerald-500/10 hover:border-emerald-500/30',
    amber: 'hover:bg-amber-500/10 hover:border-amber-500/30',
    purple: 'hover:bg-purple-500/10 hover:border-purple-500/30',
  };

  return (
    <a
      href={href}
      className={`flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-800 bg-gray-900/50 transition-all ${colorClasses[color]}`}
    >
      <div className="text-gray-400">{icon}</div>
      <span className="text-sm text-gray-300">{label}</span>
    </a>
  );
}
