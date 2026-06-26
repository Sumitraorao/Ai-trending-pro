"""AI Prediction service"""
from typing import Dict, Optional
from data.market_data import market_engine
from data.indicators import indicators
from ai.model import trading_model
from sqlalchemy.orm import Session
from database.models import AIPrediction
from config import settings

class AIPredictor:
    def __init__(self):
        self.model = trading_model

    def predict(self, symbol: str, db: Session = None) -> Dict:
        try:
            # Fetch market data
            data = market_engine.get_stock_data(symbol, period="6mo", interval="1d", db=db)

            # Calculate indicators
            data_with_indicators = indicators.calculate_all(data)

            # Get latest signals
            signals = indicators.get_latest_signals(data_with_indicators)

            # AI prediction
            prediction = self.model.predict(data_with_indicators)

            # Combine technical and ML signals
            ml_action = prediction.get('action', 'HOLD')
            ml_confidence = prediction.get('confidence', 50)

            # Adjust confidence based on technical signals
            tech_boost = 0
            if signals.get('rsi') and signals['rsi'] < 30 and ml_action == 'BUY':
                tech_boost += 10
            elif signals.get('rsi') and signals['rsi'] > 70 and ml_action == 'SELL':
                tech_boost += 10

            if 'MACD Bullish Crossover' in signals.get('interpretation', []) and ml_action == 'BUY':
                tech_boost += 5
            elif 'MACD Bearish Crossover' in signals.get('interpretation', []) and ml_action == 'SELL':
                tech_boost += 5

            final_confidence = min(ml_confidence + tech_boost, 99)

            result = {
                "symbol": symbol,
                "action": ml_action,
                "confidence": round(final_confidence, 2),
                "stop_loss": prediction.get('stop_loss'),
                "target": prediction.get('target'),
                "current_price": prediction.get('current_price'),
                "technical_signals": signals['interpretation'],
                "indicators": {
                    "rsi": signals.get('rsi'),
                    "macd": signals.get('macd'),
                    "sma_20": signals.get('sma_20'),
                    "sma_50": signals.get('sma_50'),
                    "bb_upper": signals.get('bb_upper'),
                    "bb_lower": signals.get('bb_lower'),
                    "atr": signals.get('atr')
                },
                "ml_probabilities": prediction.get('probabilities', {})
            }

            # Save prediction to database
            if db:
                ai_pred = AIPrediction(
                    symbol=symbol,
                    action=ml_action,
                    confidence=final_confidence,
                    stop_loss=prediction.get('stop_loss'),
                    target=prediction.get('target'),
                    current_price=prediction.get('current_price'),
                    indicators=result['indicators'],
                    model_version="v1.0"
                )
                db.add(ai_pred)
                db.commit()

            return result

        except Exception as e:
            return {
                "status": "error",
                "symbol": symbol,
                "message": str(e),
                "action": "HOLD",
                "confidence": 0
            }

    def batch_predict(self, symbols: list, db: Session = None) -> Dict:
        predictions = {}
        for symbol in symbols:
            predictions[symbol] = self.predict(symbol, db)
        return predictions

ai_predictor = AIPredictor()
