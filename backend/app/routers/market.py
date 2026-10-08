import asyncio
from fastapi import APIRouter, Query
from app.services.market_service import FinnhubClient, TechnicalAnalysisService
from app.config import settings

router = APIRouter(prefix="/api/market", tags=["market"])


def _client() -> FinnhubClient:
    return FinnhubClient(settings.FINNHUB_API_KEY)


@router.get("/quote/{ticker}")
async def get_quote(ticker: str):
    return await _client().get_quote(ticker.upper())


@router.get("/candles/{ticker}")
async def get_candles(ticker: str, days: int = 60):
    return await _client().get_candles(ticker.upper(), days=days)


@router.get("/news/{ticker}")
async def get_news(ticker: str, days: int = 2):
    return await _client().get_news(ticker.upper(), days=days)


@router.get("/indicators/{ticker}")
async def get_indicators(ticker: str):
    client = _client()
    ta = TechnicalAnalysisService()
    candles = await client.get_candles(ticker.upper(), days=90)
    return ta.compute_indicators(candles)


@router.get("/search")
async def search_tickers(q: str = Query(..., min_length=1)):
    return await _client().search_tickers(q)


@router.get("/batch-quotes")
async def batch_quotes(tickers: str = Query(...)):
    client = _client()
    ticker_list = [t.strip().upper() for t in tickers.split(",")[:10]]
    results = await asyncio.gather(*[client.get_quote(t) for t in ticker_list])
    return {ticker_list[i]: results[i] for i in range(len(ticker_list))}
