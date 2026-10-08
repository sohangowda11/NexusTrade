from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import get_db
from app.models.orm_models import AnalysisSession, AIVote
from app.models.schemas import AnalysisRequest
from app.services.ai_service import run_analysis_session
from app.services.market_service import FinnhubClient, TechnicalAnalysisService
from app.config import settings

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/run")
async def run_analysis(req: AnalysisRequest, db: Session = Depends(get_db)):
    ticker = req.ticker.upper()
    client = FinnhubClient(settings.FINNHUB_API_KEY)
    ta = TechnicalAnalysisService()

    # Fetch market context in parallel
    import asyncio
    quote, candles, news = await asyncio.gather(
        client.get_quote(ticker),
        client.get_candles(ticker, days=60),
        client.get_news(ticker, days=2),
    )
    indicators = ta.compute_indicators(candles)

    price_summary = (
        f"Current: ${quote.get('current_price', 'N/A')}, "
        f"Change: {quote.get('change_pct', 0):.2f}%, "
        f"High: ${quote.get('high', 'N/A')}, Low: ${quote.get('low', 'N/A')}"
    )
    news_summary = "\n".join([f"- {n['headline']}" for n in news[:5]]) or "No recent news available."
    indicators_dict = {
        "rsi": indicators.get("rsi"),
        "macd_trend": indicators.get("macd_trend", "neutral"),
        "sma20": indicators.get("sma20"),
        "sma50": indicators.get("sma50"),
        "volume_trend": indicators.get("volume_trend"),
        "momentum_5d": indicators.get("momentum_5d"),
    }

    result = await run_analysis_session(ticker, price_summary, news_summary, indicators_dict)
    result["price_at_analysis"] = quote.get("current_price", 0)

    # Persist to DB
    session = AnalysisSession(
        ticker=ticker,
        final_direction=result["final_direction"],
        final_confidence=result["final_confidence"],
        final_risk=result["final_risk"],
        consensus_score=result["consensus_score"],
        aggregated_reasoning=result["aggregated_reasoning"],
        price_at_analysis=result["price_at_analysis"],
        timestamp=datetime.utcnow(),
    )
    db.add(session)
    db.flush()

    for vote_data in result["round1_votes"] + result["round2_votes"]:
        vote = AIVote(
            session_id=session.id,
            model_name=vote_data["model_name"],
            direction=vote_data["direction"],
            confidence=vote_data["confidence"],
            risk_level=vote_data["risk_level"],
            reasoning=vote_data.get("reasoning", ""),
            discussion_round=vote_data.get("round", 1),
        )
        db.add(vote)
    db.commit()

    return result


@router.get("/history/{ticker}")
def get_history(ticker: str, limit: int = 20, db: Session = Depends(get_db)):
    sessions = (
        db.query(AnalysisSession)
        .filter(AnalysisSession.ticker == ticker.upper())
        .order_by(AnalysisSession.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": s.id, "ticker": s.ticker,
            "final_direction": s.final_direction,
            "final_confidence": s.final_confidence,
            "final_risk": s.final_risk,
            "consensus_score": s.consensus_score,
            "timestamp": s.timestamp.isoformat(),
            "price_at_analysis": s.price_at_analysis,
            "price_24h_later": s.price_24h_later,
        }
        for s in sessions
    ]


@router.get("/model-performance")
def get_model_performance(db: Session = Depends(get_db)):
    from app.models.orm_models import ModelPerformance
    rows = db.query(ModelPerformance).all()
    return [
        {
            "model_name": r.model_name, "ticker": r.ticker,
            "correct": r.correct_predictions, "total": r.total_predictions,
            "accuracy": r.accuracy,
        }
        for r in rows
    ]
