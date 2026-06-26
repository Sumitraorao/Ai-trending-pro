'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { TrendingUp, Shield, Brain, BarChart3, ArrowRight, Zap, Lock } from 'lucide-react';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      {/* Navbar */}
      <nav className="border-b border-gray-800 bg-[#0a0e1a]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-blue-500" />
              <span className="text-xl font-bold text-white">AI-Trader-Pro</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-gray-300 hover:text-white transition-colors">
                Sign In
              </Link>
              <Link href="/login" className="btn-primary">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-32">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/10 to-transparent" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-8">
              <Zap className="w-4 h-4 text-blue-400" />
              <span className="text-blue-400 text-sm font-medium">Paper Trading Only - No Real Money</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="text-white">AI-Powered</span>
              <br />
              <span className="text-gradient">Trading Intelligence</span>
            </h1>

            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
              Autonomous AI trading assistant that learns from market data, generates signals, 
              and trades with virtual money. Build confidence before going live.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/login" className="btn-primary flex items-center justify-center gap-2 text-lg px-8 py-3">
                Start Trading <ArrowRight className="w-5 h-5" />
              </Link>
              <Link href="/login" className="bg-gray-800 hover:bg-gray-700 text-white px-8 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 text-lg">
                <Brain className="w-5 h-5" /> Learn More
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-16">
            <span className="text-gradient">Powerful Features</span>
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard 
              icon={<Brain className="w-8 h-8 text-purple-400" />}
              title="AI Predictions"
              description="Machine learning models analyze market data and generate BUY/SELL/HOLD signals with confidence scores."
            />
            <FeatureCard 
              icon={<BarChart3 className="w-8 h-8 text-blue-400" />}
              title="Technical Analysis"
              description="RSI, MACD, Moving Averages, Bollinger Bands, and more indicators calculated in real-time."
            />
            <FeatureCard 
              icon={<Shield className="w-8 h-8 text-emerald-400" />}
              title="Risk Management"
              description="Automatic stop-losses, position sizing limits, and circuit breakers to protect your portfolio."
            />
            <FeatureCard 
              icon={<TrendingUp className="w-8 h-8 text-amber-400" />}
              title="Paper Trading"
              description="Practice with ₹10,00,000 virtual money. Zero risk while you learn and refine your strategy."
            />
            <FeatureCard 
              icon={<Zap className="w-8 h-8 text-red-400" />}
              title="Backtesting"
              description="Test strategies on historical data. Performance reports with Sharpe ratio and drawdown analysis."
            />
            <FeatureCard 
              icon={<Lock className="w-8 h-8 text-cyan-400" />}
              title="Secure & Private"
              description="JWT authentication, encrypted data, and complete privacy. Your data stays yours."
            />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 border-t border-gray-800 bg-[#0d1321]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <StatCard number="₹10L" label="Virtual Balance" />
            <StatCard number="50+" label="Indian Stocks" />
            <StatCard number="15+" label="Technical Indicators" />
            <StatCard number="100%" label="Risk-Free" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500">
          <p> AI-Trader-Pro. Built for learning. Paper trading only.</p>
          <p className="mt-2 text-sm">Not financial advice. Trade at your own risk.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="card card-hover">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{description}</p>
    </div>
  );
}

function StatCard({ number, label }) {
  return (
    <div>
      <div className="text-3xl md:text-4xl font-bold text-gradient mb-2">{number}</div>
      <div className="text-gray-400 text-sm">{label}</div>
    </div>
  );
}
