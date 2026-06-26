"""Database models for AI-Trader-Pro"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    trades = relationship("Trade", back_populates="user")
    predictions = relationship("AIPrediction", back_populates="user")
    performance = relationship("Performance", back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    virtual_balance = Column(Float, default=1000000.0)
    total_invested = Column(Float, default=0.0)
    total_profit_loss = Column(Float, default=0.0)
    total_profit_loss_pct = Column(Float, default=0.0)
    win_count = Column(Integer, default=0)
    loss_count = Column(Integer, default=0)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    current_drawdown = Column(Float, default=0.0)
    peak_value = Column(Float, default=1000000.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="portfolio")
    holdings = relationship("Holding", back_populates="portfolio")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(20), nullable=False)
    quantity = Column(Integer, default=0)
    avg_buy_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_pct = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="holdings")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    profit_loss = Column(Float, default=0.0)
    profit_loss_pct = Column(Float, default=0.0)
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED, STOPPED
    ai_confidence = Column(Float, nullable=True)
    ai_recommendation = Column(String(10), nullable=True)
    trade_date = Column(DateTime, default=datetime.utcnow)
    closed_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="trades")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    current_price = Column(Float, nullable=False)
    indicators = Column(JSON, nullable=True)
    model_version = Column(String(50), nullable=True)
    executed = Column(Boolean, default=False)
    result = Column(String(20), nullable=True)  # CORRECT, INCORRECT, PENDING
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")

class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    portfolio_value = Column(Float, default=0.0)
    daily_pnl = Column(Float, default=0.0)
    daily_pnl_pct = Column(Float, default=0.0)
    total_return = Column(Float, default=0.0)
    total_return_pct = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)

    user = relationship("User", back_populates="performance")

class MarketDataCache(Base):
    __tablename__ = "market_data_cache"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow)
