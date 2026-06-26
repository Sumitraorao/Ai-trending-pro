"""Market data API routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database.database import get_db
from data.market_data import market_engine
from data.indicators import indicators
from api.auth import get_current_active_user
from database.models import User

router = APIRouter(prefix="/market", tags=["Market Data"])

@router.get("/price/{symbol}")
def get_price(symbol: str, db: Session = Depends(get_db)):
    try:
        price = market_engine.get_current_price(symbol)
        info = market_engine.get_stock_info(symbol)
        return {
            "status": "success",
            "symbol": symbol,
            "current_price": price,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/historical/{symbol}")
def get_historical(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    db: Session = Depends(get_db)
):
    try:
        data = market_engine.get_stock_data(symbol, period=period, interval=interval, db=db)

        # Calculate indicators
        data_with_indicators = indicators.calculate_all(data)

        # Convert to list of dicts
        records = []
        for _, row in data_with_indicators.iterrows():
            record = {}
            for col in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']:
                if col in row:
                    val = row[col]
                    if hasattr(val, 'isoformat'):
                        record[col.lower()] = val.isoformat()
                    else:
                        record[col.lower()] = float(val) if pd.notna(val) else None
            records.append(record)

        return {
            "status": "success",
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(records),
            "data": records
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/indicators/{symbol}")
def get_indicators(
    symbol: str,
    period: str = "3mo",
    db: Session = Depends(get_db)
):
    try:
        data = market_engine.get_stock_data(symbol, period=period, interval="1d", db=db)
        data_with_indicators = indicators.calculate_all(data)
        signals = indicators.get_latest_signals(data_with_indicators)

        return {
            "status": "success",
            "symbol": symbol,
            "signals": signals
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/multiple")
def get_multiple_prices(symbols: str, db: Session = Depends(get_db)):
    symbol_list = [s.strip() for s in symbols.split(",")]
    try:
        prices = market_engine.get_multiple_prices(symbol_list)
        return {
            "status": "success",
            "prices": prices
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search")
def search_stocks(query: str):
    """Search for stock symbols"""
    # Simplified search - in production, use a proper search API
    popular_stocks = {
        "RELIANCE": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "INFY": "INFY.NS",
        "HDFCBANK": "HDFCBANK.NS",
        "ICICIBANK": "ICICIBANK.NS",
        "SBIN": "SBIN.NS",
        "BHARTIARTL": "BHARTIARTL.NS",
        "ITC": "ITC.NS",
        "KOTAKBANK": "KOTAKBANK.NS",
        "LT": "LT.NS",
        "HINDUNILVR": "HINDUNILVR.NS",
        "AXISBANK": "AXISBANK.NS",
        "BAJFINANCE": "BAJFINANCE.NS",
        "ASIANPAINT": "ASIANPAINT.NS",
        "MARUTI": "MARUTI.NS",
        "TATAMOTORS": "TATAMOTORS.NS",
        "WIPRO": "WIPRO.NS",
        "SUNPHARMA": "SUNPHARMA.NS",
        "ADANIENT": "ADANIENT.NS",
        "TITAN": "TITAN.NS"
    }

    results = []
    query_upper = query.upper()
    for name, symbol in popular_stocks.items():
        if query_upper in name or query_upper in symbol:
            results.append({"name": name, "symbol": symbol})

    return {"status": "success", "results": results}
