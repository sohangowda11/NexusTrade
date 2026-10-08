from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import PortfolioSnapshot, FundsRequest
from app.services import portfolio_service

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioSnapshot)
def get_portfolio(db: Session = Depends(get_db)):
    return portfolio_service.get_snapshot(db)


@router.post("/funds")
def adjust_funds(req: FundsRequest, db: Session = Depends(get_db)):
    from app.models.orm_models import Portfolio
    portfolio = db.query(Portfolio).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if req.action == "add":
        portfolio.cash_balance += req.amount
    elif req.action == "withdraw":
        if portfolio.cash_balance < req.amount:
            raise HTTPException(status_code=400, detail="Insufficient cash balance")
        portfolio.cash_balance -= req.amount
    else:
        raise HTTPException(status_code=400, detail="action must be 'add' or 'withdraw'")
    db.commit()
    return {"cash_balance": portfolio.cash_balance, "action": req.action, "amount": req.amount}


@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    from app.models.orm_models import Trade
    trades = db.query(Trade).order_by(Trade.timestamp.asc()).all()
    running_value = 100000.0
    history = []
    for t in trades:
        if t.action == "buy":
            running_value -= t.total
        else:
            running_value += t.total
        history.append({
            "timestamp": t.timestamp.isoformat(),
            "cash_after": running_value,
        })
    return history
