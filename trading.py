"""Trading API routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.database import get_db
from trading_engine.paper_trader import paper_trader
from trading_engine.risk_manager import risk_manager
from api.auth import get_current_active_user
from database.models import User

router = APIRouter(prefix="/trading", tags=["Trading"])

class BuyRequest(BaseModel):
    symbol: str
    quantity: int
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    ai_confidence: Optional[float] = None

class SellRequest(BaseModel):
    symbol: str
    quantity: int

@router.post("/buy")
def buy_stock(
    request: BuyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    result = paper_trader.buy_stock(
        user_id=current_user.id,
        symbol=request.symbol,
        quantity=request.quantity,
        stop_loss=request.stop_loss,
        target=request.target,
        ai_confidence=request.ai_confidence,
        db=db
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result

@router.post("/sell")
def sell_stock(
    request: SellRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    result = paper_trader.sell_stock(
        user_id=current_user.id,
        symbol=request.symbol,
        quantity=request.quantity,
        db=db
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result

@router.get("/portfolio")
def get_portfolio(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return paper_trader.get_portfolio(current_user.id, db)

@router.get("/history")
def get_trade_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return {
        "status": "success",
        "trades": paper_trader.get_trade_history(current_user.id, db, limit)
    }

@router.get("/risk")
def get_risk_metrics(
    current_user: User = Depends(get_current_active_user)
):
    return {
        "status": "success",
        "risk_metrics": risk_manager.get_risk_metrics()
    }

@router.post("/risk/reset")
def reset_risk(
    current_user: User = Depends(get_current_active_user)
):
    risk_manager.reset_trading()
    return {"status": "success", "message": "Risk metrics reset successfully"}
