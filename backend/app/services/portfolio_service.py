from sqlalchemy.orm import Session
from app.models.orm_models import Portfolio, Holding, Trade
from app.models.schemas import PortfolioSnapshot, HoldingData, PositionSizeRecommendation
from app.config import settings
from datetime import datetime
from typing import Optional


def _get_portfolio(db: Session) -> Portfolio:
    portfolio = db.query(Portfolio).first()
    if not portfolio:
        portfolio = Portfolio(cash_balance=settings.INITIAL_BALANCE)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    return portfolio


def execute_buy(db: Session, ticker: str, shares: float, price: float) -> Trade:
    portfolio = _get_portfolio(db)
    total = shares * price
    if portfolio.cash_balance < total:
        raise ValueError(f"Insufficient funds: need ${total:.2f}, have ${portfolio.cash_balance:.2f}")

    # Update cash
    portfolio.cash_balance -= total
    portfolio.updated_at = datetime.utcnow()

    # Upsert holding with weighted avg cost
    holding = db.query(Holding).filter(
        Holding.portfolio_id == portfolio.id,
        Holding.ticker == ticker.upper()
    ).first()

    if holding:
        new_shares = holding.shares + shares
        holding.avg_price = (holding.avg_price * holding.shares + price * shares) / new_shares
        holding.shares = new_shares
    else:
        holding = Holding(
            portfolio_id=portfolio.id,
            ticker=ticker.upper(),
            shares=shares,
            avg_price=price,
        )
        db.add(holding)

    trade = Trade(
        portfolio_id=portfolio.id,
        ticker=ticker.upper(),
        action="buy",
        shares=shares,
        price=price,
        total=total,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def execute_sell(db: Session, ticker: str, shares: float, price: float) -> Trade:
    portfolio = _get_portfolio(db)
    holding = db.query(Holding).filter(
        Holding.portfolio_id == portfolio.id,
        Holding.ticker == ticker.upper()
    ).first()

    if not holding or holding.shares < shares:
        have = holding.shares if holding else 0
        raise ValueError(f"Not enough shares: need {shares}, have {have}")

    total = shares * price
    pnl = (price - holding.avg_price) * shares

    # Update holding
    holding.shares -= shares
    if holding.shares <= 0.0001:
        db.delete(holding)

    portfolio.cash_balance += total
    portfolio.updated_at = datetime.utcnow()

    trade = Trade(
        portfolio_id=portfolio.id,
        ticker=ticker.upper(),
        action="sell",
        shares=shares,
        price=price,
        total=total,
        pnl=pnl,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def get_snapshot(db: Session, current_prices: Optional[dict] = None) -> PortfolioSnapshot:
    portfolio = _get_portfolio(db)
    holdings_orm = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()

    holdings_data = []
    holdings_value = 0.0

    for h in holdings_orm:
        curr_price = (current_prices or {}).get(h.ticker, h.avg_price)
        value = h.shares * curr_price
        pnl = (curr_price - h.avg_price) * h.shares
        pnl_pct = ((curr_price - h.avg_price) / h.avg_price * 100) if h.avg_price else 0
        holdings_value += value
        holdings_data.append(HoldingData(
            ticker=h.ticker,
            shares=h.shares,
            avg_price=h.avg_price,
            current_price=curr_price,
            value=value,
            pnl=pnl,
            pnl_percent=pnl_pct,
        ))

    total_value = portfolio.cash_balance + holdings_value
    pnl_total = total_value - settings.INITIAL_BALANCE
    pnl_pct_total = (pnl_total / settings.INITIAL_BALANCE) * 100

    return PortfolioSnapshot(
        cash=portfolio.cash_balance,
        holdings=holdings_data,
        total_value=total_value,
        pnl=pnl_total,
        pnl_percent=pnl_pct_total,
    )


def recommend_position_size(
    confidence: float,
    risk_level: str,
    current_price: float,
    available_cash: float,
) -> PositionSizeRecommendation:
    """Kelly-criterion-inspired position sizing with risk caps."""
    # Kelly fraction: f = (2 * p - 1) where p = confidence/100
    p = confidence / 100.0
    kelly_fraction = max(0.0, 2 * p - 1)

    # Risk cap by tier
    risk_caps = {"low": 0.15, "medium": 0.10, "high": 0.05}
    cap = risk_caps.get(risk_level, 0.10)

    fraction = min(kelly_fraction, cap)
    recommended_value = available_cash * fraction
    recommended_shares = int(recommended_value / current_price) if current_price > 0 else 0

    reasoning = (
        f"Kelly fraction: {kelly_fraction:.1%} from {confidence:.0f}% confidence. "
        f"Capped at {cap:.0%} for {risk_level} risk. "
        f"Recommended: {recommended_shares} shares (${recommended_value:.0f}) "
        f"= {fraction:.1%} of available cash."
    )

    return PositionSizeRecommendation(
        recommended_shares=recommended_shares,
        recommended_value=round(recommended_value, 2),
        fraction_used=round(fraction, 4),
        reasoning=reasoning,
    )
