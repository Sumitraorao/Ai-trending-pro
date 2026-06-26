"""Trading strategy definitions"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class TradeSignal:
    symbol: str
    action: SignalType
    confidence: float
    stop_loss: float
    target: float
    strategy_name: str
    reason: str

class BaseStrategy:
    def __init__(self, name: str):
        self.name = name

    def generate_signal(self, data: dict) -> TradeSignal:
        raise NotImplementedError

class RSIStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("RSI_Strategy")

    def generate_signal(self, indicators: dict) -> TradeSignal:
        rsi = indicators.get('rsi')
        price = indicators.get('price', 0)
        atr = indicators.get('atr', price * 0.02)

        if rsi is None:
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.HOLD,
                confidence=0,
                stop_loss=price * 0.95,
                target=price * 1.05,
                strategy_name=self.name,
                reason="Insufficient data"
            )

        if rsi < 30:
            confidence = min(90, 70 + (30 - rsi))
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.BUY,
                confidence=confidence,
                stop_loss=round(price - (2 * atr), 2),
                target=round(price + (3 * atr), 2),
                strategy_name=self.name,
                reason=f"RSI oversold at {rsi:.1f}"
            )
        elif rsi > 70:
            confidence = min(90, 70 + (rsi - 70))
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.SELL,
                confidence=confidence,
                stop_loss=round(price + (2 * atr), 2),
                target=round(price - (3 * atr), 2),
                strategy_name=self.name,
                reason=f"RSI overbought at {rsi:.1f}"
            )

        return TradeSignal(
            symbol=indicators.get('symbol', ''),
            action=SignalType.HOLD,
            confidence=50,
            stop_loss=round(price * 0.95, 2),
            target=round(price * 1.05, 2),
            strategy_name=self.name,
            reason=f"RSI neutral at {rsi:.1f}"
        )

class MACDStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MACD_Strategy")

    def generate_signal(self, indicators: dict) -> TradeSignal:
        macd = indicators.get('macd')
        signal = indicators.get('macd_signal')
        histogram = indicators.get('macd_histogram')
        price = indicators.get('price', 0)
        atr = indicators.get('atr', price * 0.02)

        if macd is None or signal is None:
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.HOLD,
                confidence=0,
                stop_loss=price * 0.95,
                target=price * 1.05,
                strategy_name=self.name,
                reason="Insufficient MACD data"
            )

        if macd > signal and histogram > 0:
            confidence = min(85, 60 + abs(histogram) * 100)
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.BUY,
                confidence=confidence,
                stop_loss=round(price - (2 * atr), 2),
                target=round(price + (3 * atr), 2),
                strategy_name=self.name,
                reason=f"MACD bullish: {macd:.4f} > {signal:.4f}"
            )
        elif macd < signal and histogram < 0:
            confidence = min(85, 60 + abs(histogram) * 100)
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.SELL,
                confidence=confidence,
                stop_loss=round(price + (2 * atr), 2),
                target=round(price - (3 * atr), 2),
                strategy_name=self.name,
                reason=f"MACD bearish: {macd:.4f} < {signal:.4f}"
            )

        return TradeSignal(
            symbol=indicators.get('symbol', ''),
            action=SignalType.HOLD,
            confidence=50,
            stop_loss=round(price * 0.95, 2),
            target=round(price * 1.05, 2),
            strategy_name=self.name,
            reason="MACD neutral"
        )

class MovingAverageStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MA_Strategy")

    def generate_signal(self, indicators: dict) -> TradeSignal:
        sma20 = indicators.get('sma_20')
        sma50 = indicators.get('sma_50')
        price = indicators.get('price', 0)
        atr = indicators.get('atr', price * 0.02)

        if sma20 is None or sma50 is None:
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.HOLD,
                confidence=0,
                stop_loss=price * 0.95,
                target=price * 1.05,
                strategy_name=self.name,
                reason="Insufficient MA data"
            )

        if sma20 > sma50:
            confidence = min(80, 60 + (sma20 - sma50) / price * 1000)
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.BUY,
                confidence=confidence,
                stop_loss=round(price - (2 * atr), 2),
                target=round(price + (3 * atr), 2),
                strategy_name=self.name,
                reason=f"Golden Cross: SMA20 ({sma20:.2f}) > SMA50 ({sma50:.2f})"
            )
        else:
            confidence = min(80, 60 + (sma50 - sma20) / price * 1000)
            return TradeSignal(
                symbol=indicators.get('symbol', ''),
                action=SignalType.SELL,
                confidence=confidence,
                stop_loss=round(price + (2 * atr), 2),
                target=round(price - (3 * atr), 2),
                strategy_name=self.name,
                reason=f"Death Cross: SMA20 ({sma20:.2f}) < SMA50 ({sma50:.2f})"
            )

class StrategyManager:
    def __init__(self):
        self.strategies = [
            RSIStrategy(),
            MACDStrategy(),
            MovingAverageStrategy()
        ]

    def get_combined_signal(self, indicators: dict) -> Dict:
        signals = []
        for strategy in self.strategies:
            signal = strategy.generate_signal(indicators)
            signals.append(signal)

        # Weighted voting
        buy_votes = sum(s.confidence for s in signals if s.action == SignalType.BUY)
        sell_votes = sum(s.confidence for s in signals if s.action == SignalType.SELL)
        hold_votes = sum(s.confidence for s in signals if s.action == SignalType.HOLD)

        total = buy_votes + sell_votes + hold_votes
        if total == 0:
            total = 1

        buy_pct = buy_votes / total * 100
        sell_pct = sell_votes / total * 100
        hold_pct = hold_votes / total * 100

        if buy_pct > sell_pct and buy_pct > hold_pct:
            final_action = SignalType.BUY
            final_confidence = buy_pct
        elif sell_pct > buy_pct and sell_pct > hold_pct:
            final_action = SignalType.SELL
            final_confidence = sell_pct
        else:
            final_action = SignalType.HOLD
            final_confidence = hold_pct

        price = indicators.get('price', 0)
        atr = indicators.get('atr', price * 0.02)

        return {
            "action": final_action.value,
            "confidence": round(final_confidence, 2),
            "stop_loss": round(price - (2 * atr), 2) if final_action == SignalType.BUY else round(price + (2 * atr), 2),
            "target": round(price + (3 * atr), 2) if final_action == SignalType.BUY else round(price - (3 * atr), 2),
            "strategy_signals": [
                {
                    "strategy": s.strategy_name,
                    "action": s.action.value,
                    "confidence": round(s.confidence, 2),
                    "reason": s.reason
                } for s in signals
            ],
            "vote_distribution": {
                "buy": round(buy_pct, 2),
                "sell": round(sell_pct, 2),
                "hold": round(hold_pct, 2)
            }
        }

strategy_manager = StrategyManager()
