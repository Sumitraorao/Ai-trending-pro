"""Configuration settings for AI-Trader-Pro"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "AI-Trader-Pro"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trader_pro.db")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Trading
    STARTING_BALANCE: float = 1000000.0  # INR
    MAX_DAILY_LOSS_PCT: float = 2.0
    MAX_SINGLE_TRADE_PCT: float = 5.0
    STOP_TRADING_AFTER_LOSS_PCT: float = 10.0

    # AI
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")
    PREDICTION_THRESHOLD: float = 0.6

    # Market Data
    DEFAULT_TICKERS: list = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    DATA_CACHE_MINUTES: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
