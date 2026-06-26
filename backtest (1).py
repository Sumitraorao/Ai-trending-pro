"""Backtesting script"""
import os
import sys
import argparse
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_engine.simulator import backtest_simulator

def run_backtest(symbol: str, start_date: str, end_date: str, strategy: str = "ml"):
    """Run backtest for a symbol"""
    print(f"🔍 Running backtest for {symbol}")
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"🎯 Strategy: {strategy}")

    results = backtest_simulator.run_backtest(symbol, start_date, end_date, strategy)

    if results["status"] == "success":
        report = backtest_simulator.get_performance_report(results)

        print("\n📊 Backtest Results:")
        print(f"   Initial Balance: ₹{results['initial_balance']:,.2f}")
        print(f"   Final Value: ₹{results['final_value']:,.2f}")
        print(f"   Total Return: {results['total_return_pct']}%")
        print(f"   Max Drawdown: {results['max_drawdown_pct']}%")
        print(f"   Win Rate: {results['win_rate']}%")
        print(f"   Sharpe Ratio: {results['sharpe_ratio']}")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Grade: {report['grade']}")

        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

        # Save results
        results_dir = "./backtest_results"
        os.makedirs(results_dir, exist_ok=True)

        filename = f"{results_dir}/{symbol.replace('.', '_')}_{start_date}_{end_date}.json"
        with open(filename, 'w') as f:
            json.dump({**results, **report}, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {filename}")

        return {**results, **report}
    else:
        print(f"❌ Backtest failed: {results.get('message', 'Unknown error')}")
        return results

def main():
    parser = argparse.ArgumentParser(description='Run Backtest')
    parser.add_argument('--symbol', type=str, default='RELIANCE.NS', help='Stock symbol')
    parser.add_argument('--start', type=str, default='2023-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2024-01-01', help='End date (YYYY-MM-DD)')
    parser.add_argument('--strategy', type=str, default='ml', choices=['ml', 'ma_crossover'])

    args = parser.parse_args()

    run_backtest(args.symbol, args.start, args.end, args.strategy)

if __name__ == "__main__":
    main()
