"""Paper trading engine - virtual money trading"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Portfolio, Holding, Trade, Performance
from data.market_data import market_engine
from trading_engine.risk_manager import risk_manager
from config import settings

class PaperTrader:
    def __init__(self):
        self.starting_balance = settings.STARTING_BALANCE

    def get_or_create_portfolio(self, user_id: int, db: Session) -> Portfolio:
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                virtual_balance=self.starting_balance,
                peak_value=self.starting_balance
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
        return portfolio

    def buy_stock(self, user_id: int, symbol: str, quantity: int, 
                  stop_loss: Optional[float] = None, target: Optional[float] = None,
                  ai_confidence: Optional[float] = None, db: Session = None) -> Dict:
        try:
            portfolio = self.get_or_create_portfolio(user_id, db)

            # Get current price
            current_price = market_engine.get_current_price(symbol)
            total_cost = current_price * quantity

            # Check if enough balance
            if total_cost > portfolio.virtual_balance:
                return {
                    "status": "error",
                    "message": f"Insufficient balance. Required: ₹{total_cost:,.2f}, Available: ₹{portfolio.virtual_balance:,.2f}"
                }

            # Risk check
            holdings_dict = {h.symbol: {'total_value': h.total_value} for h in portfolio.holdings}
            portfolio_value = portfolio.virtual_balance + sum(h.total_value for h in portfolio.holdings)
            risk_check = risk_manager.check_trade(
                portfolio_value=portfolio_value,
                trade_amount=total_cost,
                symbol=symbol,
                action="BUY",
                current_holdings=holdings_dict
            )

            if not risk_check.passed:
                return {
                    "status": "error",
                    "message": f"Risk check failed: {risk_check.reason}",
                    "risk_level": risk_check.risk_level
                }

            # Execute trade
            portfolio.virtual_balance -= total_cost
            portfolio.total_invested += total_cost

            # Update or create holding
            holding = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id,
                Holding.symbol == symbol
            ).first()

            if holding:
                total_qty = holding.quantity + quantity
                holding.avg_buy_price = ((holding.avg_buy_price * holding.quantity) + (current_price * quantity)) / total_qty
                holding.quantity = total_qty
            else:
                holding = Holding(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    quantity=quantity,
                    avg_buy_price=current_price,
                    current_price=current_price
                )
                db.add(holding)

            # Record trade
            trade = Trade(
                user_id=user_id,
                symbol=symbol,
                action="BUY",
                quantity=quantity,
                entry_price=current_price,
                stop_loss=stop_loss,
                target=target,
                status="OPEN",
                ai_confidence=ai_confidence
            )
            db.add(trade)

            # Update holding value
            holding.current_price = current_price
            holding.total_value = holding.quantity * current_price
            holding.unrealized_pnl = (current_price - holding.avg_buy_price) * holding.quantity
            holding.unrealized_pnl_pct = ((current_price - holding.avg_buy_price) / holding.avg_buy_price) * 100

            portfolio.total_trades += 1
            portfolio.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(portfolio)
            db.refresh(trade)

            return {
                "status": "success",
                "message": f"Bought {quantity} shares of {symbol} at ₹{current_price:,.2f}",
                "trade_id": trade.id,
                "symbol": symbol,
                "quantity": quantity,
                "price": current_price,
                "total_cost": total_cost,
                "remaining_balance": portfolio.virtual_balance,
                "risk_level": risk_check.risk_level
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def sell_stock(self, user_id: int, symbol: str, quantity: int, db: Session = None) -> Dict:
        try:
            portfolio = self.get_or_create_portfolio(user_id, db)

            # Find holding
            holding = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id,
                Holding.symbol == symbol
            ).first()

            if not holding or holding.quantity < quantity:
                return {
                    "status": "error",
                    "message": f"Insufficient holdings. You have {holding.quantity if holding else 0} shares of {symbol}"
                }

            # Get current price
            current_price = market_engine.get_current_price(symbol)
            total_revenue = current_price * quantity

            # Calculate P&L
            cost_basis = holding.avg_buy_price * quantity
            profit_loss = total_revenue - cost_basis
            profit_loss_pct = (profit_loss / cost_basis) * 100

            # Risk check
            portfolio_value = portfolio.virtual_balance + sum(h.total_value for h in portfolio.holdings)
            risk_check = risk_manager.check_trade(
                portfolio_value=portfolio_value,
                trade_amount=total_revenue,
                symbol=symbol,
                action="SELL",
                current_holdings={}
            )

            # Execute trade
            portfolio.virtual_balance += total_revenue
            portfolio.total_profit_loss += profit_loss

            if profit_loss > 0:
                portfolio.win_count += 1
            else:
                portfolio.loss_count += 1

            # Update holding
            holding.quantity -= quantity
            if holding.quantity == 0:
                db.delete(holding)
            else:
                holding.total_value = holding.quantity * current_price
                holding.unrealized_pnl = (current_price - holding.avg_buy_price) * holding.quantity
                holding.unrealized_pnl_pct = ((current_price - holding.avg_buy_price) / holding.avg_buy_price) * 100

            # Record trade
            trade = Trade(
                user_id=user_id,
                symbol=symbol,
                action="SELL",
                quantity=quantity,
                entry_price=holding.avg_buy_price if holding else current_price,
                exit_price=current_price,
                profit_loss=profit_loss,
                profit_loss_pct=profit_loss_pct,
                status="CLOSED",
                closed_date=datetime.utcnow()
            )
            db.add(trade)

            # Update win rate
            if portfolio.total_trades > 0:
                portfolio.win_rate = (portfolio.win_count / portfolio.total_trades) * 100

            # Update peak and drawdown
            total_value = portfolio.virtual_balance + sum(
                h.total_value for h in db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
            )
            if total_value > portfolio.peak_value:
                portfolio.peak_value = total_value
            portfolio.current_drawdown = ((portfolio.peak_value - total_value) / portfolio.peak_value) * 100
            portfolio.max_drawdown = max(portfolio.max_drawdown, portfolio.current_drawdown)

            portfolio.total_trades += 1
            portfolio.updated_at = datetime.utcnow()

            # Record risk result
            risk_manager.record_trade_result(profit_loss)

            db.commit()
            db.refresh(trade)

            return {
                "status": "success",
                "message": f"Sold {quantity} shares of {symbol} at ₹{current_price:,.2f}",
                "trade_id": trade.id,
                "symbol": symbol,
                "quantity": quantity,
                "sell_price": current_price,
                "total_revenue": total_revenue,
                "profit_loss": round(profit_loss, 2),
                "profit_loss_pct": round(profit_loss_pct, 2),
                "new_balance": portfolio.virtual_balance,
                "risk_level": risk_check.risk_level
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_portfolio(self, user_id: int, db: Session) -> Dict:
        portfolio = self.get_or_create_portfolio(user_id, db)

        # Update current prices for all holdings
        total_holdings_value = 0
        holdings_data = []

        for holding in portfolio.holdings:
            try:
                current_price = market_engine.get_current_price(holding.symbol)
                holding.current_price = current_price
                holding.total_value = holding.quantity * current_price
                holding.unrealized_pnl = (current_price - holding.avg_buy_price) * holding.quantity
                holding.unrealized_pnl_pct = ((current_price - holding.avg_buy_price) / holding.avg_buy_price) * 100
                total_holdings_value += holding.total_value

                holdings_data.append({
                    "symbol": holding.symbol,
                    "quantity": holding.quantity,
                    "avg_buy_price": round(holding.avg_buy_price, 2),
                    "current_price": round(current_price, 2),
                    "total_value": round(holding.total_value, 2),
                    "unrealized_pnl": round(holding.unrealized_pnl, 2),
                    "unrealized_pnl_pct": round(holding.unrealized_pnl_pct, 2)
                })
            except:
                total_holdings_value += holding.total_value
                holdings_data.append({
                    "symbol": holding.symbol,
                    "quantity": holding.quantity,
                    "avg_buy_price": round(holding.avg_buy_price, 2),
                    "current_price": round(holding.current_price, 2),
                    "total_value": round(holding.total_value, 2),
                    "unrealized_pnl": round(holding.unrealized_pnl, 2),
                    "unrealized_pnl_pct": round(holding.unrealized_pnl_pct, 2)
                })

        total_value = portfolio.virtual_balance + total_holdings_value
        total_return = total_value - self.starting_balance
        total_return_pct = (total_return / self.starting_balance) * 100

        db.commit()

        return {
            "virtual_balance": round(portfolio.virtual_balance, 2),
            "total_invested": round(portfolio.total_invested, 2),
            "total_holdings_value": round(total_holdings_value, 2),
            "total_portfolio_value": round(total_value, 2),
            "total_return": round(total_return, 2),
            "total_return_pct": round(total_return_pct, 2),
            "total_profit_loss": round(portfolio.total_profit_loss, 2),
            "win_count": portfolio.win_count,
            "loss_count": portfolio.loss_count,
            "total_trades": portfolio.total_trades,
            "win_rate": round(portfolio.win_rate, 2),
            "max_drawdown": round(portfolio.max_drawdown, 2),
            "current_drawdown": round(portfolio.current_drawdown, 2),
            "holdings": holdings_data,
            "risk_metrics": risk_manager.get_risk_metrics()
        }

    def get_trade_history(self, user_id: int, db: Session, limit: int = 50) -> List[Dict]:
        trades = db.query(Trade).filter(Trade.user_id == user_id).order_by(Trade.trade_date.desc()).limit(limit).all()

        return [
            {
                "id": trade.id,
                "symbol": trade.symbol,
                "action": trade.action,
                "quantity": trade.quantity,
                "entry_price": round(trade.entry_price, 2),
                "exit_price": round(trade.exit_price, 2) if trade.exit_price else None,
                "stop_loss": trade.stop_loss,
                "target": trade.target,
                "profit_loss": round(trade.profit_loss, 2) if trade.profit_loss else None,
                "profit_loss_pct": round(trade.profit_loss_pct, 2) if trade.profit_loss_pct else None,
                "status": trade.status,
                "ai_confidence": trade.ai_confidence,
                "ai_recommendation": trade.ai_recommendation,
                "trade_date": trade.trade_date.isoformat() if trade.trade_date else None,
                "closed_date": trade.closed_date.isoformat() if trade.closed_date else None
            }
            for trade in trades
        ]

paper_trader = PaperTrader()
