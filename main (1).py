"""AI-Trader-Pro Backend - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from database.database import init_db
from api import auth, market, trading, portfolio, ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 AI-Trader-Pro Backend Starting...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 AI-Trader-Pro Backend Shutting down...")

app = FastAPI(
    title="AI-Trader-Pro API",
    description="Autonomous AI Trading Assistant - Paper Trading Only",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow all origins for now (change in production)
# In production, replace with your actual Vercel URL
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
]

# Add Vercel URL from environment variable
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")

# Add custom frontend URL from env
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(market.router)
app.include_router(trading.router)
app.include_router(portfolio.router)
app.include_router(ai.router)

@app.get("/")
def root():
    return {
        "message": "AI-Trader-Pro API",
        "version": "1.0.0",
        "status": "operational",
        "mode": "PAPER TRADING ONLY - No real money",
        "docs": "/docs",
        "allowed_origins": allowed_origins
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-trader-pro"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
