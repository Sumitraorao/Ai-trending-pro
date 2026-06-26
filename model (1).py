"""AI Model architecture for trading predictions"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple, Optional
import pickle
import os
from config import settings

class TradingModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50',
            'BB_Upper', 'BB_Lower', 'ATR',
            'Returns', 'Volatility', 'Volume_MA'
        ]
        self.model_path = settings.MODEL_PATH
        os.makedirs(self.model_path, exist_ok=True)

    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Calculate returns
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()

        # Price relative to moving averages
        df['Price_to_SMA20'] = df['Close'] / df['SMA_20']
        df['Price_to_SMA50'] = df['Close'] / df['SMA_50']

        # Trend features
        df['Trend_5d'] = df['Close'].pct_change(5)
        df['Trend_10d'] = df['Close'].pct_change(10)
        df['Trend_20d'] = df['Close'].pct_change(20)

        return df

    def _create_labels(self, data: pd.DataFrame, forward_days: int = 5, threshold: float = 0.02) -> pd.Series:
        future_returns = data['Close'].shift(-forward_days) / data['Close'] - 1

        labels = pd.Series(index=data.index, dtype='object')
        labels[future_returns > threshold] = 'BUY'
        labels[future_returns < -threshold] = 'SELL'
        labels[(future_returns >= -threshold) & (future_returns <= threshold)] = 'HOLD'

        return labels

    def train(self, data: pd.DataFrame) -> Dict:
        df = self._prepare_features(data)
        df['Label'] = self._create_labels(df)

        # Drop NaN values
        df = df.dropna()

        if len(df) < 100:
            return {"status": "error", "message": "Insufficient data for training"}

        X = df[self.feature_columns].fillna(0)
        y = df['Label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train ensemble model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train_scaled, y_train)

        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)

        # Feature importance
        importance = dict(zip(self.feature_columns, self.model.feature_importances_))

        # Save model
        self.save_model()

        return {
            "status": "success",
            "train_accuracy": round(train_score * 100, 2),
            "test_accuracy": round(test_score * 100, 2),
            "feature_importance": {k: round(v, 4) for k, v in sorted(importance.items(), key=lambda x: x[1], reverse=True)},
            "samples_trained": len(X_train),
            "samples_tested": len(X_test)
        }

    def predict(self, data: pd.DataFrame) -> Dict:
        if self.model is None:
            loaded = self.load_model()
            if not loaded:
                return {"status": "error", "message": "No trained model available"}

        df = self._prepare_features(data)
        latest = df.iloc[-1:][self.feature_columns].fillna(0)
        latest_scaled = self.scaler.transform(latest)

        prediction = self.model.predict(latest_scaled)[0]
        probabilities = self.model.predict_proba(latest_scaled)[0]

        confidence = max(probabilities) * 100

        current_price = data['Close'].iloc[-1]
        atr = data['ATR'].iloc[-1] if 'ATR' in data.columns else current_price * 0.02

        stop_loss = round(current_price - (2 * atr), 2) if prediction == 'BUY' else round(current_price + (2 * atr), 2)
        target = round(current_price + (3 * atr), 2) if prediction == 'BUY' else round(current_price - (3 * atr), 2)

        return {
            "status": "success",
            "action": prediction,
            "confidence": round(confidence, 2),
            "stop_loss": stop_loss,
            "target": target,
            "current_price": round(current_price, 2),
            "probabilities": {
                cls: round(prob * 100, 2) 
                for cls, prob in zip(self.model.classes_, probabilities)
            }
        }

    def save_model(self):
        if self.model:
            with open(f"{self.model_path}/trading_model.pkl", "wb") as f:
                pickle.dump(self.model, f)
            with open(f"{self.model_path}/scaler.pkl", "wb") as f:
                pickle.dump(self.scaler, f)

    def load_model(self) -> bool:
        model_file = f"{self.model_path}/trading_model.pkl"
        scaler_file = f"{self.model_path}/scaler.pkl"

        if os.path.exists(model_file) and os.path.exists(scaler_file):
            with open(model_file, "rb") as f:
                self.model = pickle.load(f)
            with open(scaler_file, "rb") as f:
                self.scaler = pickle.load(f)
            return True
        return False

trading_model = TradingModel()
