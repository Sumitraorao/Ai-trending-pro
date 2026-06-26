"""Risk management system"""
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from config import settings

@dataclass
class RiskCheck:
    passed: bool
    reason: str
    risk_level: str  # LOW, MEDIUM, HIGH

class RiskManager:
    def __init__(self):
        self.max_daily_loss_pct = settings.MAX_DAILY_LOSS_PCT
        self.max_single_trade_pct = settings.MAX_SINGLE_TRADE_PCT
        self.stop_trading_after_loss_pct = settings.STOP_TRADING_AFTER_LOSS_PCT
        self.daily_trades: List[Dict] = []
        self.daily_pnl = 0.0
        self.last_reset = datetime.utcnow().date()
        self.trading_enabled = True
        self.consecutive_losses = 0
        self.max_consecutive_losses = 3

    def _reset_daily(self):
        today = datetime.utcnow().date()
        if today != self.last_reset:
            self.daily_trades = []
            self.daily_pnl = 0.0
            self.last_reset = today
            self.consecutive_losses = 0
            self.trading_enabled = True

    def check_trade(self, portfolio_value: float, trade_amount: float, 
                   symbol: str, action: str, current_holdings: Dict) -> RiskCheck:
        self._reset_daily()

        # Check if trading is enabled
        if not self.trading_enabled:
            return RiskCheck(
                passed=False,
                reason="Trading halted due to excessive losses. Manual reset required.",
                risk_level="HIGH"
            )

        # Check single trade size
        trade_pct = (trade_amount / portfolio_value) * 100
        if trade_pct > self.max_single_trade_pct:
            return RiskCheck(
                passed=False,
                reason=f"Trade size {trade_pct:.2f}% exceeds maximum {self.max_single_trade_pct}%",
                risk_level="HIGH"
            )

        # Check daily loss limit
        if self.daily_pnl < -(portfolio_value * self.max_daily_loss_pct / 100):
            return RiskCheck(
                passed=False,
                reason=f"Daily loss limit of {self.max_daily_loss_pct}% reached",
                risk_level="HIGH"
            )

        # Check consecutive losses
        if self.consecutive_losses >= self.max_consecutive_losses:
            return RiskCheck(
                passed=False,
                reason=f"{self.max_consecutive_losses} consecutive losses. Trading paused.",
                risk_level="HIGH"
            )

        # Check portfolio concentration
        if action == "BUY" and symbol in current_holdings:
            current_value = current_holdings[symbol].get('total_value', 0)
            new_value = current_value + trade_amount
            concentration = (new_value / portfolio_value) * 100
            if concentration > 20:  # Max 20% in single stock
                return RiskCheck(
                    passed=False,
                    reason=f"Portfolio concentration would exceed 20% for {symbol}",
                    risk_level="MEDIUM"
                )

        # Check volatility (simplified)
        if trade_pct > 3:
            return RiskCheck(
                passed=True,
                reason="Trade approved with caution - large position size",
                risk_level="MEDIUM"
            )

        return RiskCheck(
            passed=True,
            reason="Trade approved",
            risk_level="LOW"
        )

    def record_trade_result(self, profit_loss: float):
        self._reset_daily()
        self.daily_pnl += profit_loss
        self.daily_trades.append({
            'time': datetime.utcnow(),
            'pnl': profit_loss
        })

        if profit_loss < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        # Check if we should stop trading
        if self.daily_pnl < -(1000000 * self.stop_trading_after_loss_pct / 100):
            self.trading_enabled = False

    def get_risk_metrics(self) -> Dict:
        self._reset_daily()

        total_trades = len(self.daily_trades)
        winning_trades = sum(1 for t in self.daily_trades if t['pnl'] > 0)

        return {
            "daily_pnl": round(self.daily_pnl, 2),
            "daily_pnl_pct": round((self.daily_pnl / 1000000) * 100, 2),
            "total_trades_today": total_trades,
            "winning_trades_today": winning_trades,
            "consecutive_losses": self.consecutive_losses,
            "trading_enabled": self.trading_enabled,
            "max_daily_loss_pct": self.max_daily_loss_pct,
            "max_single_trade_pct": self.max_single_trade_pct,
            "risk_level": self._calculate_overall_risk()
        }

    def _calculate_overall_risk(self) -> str:
        if not self.trading_enabled:
            return "CRITICAL"
        if self.consecutive_losses >= 2:
            return "HIGH"
        if self.daily_pnl < -10000:
            return "MEDIUM"
        return "LOW"

    def reset_trading(self):
        self.trading_enabled = True
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.daily_trades = []

risk_manager = RiskManager()
