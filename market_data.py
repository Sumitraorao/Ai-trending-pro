"""Market data fetching and caching"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import MarketDataCache
from config import settings
import json

class MarketDataEngine:
    def __init__(self):
        self.cache_duration = timedelta(minutes=settings.DATA_CACHE_MINUTES)

    def _get_cached_data(self, symbol: str, db: Session) -> Optional[pd.DataFrame]:
        cache = db.query(MarketDataCache).filter(MarketDataCache.symbol == symbol).first()
        if cache and (datetime.utcnow() - cache.cached_at) < self.cache_duration:
            df = pd.read_json(cache.data)
            return df
        return None

    def _set_cached_data(self, symbol: str, data: pd.DataFrame, db: Session):
        cache = db.query(MarketDataCache).filter(MarketDataCache.symbol == symbol).first()
        json_data = data.to_json(date_format='iso')
        if cache:
            cache.data = json_data
            cache.cached_at = datetime.utcnow()
        else:
            cache = MarketDataCache(symbol=symbol, data=json_data)
            db.add(cache)
        db.commit()

    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d", db: Session = None) -> pd.DataFrame:
        if db is None:
            db = SessionLocal()

        cached = self._get_cached_data(symbol, db)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            if data.empty:
                raise ValueError(f"No data found for {symbol}")

            data = data.reset_index()
            data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]

            self._set_cached_data(symbol, data, db)
            return data
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    def get_current_price(self, symbol: str) -> float:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            if price:
                return float(price)

            hist = ticker.history(period="1d")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            raise ValueError(f"Could not get current price for {symbol}")
        except Exception as e:
            raise Exception(f"Error getting current price for {symbol}: {str(e)}")

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        prices = {}
        for symbol in symbols:
            try:
                prices[symbol] = self.get_current_price(symbol)
            except:
                prices[symbol] = 0.0
        return prices

    def get_stock_info(self, symbol: str) -> dict:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol,
                "name": info.get('longName', info.get('shortName', symbol)),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "market_cap": info.get('marketCap'),
                "pe_ratio": info.get('trailingPE'),
                "dividend_yield": info.get('dividendYield'),
                "fifty_two_week_high": info.get('fiftyTwoWeekHigh'),
                "fifty_two_week_low": info.get('fiftyTwoWeekLow'),
                "avg_volume": info.get('averageVolume'),
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

market_engine = MarketDataEngine()
