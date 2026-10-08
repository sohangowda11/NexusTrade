from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.schemas import TradeRequest, TradeResponse, PositionSizeRecommendation
from app.services import portfolio_service

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.post("/execute", response_model=TradeResponse)
def execute_trade(req: TradeRequest, db: Session = Depends(get_db)):
    try:
        if req.action == "buy":
            trade = portfolio_service.execute_buy(db, req.ticker, req.shares, req.price)
        elif req.action == "sell":
            trade = portfolio_service.execute_sell(db, req.ticker, req.shares, req.price)
        else:
            raise HTTPException(status_code=400, detail="action must be 'buy' or 'sell'")
        return TradeResponse(
            id=trade.id,
            ticker=trade.ticker,
            action=trade.action,
            shares=trade.shares,
            price=trade.price,
            total=trade.total,
            pnl=trade.pnl,
            timestamp=trade.timestamp,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
def get_trade_history(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    from app.models.orm_models import Trade
    trades = (
        db.query(Trade)
        .order_by(Trade.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(Trade).count()
    return {
        "trades": [
            {
                "id": t.id, "ticker": t.ticker, "action": t.action,
                "shares": t.shares, "price": t.price, "total": t.total,
                "pnl": t.pnl, "timestamp": t.timestamp.isoformat(),
            }
            for t in trades
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/performance")
def get_performance(db: Session = Depends(get_db)):
    from app.models.orm_models import Trade
    sells = db.query(Trade).filter(Trade.action == "sell").all()
    if not sells:
        return {"total_pnl": 0, "wins": 0, "losses": 0, "win_rate": 0, "trade_count": 0}
    pnls = [t.pnl or 0 for t in sells]
    wins = sum(1 for p in pnls if p > 0)
    losses = sum(1 for p in pnls if p <= 0)
    return {
        "total_pnl": round(sum(pnls), 2),
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / len(pnls) * 100, 1) if pnls else 0,
        "best_trade": round(max(pnls), 2),
        "worst_trade": round(min(pnls), 2),
        "trade_count": len(sells),
    }


@router.post("/position-size", response_model=PositionSizeRecommendation)
def recommend_position(
    ticker: str, confidence: float, risk_level: str, current_price: float,
    db: Session = Depends(get_db),
):
    from app.models.orm_models import Portfolio
    portfolio = db.query(Portfolio).first()
    cash = portfolio.cash_balance if portfolio else 0
    return portfolio_service.recommend_position_size(confidence, risk_level, current_price, cash)
