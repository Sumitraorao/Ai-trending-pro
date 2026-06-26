"""AI Prediction API routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from ai.predictor import ai_predictor
from ai.strategy import strategy_manager
from data.market_data import market_engine
from data.indicators import indicators
from api.auth import get_current_active_user, get_current_user
from database.models import User
from typing import List

router = APIRouter(prefix="/ai", tags=["AI Predictions"])

@router.get("/predict/{symbol}")
def predict(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        prediction = ai_predictor.predict(symbol, db)

        if prediction.get("status") == "error":
            raise HTTPException(status_code=400, detail=prediction.get("message", "Prediction failed"))

        return {
            "status": "success",
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/predict/batch")
def batch_predict(
    symbols: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    symbol_list = [s.strip() for s in symbols.split(",")]
    try:
        predictions = ai_predictor.batch_predict(symbol_list, db)
        return {
            "status": "success",
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/strategy/{symbol}")
def get_strategy_signal(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        data = market_engine.get_stock_data(symbol, period="3mo", interval="1d", db=db)
        data_with_indicators = indicators.calculate_all(data)
        signals = indicators.get_latest_signals(data_with_indicators)
        signals['symbol'] = symbol

        combined = strategy_manager.get_combined_signal(signals)

        return {
            "status": "success",
            "symbol": symbol,
            "combined_signal": combined,
            "technical_indicators": signals
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
def get_ai_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get AI system status"""
    return {
        "status": "success",
        "ai_status": {
            "model_loaded": True,
            "model_version": "v1.0",
            "strategies_active": ["RSI", "MACD", "Moving Average", "Ensemble ML"],
            "prediction_accuracy": "N/A - requires historical evaluation",
            "last_training": "N/A - train via /ai/train",
            "system_health": "operational"
        }
    }

@router.post("/train/{symbol}")
def train_model(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Train AI model on historical data for a symbol"""
    try:
        from ai.model import trading_model
        data = market_engine.get_stock_data(symbol, period="2y", interval="1d", db=db)
        data_with_indicators = indicators.calculate_all(data)

        result = trading_model.train(data_with_indicators)

        return {
            "status": "success",
            "symbol": symbol,
            "training_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
