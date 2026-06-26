'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import TradingChart from '@/components/TradingChart';
import AIStatus from '@/components/AIStatus';
import { api } from '@/lib/api';
import { 
  Search, TrendingUp, TrendingDown, Loader2, 
  ArrowUpRight, ArrowDownRight, Brain, AlertTriangle 
} from 'lucide-react';

const POPULAR_STOCKS = [
  'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 
  'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS'
];

export default function TradingPage() {
  const router = useRouter();
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE.NS');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [indicators, setIndicators] = useState(null);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [portfolio, setPortfolio] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadData();
  }, [router]);

  useEffect(() => {
    if (selectedSymbol) {
      loadSymbolData();
    }
  }, [selectedSymbol]);

  const loadData = async () => {
    try {
      const portfolioRes = await api.getPortfolio();
      setPortfolio(portfolioRes);
    } catch (error) {
      console.error('Error loading portfolio:', error);
    }
  };

  const loadSymbolData = async () => {
    setLoading(true);
    try {
      const [priceRes, historicalRes, predictionRes, indicatorsRes] = await Promise.all([
        api.getPrice(selectedSymbol),
        api.getHistorical(selectedSymbol, '3mo', '1d'),
        api.getPrediction(selectedSymbol),
        api.getIndicators(selectedSymbol),
      ]);

      setCurrentPrice(priceRes);
      setChartData(historicalRes.data || []);
      setPrediction(predictionRes.prediction);
      setIndicators(indicatorsRes.signals);
    } catch (error) {
      console.error('Error loading symbol data:', error);
      setMessage({ type: 'error', text: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const res = await api.searchStocks(searchQuery);
      setSearchResults(res.results || []);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleBuy = async () => {
    if (!quantity || quantity < 1) {
      setMessage({ type: 'error', text: 'Please enter a valid quantity' });
      return;
    }

    setActionLoading(true);
    try {
      const res = await api.buyStock(
        selectedSymbol, 
        parseInt(quantity),
        prediction?.stop_loss,
        prediction?.target
      );
      setMessage({ type: 'success', text: res.message });
      loadData();
      setQuantity(1);
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setActionLoading(false);
    }
  };

  const handleSell = async () => {
    if (!quantity || quantity < 1) {
      setMessage({ type: 'error', text: 'Please enter a valid quantity' });
      return;
    }

    setActionLoading(true);
    try {
      const res = await api.sellStock(selectedSymbol, parseInt(quantity));
      setMessage({ type: 'success', text: res.message });
      loadData();
      setQuantity(1);
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setActionLoading(false);
    }
  };

  const currentHolding = portfolio?.holdings?.find(h => h.symbol === selectedSymbol);

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      <Navbar />

      <main className="lg:ml-64 pt-16 lg:pt-0">
        <div className="p-4 lg:p-8">
          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
            <h1 className="text-2xl font-bold text-white">Trading Terminal</h1>

            {/* Search */}
            <div className="relative max-w-md w-full">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Search stocks..."
                    className="input-field w-full pl-10"
                  />
                </div>
                <button onClick={handleSearch} className="btn-primary px-4">
                  <Search className="w-4 h-4" />
                </button>
              </div>

              {searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-[#1f2937] border border-gray-700 rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto">
                  {searchResults.map((result) => (
                    <button
                      key={result.symbol}
                      onClick={() => {
                        setSelectedSymbol(result.symbol);
                        setSearchResults([]);
                        setSearchQuery('');
                      }}
                      className="w-full text-left px-4 py-3 hover:bg-gray-700 transition-colors border-b border-gray-800 last:border-0"
                    >
                      <p className="text-white font-medium">{result.name}</p>
                      <p className="text-gray-500 text-sm">{result.symbol}</p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Popular Stocks */}
          <div className="flex gap-2 overflow-x-auto pb-4 mb-6">
            {POPULAR_STOCKS.map((stock) => (
              <button
                key={stock}
                onClick={() => setSelectedSymbol(stock)}
                className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                  selectedSymbol === stock
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {stock.replace('.NS', '')}
              </button>
            ))}
          </div>

          {/* Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg ${
              message.type === 'success' 
                ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' 
                : 'bg-red-500/10 border border-red-500/20 text-red-400'
            }`}>
              <div className="flex items-center gap-2">
                {message.type === 'success' ? <TrendingUp className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                {message.text}
              </div>
            </div>
          )}

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Chart Section */}
            <div className="lg:col-span-2 space-y-6">
              {/* Price Header */}
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedSymbol}</h2>
                    <p className="text-gray-500 text-sm">{currentPrice?.info?.name || selectedSymbol}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-white">
                      ₹{currentPrice?.current_price?.toLocaleString('en-IN') || '---'}
                    </p>
                    {currentPrice?.info?.market_cap && (
                      <p className="text-xs text-gray-500">
                        MCap: ₹{(currentPrice.info.market_cap / 1e9).toFixed(2)}B
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Chart */}
              <div className="card">
                {loading ? (
                  <div className="flex items-center justify-center h-[400px]">
                    <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                  </div>
                ) : (
                  <TradingChart data={chartData} />
                )}
              </div>

              {/* Indicators */}
              {indicators && (
                <div className="card">
                  <h3 className="font-semibold text-white mb-4">Technical Indicators</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <IndicatorBox label="RSI" value={indicators.rsi} />
                    <IndicatorBox label="MACD" value={indicators.macd} />
                    <IndicatorBox label="SMA 20" value={indicators.sma_20} />
                    <IndicatorBox label="SMA 50" value={indicators.sma_50} />
                    <IndicatorBox label="BB Upper" value={indicators.bb_upper} />
                    <IndicatorBox label="BB Lower" value={indicators.bb_lower} />
                    <IndicatorBox label="ATR" value={indicators.atr} />
                    <IndicatorBox label="Volume" value={indicators.volume?.toLocaleString()} />
                  </div>
                </div>
              )}
            </div>

            {/* Right Panel */}
            <div className="space-y-6">
              {/* AI Prediction */}
              <AIStatus prediction={prediction} />

              {/* Trading Panel */}
              <div className="card glow-border">
                <h3 className="font-semibold text-white mb-4">Place Order</h3>

                {/* Current Holding Info */}
                {currentHolding && (
                  <div className="mb-4 p-3 bg-gray-900/50 rounded-lg">
                    <p className="text-xs text-gray-500">Current Holding</p>
                    <p className="text-white font-medium">{currentHolding.quantity} shares @ ₹{currentHolding.avg_buy_price}</p>
                    <p className={`text-xs ${currentHolding.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      P&L: {currentHolding.unrealized_pnl >= 0 ? '+' : ''}₹{currentHolding.unrealized_pnl.toLocaleString('en-IN')} ({currentHolding.unrealized_pnl_pct}%)
                    </p>
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Quantity</label>
                    <input
                      type="number"
                      min="1"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                      className="input-field w-full"
                    />
                  </div>

                  {currentPrice?.current_price && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Estimated Value</span>
                      <span className="text-white font-medium">
                        ₹{(currentPrice.current_price * quantity).toLocaleString('en-IN')}
                      </span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={handleBuy}
                      disabled={actionLoading}
                      className="btn-success flex items-center justify-center gap-2 py-3"
                    >
                      {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUpRight className="w-4 h-4" />}
                      BUY
                    </button>
                    <button
                      onClick={handleSell}
                      disabled={actionLoading}
                      className="btn-danger flex items-center justify-center gap-2 py-3"
                    >
                      {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowDownRight className="w-4 h-4" />}
                      SELL
                    </button>
                  </div>
                </div>
              </div>

              {/* Strategy Signals */}
              {prediction?.strategy_signals && (
                <div className="card">
                  <h3 className="font-semibold text-white mb-3">Strategy Analysis</h3>
                  <div className="space-y-2">
                    {prediction.strategy_signals.map((sig, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-gray-900/50">
                        <span className="text-sm text-gray-400">{sig.strategy}</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-medium ${
                            sig.action === 'BUY' ? 'text-emerald-400' : 
                            sig.action === 'SELL' ? 'text-red-400' : 'text-amber-400'
                          }`}>
                            {sig.action}
                          </span>
                          <span className="text-xs text-gray-500">{sig.confidence}%</span>
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

function IndicatorBox({ label, value }) {
  return (
    <div className="bg-gray-900/50 rounded-lg p-3 text-center">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-white font-semibold">{value !== null && value !== undefined ? value : '---'}</p>
    </div>
  );
}
