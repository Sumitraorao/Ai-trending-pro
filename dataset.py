"""Dataset preparation for ML training"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, Dict
import yfinance as yf

class TradingDataset:
    def __init__(self, symbol: str, period: str = "2y", interval: str = "1d"):
        self.symbol = symbol
        self.period = period
        self.interval = interval
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = [
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50',
            'BB_Upper', 'BB_Lower', 'ATR',
            'Returns', 'Volatility', 'Volume_MA',
            'Price_to_SMA20', 'Price_to_SMA50',
            'Trend_5d', 'Trend_10d', 'Trend_20d'
        ]

    def fetch_data(self) -> pd.DataFrame:
        """Fetch historical data from Yahoo Finance"""
        ticker = yf.Ticker(self.symbol)
        data = ticker.history(period=self.period, interval=self.interval)
        data = data.reset_index()
        data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
        return data

    def calculate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators and features"""
        df = data.copy()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        ema_fast = df['Close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

        # Bollinger Bands
        sma_20 = df['Close'].rolling(window=20).mean()
        std_20 = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = sma_20 + (std_20 * 2)
        df['BB_Lower'] = sma_20 - (std_20 * 2)

        # ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()

        # Additional features
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Price_to_SMA20'] = df['Close'] / df['SMA_20']
        df['Price_to_SMA50'] = df['Close'] / df['SMA_50']
        df['Trend_5d'] = df['Close'].pct_change(5)
        df['Trend_10d'] = df['Close'].pct_change(10)
        df['Trend_20d'] = df['Close'].pct_change(20)

        return df

    def create_labels(self, data: pd.DataFrame, forward_days: int = 5, threshold: float = 0.02) -> pd.Series:
        """Create labels for supervised learning"""
        future_returns = data['Close'].shift(-forward_days) / data['Close'] - 1

        labels = pd.Series(index=data.index, dtype='object')
        labels[future_returns > threshold] = 'BUY'
        labels[future_returns < -threshold] = 'SELL'
        labels[(future_returns >= -threshold) & (future_returns <= threshold)] = 'HOLD'

        return labels

    def prepare_dataset(self, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Prepare complete dataset for training"""
        # Fetch and process data
        raw_data = self.fetch_data()
        data = self.calculate_features(raw_data)
        data['Label'] = self.create_labels(data)

        # Drop NaN values
        data = data.dropna()

        if len(data) < 100:
            raise ValueError(f"Insufficient data. Only {len(data)} rows available after processing.")

        # Split features and labels
        X = data[self.feature_columns].fillna(0)
        y = data['Label']

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)

        # Split into train and test
        split_idx = int(len(X) * (1 - test_size))
        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_train = y_encoded[:split_idx]
        y_test = y_encoded[split_idx:]

        # Scale features
        X_train_scaled = pd.DataFrame(
            self.scaler.fit_transform(X_train),
            columns=self.feature_columns,
            index=X_train.index
        )
        X_test_scaled = pd.DataFrame(
            self.scaler.transform(X_test),
            columns=self.feature_columns,
            index=X_test.index
        )

        return X_train_scaled, X_test_scaled, pd.Series(y_train), pd.Series(y_test)

    def get_feature_importance(self, model) -> Dict:
        """Get feature importance from trained model"""
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(self.feature_columns, model.feature_importances_))
            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        return {}

    def inverse_transform_labels(self, labels):
        """Convert encoded labels back to original"""
        return self.label_encoder.inverse_transform(labels)
