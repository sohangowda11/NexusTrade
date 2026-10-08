import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx
import numpy as np

logger = logging.getLogger(__name__)

# Simple in-memory TTL cache
_cache: dict = {}


def _cache_get(key: str) -> Optional[dict]:
    if key in _cache:
        val, expires = _cache[key]
        if datetime.utcnow() < expires:
            return val
        del _cache[key]
    return None


def _cache_set(key: str, val, ttl_seconds: int):
    _cache[key] = (val, datetime.utcnow() + timedelta(seconds=ttl_seconds))


def _mock_candles(ticker: str, days: int = 60) -> list:
    """Deterministic random-walk OHLCV seeded by ticker."""
    seed = sum(ord(c) for c in ticker)
    rng = random.Random(seed)
    price = rng.uniform(80, 400)
    candles = []
    base_date = datetime.utcnow() - timedelta(days=days)
    for i in range(days):
        open_p = price * (1 + rng.uniform(-0.005, 0.005))
        close_p = open_p * (1 + rng.gauss(0.0003, 0.015))
        high_p = max(open_p, close_p) * (1 + abs(rng.gauss(0, 0.008)))
        low_p = min(open_p, close_p) * (1 - abs(rng.gauss(0, 0.008)))
        vol = int(rng.uniform(5_000_000, 80_000_000))
        candles.append({
            "time": int((base_date + timedelta(days=i)).timestamp()),
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": vol,
        })
        price = close_p
    return candles


class FinnhubClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.mock_mode = not bool(api_key)

    async def _get(self, path: str, params: dict = None) -> dict:
        if self.mock_mode:
            return {}
        params = params or {}
        params["token"] = self.api_key
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.base_url}{path}", params=params)
                if resp.status_code == 429:
                    logger.warning("Finnhub rate limited, switching to mock mode")
                    self.mock_mode = True
                    return {}
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.warning(f"Finnhub request failed: {e}")
            return {}

    async def get_quote(self, ticker: str) -> dict:
        key = f"quote:{ticker}"
        cached = _cache_get(key)
        if cached:
            return cached
        if self.mock_mode:
            seed = sum(ord(c) for c in ticker)
            # Vary slightly by minute so it feels live
            rng = random.Random(seed + int(datetime.utcnow().timestamp() // 60))
            price = rng.uniform(80, 400)
            change = rng.gauss(0, price * 0.02)
            result = {
                "current_price": round(price, 2),
                "open": round(price - change * 0.3, 2),
                "high": round(price + abs(change) * 0.5, 2),
                "low": round(price - abs(change) * 0.5, 2),
                "prev_close": round(price - change, 2),
                "change": round(change, 2),
                "change_pct": round(change / price * 100, 3),
                "timestamp": int(datetime.utcnow().timestamp()),
            }
        else:
            data = await self._get("/quote", {"symbol": ticker})
            if not data:
                self.mock_mode = True
                return await self.get_quote(ticker)
            result = {
                "current_price": data.get("c", 0),
                "open": data.get("o", 0),
                "high": data.get("h", 0),
                "low": data.get("l", 0),
                "prev_close": data.get("pc", 0),
                "change": data.get("d", 0),
                "change_pct": data.get("dp", 0),
                "timestamp": data.get("t", 0),
            }
        _cache_set(key, result, 15)
        return result

    async def get_candles(self, ticker: str, resolution: str = "D", days: int = 60) -> list:
        key = f"candles:{ticker}:{days}"
        cached = _cache_get(key)
        if cached:
            return cached
        if self.mock_mode:
            result = _mock_candles(ticker, days)
        else:
            to_ts = int(datetime.utcnow().timestamp())
            from_ts = to_ts - days * 86400
            data = await self._get("/stock/candle", {
                "symbol": ticker, "resolution": resolution,
                "from": from_ts, "to": to_ts,
            })
            if not data or data.get("s") != "ok":
                result = _mock_candles(ticker, days)
            else:
                result = [
                    {"time": t, "open": o, "high": h, "low": l, "close": c, "volume": v}
                    for t, o, h, l, c, v in zip(
                        data["t"], data["o"], data["h"], data["l"], data["c"], data["v"]
                    )
                ]
        _cache_set(key, result, 60)
        return result

    async def get_news(self, ticker: str, days: int = 2) -> list:
        key = f"news:{ticker}:{days}"
        cached = _cache_get(key)
        if cached:
            return cached
        if self.mock_mode:
            result = [
                {"headline": f"{ticker} reports strong quarterly results beating analyst expectations",
                 "summary": "Revenue exceeded consensus estimates by 8%, driven by core business growth.",
                 "source": "Reuters", "datetime": int((datetime.utcnow() - timedelta(hours=6)).timestamp()),
                 "url": "#", "sentiment": "positive"},
                {"headline": f"Analysts raise {ticker} price target following earnings beat",
                 "summary": "Multiple Wall Street firms upgraded their outlook after strong guidance.",
                 "source": "Bloomberg", "datetime": int((datetime.utcnow() - timedelta(hours=18)).timestamp()),
                 "url": "#", "sentiment": "positive"},
                {"headline": f"{ticker} navigates macro uncertainty with resilient margins",
                 "summary": "Company maintained full-year guidance despite broader market headwinds.",
                 "source": "WSJ", "datetime": int((datetime.utcnow() - timedelta(hours=36)).timestamp()),
                 "url": "#", "sentiment": "neutral"},
            ]
        else:
            to_dt = datetime.utcnow().strftime("%Y-%m-%d")
            from_dt = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            data = await self._get("/company-news", {"symbol": ticker, "from": from_dt, "to": to_dt})
            result = [
                {"headline": n.get("headline", ""),
                 "summary": n.get("summary", ""),
                 "source": n.get("source", ""),
                 "datetime": n.get("datetime", 0),
                 "url": n.get("url", "#"),
                 "sentiment": "neutral"}
                for n in (data or [])[:10]
            ] if data else []
        _cache_set(key, result, 300)
        return result

    async def get_company_profile(self, ticker: str) -> dict:
        if self.mock_mode:
            return {"name": ticker, "exchange": "NASDAQ", "industry": "Technology",
                    "market_cap": 1_000_000_000, "logo_url": ""}
        data = await self._get("/stock/profile2", {"symbol": ticker})
        return {
            "name": data.get("name", ticker),
            "exchange": data.get("exchange", ""),
            "industry": data.get("finnhubIndustry", ""),
            "market_cap": data.get("marketCapitalization", 0),
            "logo_url": data.get("logo", ""),
        }

    async def search_tickers(self, query: str) -> list:
        if self.mock_mode:
            return [{"ticker": query.upper(), "name": f"{query.upper()} Inc."}]
        data = await self._get("/search", {"q": query})
        return [
            {"ticker": r.get("symbol", ""), "name": r.get("description", "")}
            for r in (data.get("result", []))[:10]
        ]


class TechnicalAnalysisService:
    def compute_indicators(self, candles: list) -> dict:
        if not candles or len(candles) < 5:
            return {"rsi": None, "macd": None, "macd_trend": "neutral",
                    "sma20": None, "sma50": None, "bollinger": None, "volume_trend": "unknown"}

        closes = np.array([c["close"] for c in candles], dtype=float)
        volumes = np.array([c["volume"] for c in candles], dtype=float)
        result: dict = {}

        # RSI
        if len(closes) >= 15:
            deltas = np.diff(closes)
            gains = np.where(deltas > 0, deltas, 0.0)
            losses = np.where(deltas < 0, -deltas, 0.0)
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            rs = avg_gain / avg_loss if avg_loss > 0 else 100.0
            result["rsi"] = round(100 - (100 / (1 + rs)), 2)
        else:
            result["rsi"] = None

        # SMA
        result["sma20"] = round(float(np.mean(closes[-20:])), 2) if len(closes) >= 20 else None
        result["sma50"] = round(float(np.mean(closes[-50:])), 2) if len(closes) >= 50 else None

        # MACD
        if len(closes) >= 26:
            def ema(data: np.ndarray, period: int) -> np.ndarray:
                k = 2.0 / (period + 1)
                out = [float(data[0])]
                for v in data[1:]:
                    out.append(float(v) * k + out[-1] * (1 - k))
                return np.array(out)

            ema12 = ema(closes, 12)
            ema26 = ema(closes, 26)
            macd_line = ema12[-len(ema26):] - ema26
            signal_line = ema(macd_line, 9) if len(macd_line) >= 9 else macd_line
            histogram = float(macd_line[-1] - signal_line[-1])
            trend = "bullish" if histogram > 0 else ("bearish" if histogram < 0 else "neutral")
            result["macd"] = {
                "macd": round(float(macd_line[-1]), 4),
                "signal": round(float(signal_line[-1]), 4),
                "histogram": round(histogram, 4),
                "trend": trend,
            }
            result["macd_trend"] = trend
        else:
            result["macd"] = None
            result["macd_trend"] = "neutral"

        # Bollinger Bands
        if len(closes) >= 20:
            sma = float(np.mean(closes[-20:]))
            std = float(np.std(closes[-20:]))
            upper = sma + 2 * std
            lower = sma - 2 * std
            current = float(closes[-1])
            position = "above" if current > upper else ("below" if current < lower else "within")
            result["bollinger"] = {
                "upper": round(upper, 2),
                "middle": round(sma, 2),
                "lower": round(lower, 2),
                "width": round((upper - lower) / sma, 4) if sma else 0,
                "position": position,
            }
        else:
            result["bollinger"] = None

        # Volume trend
        if len(volumes) >= 20:
            ratio = float(np.mean(volumes[-5:])) / float(np.mean(volumes[-20:]))
            result["volume_trend"] = "above_average" if ratio > 1.2 else ("below_average" if ratio < 0.8 else "normal")
        else:
            result["volume_trend"] = "unknown"

        # Momentum
        result["momentum_1d"] = round(float((closes[-1] - closes[-2]) / closes[-2] * 100), 3) if len(closes) >= 2 else None
        result["momentum_5d"] = round(float((closes[-1] - closes[-6]) / closes[-6] * 100), 3) if len(closes) >= 6 else None
        result["momentum_20d"] = round(float((closes[-1] - closes[-21]) / closes[-21] * 100), 3) if len(closes) >= 21 else None

        return result
