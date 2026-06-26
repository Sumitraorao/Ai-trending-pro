# 🤖 AI-Trader-Pro

**Autonomous AI Trading Assistant with Paper Trading**

AI-Trader-Pro is a complete full-stack AI trading system that analyzes market data, generates BUY/SELL/HOLD signals using machine learning, manages risk, and executes trades with virtual money (paper trading). Built for learning and strategy development before real trading.

> ⚠️ **IMPORTANT**: This system uses PAPER TRADING ONLY. No real money is involved. Real broker integration is available as a placeholder for future use.

---

## ✨ Features

### 🤖 AI Prediction Engine
- Machine Learning models (Random Forest, Gradient Boosting) for signal generation
- Technical indicators: RSI, MACD, Moving Averages, Bollinger Bands, ATR
- Ensemble strategy combining multiple signals
- Confidence scores for each prediction
- Auto stop-loss and target calculation

### 📊 Trading Dashboard
- Real-time portfolio overview
- Virtual balance tracking (₹10,00,000 starting)
- P&L tracking with win rate
- Interactive charts with Chart.js
- Dark theme professional trading UI

### 🛡️ Risk Management
- Maximum daily loss limit (2%)
- Maximum single trade size (5%)
- Circuit breaker after consecutive losses
- Portfolio concentration limits
- Automatic trading halt on excessive losses

### 📈 Backtesting
- Historical strategy testing
- Performance reports with Sharpe ratio
- Maximum drawdown analysis
- Win rate and profit factor calculation
- Strategy grading system

### 🧠 Reinforcement Learning Ready
- Gymnasium-compatible trading environment
- Reward system based on profit/loss
- Configurable risk parameters
- Stable Baselines3 integration structure

### 🔐 Security
- JWT authentication
- Password hashing with bcrypt
- Protected API routes
- SQLite for local development (PostgreSQL ready)

---

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework
- **Tailwind CSS** - Utility-first styling
- **Chart.js** - Interactive charts
- **Lucide React** - Icons

### Backend
- **FastAPI** - High-performance Python API
- **SQLAlchemy** - ORM for database
- **yfinance** - Market data from Yahoo Finance
- **scikit-learn** - Machine learning
- **PyTorch** - Deep learning ready
- **Stable Baselines3** - RL framework

### Database
- **SQLite** - Local development
- **PostgreSQL** - Production ready

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AI-Trader-Pro
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate
# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The backend will start at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will start at `http://localhost:3000`

### 4. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `SECRET_KEY` - Change this in production!
- `DATABASE_URL` - SQLite for local, PostgreSQL for production
- `NEXT_PUBLIC_API_URL` - Backend URL

---

## 📁 Project Structure

```
AI-Trader-Pro/
├── frontend/                 # Next.js Frontend
│   ├── app/                  # App Router
│   │   ├── dashboard/        # Dashboard page
│   │   ├── trading/          # Trading terminal
│   │   ├── portfolio/        # Portfolio page
│   │   ├── login/            # Auth page
│   │   ├── layout.jsx        # Root layout
│   │   └── page.jsx          # Landing page
│   ├── components/           # React components
│   │   ├── Navbar.jsx
│   │   ├── TradingChart.jsx
│   │   ├── AIStatus.jsx
│   │   ├── PortfolioCard.jsx
│   │   ├── TradeHistory.jsx
│   │   └── RiskMeter.jsx
│   ├── lib/
│   │   └── api.js            # API client
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                  # FastAPI Backend
│   ├── main.py               # Application entry
│   ├── config.py             # Settings
│   ├── requirements.txt
│   ├── api/                  # API routes
│   │   ├── auth.py           # Authentication
│   │   ├── market.py         # Market data
│   │   ├── trading.py        # Trading operations
│   │   ├── portfolio.py      # Portfolio management
│   │   └── ai.py             # AI predictions
│   ├── ai/                   # AI modules
│   │   ├── model.py          # ML models
│   │   ├── predictor.py      # Prediction service
│   │   ├── strategy.py       # Trading strategies
│   │   └── reinforcement.py  # RL environment
│   ├── trading_engine/       # Trading logic
│   │   ├── paper_trader.py   # Virtual trading
│   │   ├── risk_manager.py   # Risk controls
│   │   └── simulator.py      # Backtesting
│   ├── data/                 # Data layer
│   │   ├── market_data.py    # Market data fetcher
│   │   └── indicators.py     # Technical indicators
│   ├── database/             # Database
│   │   ├── database.py       # Connection
│   │   └── models.py         # SQLAlchemy models
│   └── broker_api.py         # Broker integration placeholder
│
├── ml_training/              # ML Training scripts
│   ├── train_model.py        # Model training
│   ├── dataset.py            # Dataset preparation
│   └── backtest.py           # Backtesting script
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (returns JWT)
- `GET /auth/me` - Get current user

### Market Data
- `GET /market/price/{symbol}` - Current price
- `GET /market/historical/{symbol}` - Historical data
- `GET /market/indicators/{symbol}` - Technical indicators
- `GET /market/search?query={q}` - Stock search

### Trading
- `POST /trading/buy` - Buy stock
- `POST /trading/sell` - Sell stock
- `GET /trading/portfolio` - Portfolio status
- `GET /trading/history` - Trade history
- `GET /trading/risk` - Risk metrics

### AI
- `GET /ai/predict/{symbol}` - Get AI prediction
- `GET /ai/strategy/{symbol}` - Strategy signals
- `POST /ai/train/{symbol}` - Train model
- `GET /ai/status` - AI system status

---

## 🧠 AI Model Training

### Train a Model

```bash
cd backend

# Train for a specific stock
python -m ml_training.train_model --symbol RELIANCE.NS --model random_forest

# Or use gradient boosting
python -m ml_training.train_model --symbol TCS.NS --model gradient_boosting
```

### Run Backtest

```bash
# Test strategy on historical data
python -m ml_training.backtest --symbol RELIANCE.NS --start 2023-01-01 --end 2024-01-01 --strategy ml
```

---

## 🛡️ Risk Management Rules

1. **Maximum Daily Loss**: 2% of portfolio
2. **Maximum Single Trade**: 5% of portfolio
3. **Stop Trading After**: 10% cumulative loss
4. **Max Consecutive Losses**: 3 trades
5. **Portfolio Concentration**: Max 20% in single stock
6. **Auto Stop-Loss**: 2x ATR from entry

---

## 🏃 Running on Replit

1. Create a new Repl
2. Upload or copy all files
3. Install backend dependencies:
   ```bash
   cd backend && pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend && npm install
   ```
5. In one shell, run backend:
   ```bash
   cd backend && python main.py
   ```
6. In another shell, run frontend:
   ```bash
   cd frontend && npm run dev
   ```

---

## 🔄 Future Broker Integration

The system includes placeholder structures for:
- **Zerodha** (Kite Connect)
- **Upstox** (API v2)
- **Angel One** (SmartAPI)
- **Fyers** (API v3)

> ⚠️ Real trading is DISABLED by default. Enable only after thorough testing.

---

## ⚠️ Disclaimer

**This is for educational and paper trading purposes only.**

- Not financial advice
- Past performance doesn't guarantee future results
- Always do your own research
- Trading involves substantial risk of loss

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

Built with ❤️ for the trading community.
