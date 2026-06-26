"""Technical indicators calculation"""
import pandas as pd
import numpy as np
from typing import Dict

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
        return data['Close'].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int = 20) -> pd.Series:
        return data['Close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict:
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        return {
            "upper": upper,
            "middle": sma,
            "lower": lower
        }

    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=period).mean()

    @staticmethod
    def calculate_all(data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # RSI
        df['RSI'] = TechnicalIndicators.calculate_rsi(df)

        # MACD
        macd = TechnicalIndicators.calculate_macd(df)
        df['MACD'] = macd['macd']
        df['MACD_Signal'] = macd['signal']
        df['MACD_Histogram'] = macd['histogram']

        # Moving Averages
        df['SMA_20'] = TechnicalIndicators.calculate_sma(df, 20)
        df['SMA_50'] = TechnicalIndicators.calculate_sma(df, 50)
        df['EMA_20'] = TechnicalIndicators.calculate_ema(df, 20)
        df['EMA_50'] = TechnicalIndicators.calculate_ema(df, 50)

        # Bollinger Bands
        bb = TechnicalIndicators.calculate_bollinger_bands(df)
        df['BB_Upper'] = bb['upper']
        df['BB_Middle'] = bb['middle']
        df['BB_Lower'] = bb['lower']

        # ATR
        df['ATR'] = TechnicalIndicators.calculate_atr(df)

        return df

    @staticmethod
    def get_latest_signals(data: pd.DataFrame) -> Dict:
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest

        signals = {
            "rsi": round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else None,
            "macd": round(latest['MACD'], 4) if not pd.isna(latest['MACD']) else None,
            "macd_signal": round(latest['MACD_Signal'], 4) if not pd.isna(latest['MACD_Signal']) else None,
            "macd_histogram": round(latest['MACD_Histogram'], 4) if not pd.isna(latest['MACD_Histogram']) else None,
            "sma_20": round(latest['SMA_20'], 2) if not pd.isna(latest['SMA_20']) else None,
            "sma_50": round(latest['SMA_50'], 2) if not pd.isna(latest['SMA_50']) else None,
            "ema_20": round(latest['EMA_20'], 2) if not pd.isna(latest['EMA_20']) else None,
            "ema_50": round(latest['EMA_50'], 2) if not pd.isna(latest['EMA_50']) else None,
            "bb_upper": round(latest['BB_Upper'], 2) if not pd.isna(latest['BB_Upper']) else None,
            "bb_lower": round(latest['BB_Lower'], 2) if not pd.isna(latest['BB_Lower']) else None,
            "atr": round(latest['ATR'], 2) if not pd.isna(latest['ATR']) else None,
            "price": round(latest['Close'], 2),
            "volume": int(latest['Volume']) if not pd.isna(latest['Volume']) else 0,
        }

        # Generate signal interpretation
        signal_text = []

        if signals['rsi'] is not None:
            if signals['rsi'] < 30:
                signal_text.append("RSI Oversold (Bullish)")
            elif signals['rsi'] > 70:
                signal_text.append("RSI Overbought (Bearish)")

        if signals['macd'] is not None and signals['macd_signal'] is not None:
            if signals['macd'] > signals['macd_signal'] and prev['MACD'] <= prev['MACD_Signal']:
                signal_text.append("MACD Bullish Crossover")
            elif signals['macd'] < signals['macd_signal'] and prev['MACD'] >= prev['MACD_Signal']:
                signal_text.append("MACD Bearish Crossover")

        if signals['sma_20'] is not None and signals['sma_50'] is not None:
            if signals['sma_20'] > signals['sma_50']:
                signal_text.append("Golden Cross (Bullish)")
            else:
                signal_text.append("Death Cross (Bearish)")

        signals['interpretation'] = signal_text
        return signals

indicators = TechnicalIndicators()
