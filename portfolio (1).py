"""Portfolio API routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from database.models import User, Portfolio, Trade, Performance
from trading_engine.paper_trader import paper_trader
from api.auth import get_current_active_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/status")
def get_portfolio_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return paper_trader.get_portfolio(current_user.id, db)

@router.get("/summary")
def get_portfolio_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    portfolio = paper_trader.get_portfolio(current_user.id, db)

    # Get recent performance
    recent_performance = db.query(Performance).filter(
        Performance.user_id == current_user.id
    ).order_by(Performance.date.desc()).limit(30).all()

    performance_data = []
    for perf in recent_performance:
        performance_data.append({
            "date": perf.date.isoformat() if perf.date else None,
            "portfolio_value": perf.portfolio_value,
            "daily_pnl": perf.daily_pnl,
            "daily_pnl_pct": perf.daily_pnl_pct
        })

    return {
        "status": "success",
        "portfolio": portfolio,
        "performance_history": performance_data
    }

@router.get("/performance")
def get_performance_metrics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get trades in the period
    start_date = datetime.utcnow() - timedelta(days=days)
    trades = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.trade_date >= start_date
    ).all()

    closed_trades = [t for t in trades if t.status == "CLOSED"]

    if not closed_trades:
        return {
            "status": "success",
            "period_days": days,
            "message": "No closed trades in this period",
            "metrics": {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "avg_profit": 0,
                "avg_loss": 0,
                "profit_factor": 0,
                "total_pnl": 0
            }
        }

    winning_trades = [t for t in closed_trades if t.profit_loss and t.profit_loss > 0]
    losing_trades = [t for t in closed_trades if t.profit_loss and t.profit_loss <= 0]

    total_pnl = sum(t.profit_loss for t in closed_trades if t.profit_loss)
    avg_profit = sum(t.profit_loss for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t.profit_loss for t in losing_trades) / len(losing_trades) if losing_trades else 0

    gross_profit = sum(t.profit_loss for t in winning_trades if t.profit_loss)
    gross_loss = abs(sum(t.profit_loss for t in losing_trades if t.profit_loss))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    return {
        "status": "success",
        "period_days": days,
        "metrics": {
            "total_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round((len(winning_trades) / len(closed_trades)) * 100, 2),
            "avg_profit": round(avg_profit, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "total_pnl": round(total_pnl, 2),
            "largest_profit": round(max((t.profit_loss for t in winning_trades if t.profit_loss), default=0), 2),
            "largest_loss": round(min((t.profit_loss for t in losing_trades if t.profit_loss), default=0), 2)
        }
    }

@router.get("/holdings")
def get_holdings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    portfolio = paper_trader.get_portfolio(current_user.id, db)
    return {
        "status": "success",
        "holdings": portfolio.get("holdings", [])
    }
