"""Backtesting and simulation engine"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from data.market_data import market_engine
from data.indicators import indicators
from ai.model import trading_model
from config import settings

class BacktestSimulator:
    def __init__(self, initial_balance: float = 1000000.0):
        self.initial_balance = initial_balance

    def run_backtest(self, symbol: str, start_date: str, end_date: str, 
                     strategy: str = "ml") -> Dict:
        try:
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            data = data.reset_index()
            data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]

            if data.empty:
                return {"status": "error", "message": "No data available for the specified period"}

            # Calculate indicators
            data = indicators.calculate_all(data)
            data = data.dropna()

            if len(data) < 50:
                return {"status": "error", "message": "Insufficient data for backtesting"}

            # Train model if using ML strategy
            if strategy == "ml":
                train_data = data.iloc[:int(len(data) * 0.7)]
                test_data = data.iloc[int(len(data) * 0.7):]

                if len(train_data) < 100:
                    return {"status": "error", "message": "Insufficient training data"}

                training_result = trading_model.train(train_data)
                if training_result.get("status") != "success":
                    return training_result
            else:
                test_data = data

            # Run simulation
            results = self._simulate_trades(test_data, strategy)

            return {
                "status": "success",
                "symbol": symbol,
                "strategy": strategy,
                "period": f"{start_date} to {end_date}",
                "total_days": len(test_data),
                **results
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _simulate_trades(self, data: pd.DataFrame, strategy: str) -> Dict:
        cash = self.initial_balance
        holdings = 0
        trades = []
        portfolio_values = []
        peak_value = self.initial_balance
        max_drawdown = 0

        for i in range(1, len(data)):
            current_price = data.iloc[i]['Close']
            prev_price = data.iloc[i-1]['Close']

            # Get signal
            if strategy == "ml":
                signal_data = data.iloc[:i+1]
                prediction = trading_model.predict(signal_data)
                action = prediction.get('action', 'HOLD')
                confidence = prediction.get('confidence', 0)
            else:
                # Simple moving average crossover
                if data.iloc[i]['SMA_20'] > data.iloc[i]['SMA_50'] and data.iloc[i-1]['SMA_20'] <= data.iloc[i-1]['SMA_50']:
                    action = 'BUY'
                    confidence = 70
                elif data.iloc[i]['SMA_20'] < data.iloc[i]['SMA_50'] and data.iloc[i-1]['SMA_20'] >= data.iloc[i-1]['SMA_50']:
                    action = 'SELL'
                    confidence = 70
                else:
                    action = 'HOLD'
                    confidence = 50

            # Execute trades
            if action == 'BUY' and cash >= current_price * 10 and confidence > 60:
                shares = min(int(cash / current_price), 10)
                cost = shares * current_price
                cash -= cost
                holdings += shares
                trades.append({
                    'day': i,
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'confidence': confidence
                })

            elif action == 'SELL' and holdings > 0 and confidence > 60:
                shares = min(holdings, 10)
                revenue = shares * current_price
                cash += revenue
                holdings -= shares
                trades.append({
                    'day': i,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares,
                    'confidence': confidence
                })

            # Calculate portfolio value
            portfolio_value = cash + (holdings * current_price)
            portfolio_values.append(portfolio_value)

            # Update peak and drawdown
            if portfolio_value > peak_value:
                peak_value = portfolio_value
            drawdown = (peak_value - portfolio_value) / peak_value
            max_drawdown = max(max_drawdown, drawdown)

        # Final calculations
        final_value = cash + (holdings * data.iloc[-1]['Close'])
        total_return = final_value - self.initial_balance
        total_return_pct = (total_return / self.initial_balance) * 100

        winning_trades = sum(1 for t in trades if t['action'] == 'SELL')
        total_trades = len([t for t in trades if t['action'] == 'SELL'])

        # Calculate daily returns for Sharpe ratio
        daily_returns = []
        for i in range(1, len(portfolio_values)):
            if portfolio_values[i-1] > 0:
                daily_returns.append((portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1])

        sharpe_ratio = 0
        if len(daily_returns) > 1 and np.std(daily_returns) > 0:
            sharpe_ratio = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(252)

        return {
            "initial_balance": self.initial_balance,
            "final_value": round(final_value, 2),
            "total_return": round(total_return, 2),
            "total_return_pct": round(total_return_pct, 2),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "total_trades": len(trades),
            "winning_trades": winning_trades,
            "win_rate": round((winning_trades / total_trades * 100) if total_trades > 0 else 0, 2),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "trades": trades[:20],  # Return first 20 trades
            "portfolio_values": [round(v, 2) for v in portfolio_values[::10]]  # Sample every 10th value
        }

    def get_performance_report(self, backtest_result: Dict) -> Dict:
        if backtest_result.get("status") != "success":
            return backtest_result

        return {
            "report_summary": {
                "strategy": backtest_result["strategy"],
                "symbol": backtest_result["symbol"],
                "period": backtest_result["period"],
                "total_return_pct": backtest_result["total_return_pct"],
                "max_drawdown_pct": backtest_result["max_drawdown_pct"],
                "sharpe_ratio": backtest_result["sharpe_ratio"],
                "win_rate": backtest_result["win_rate"],
                "total_trades": backtest_result["total_trades"]
            },
            "grade": self._calculate_grade(backtest_result),
            "recommendations": self._generate_recommendations(backtest_result)
        }

    def _calculate_grade(self, result: Dict) -> str:
        score = 0

        if result["total_return_pct"] > 20:
            score += 3
        elif result["total_return_pct"] > 10:
            score += 2
        elif result["total_return_pct"] > 0:
            score += 1

        if result["max_drawdown_pct"] < 10:
            score += 3
        elif result["max_drawdown_pct"] < 20:
            score += 2
        elif result["max_drawdown_pct"] < 30:
            score += 1

        if result["sharpe_ratio"] > 1.5:
            score += 3
        elif result["sharpe_ratio"] > 1.0:
            score += 2
        elif result["sharpe_ratio"] > 0.5:
            score += 1

        if result["win_rate"] > 60:
            score += 2
        elif result["win_rate"] > 50:
            score += 1

        grades = {10: "A+", 9: "A", 8: "A-", 7: "B+", 6: "B", 5: "B-", 4: "C+", 3: "C", 2: "C-", 1: "D", 0: "F"}
        return grades.get(score, "F")

    def _generate_recommendations(self, result: Dict) -> List[str]:
        recommendations = []

        if result["max_drawdown_pct"] > 20:
            recommendations.append("Consider tighter stop-losses to reduce drawdown")

        if result["win_rate"] < 50:
            recommendations.append("Strategy win rate is below 50%. Consider improving entry criteria")

        if result["sharpe_ratio"] < 1.0:
            recommendations.append("Risk-adjusted returns are low. Consider reducing position sizes")

        if result["total_return_pct"] < 0:
            recommendations.append("Strategy is unprofitable. Review and optimize parameters")

        if not recommendations:
            recommendations.append("Strategy performance is satisfactory. Continue monitoring")

        return recommendations

backtest_simulator = BacktestSimulator()
