from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Market ───────────────────────────────────────────────────────────────────

class QuoteData(BaseModel):
    current_price: float = 0
    open: float = 0
    high: float = 0
    low: float = 0
    prev_close: float = 0
    change: float = 0
    change_pct: float = 0
    timestamp: int = 0


class CandleData(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: int


class NewsItem(BaseModel):
    headline: str
    summary: str
    source: str
    datetime: int
    url: str
    sentiment: str = "neutral"


class MACDData(BaseModel):
    macd: Optional[float] = None
    signal: Optional[float] = None
    histogram: Optional[float] = None
    trend: str = "neutral"


class BollingerData(BaseModel):
    upper: float
    middle: float
    lower: float
    width: float
    position: str


class TechnicalIndicators(BaseModel):
    rsi: Optional[float] = None
    macd: Optional[MACDData] = None
    macd_trend: str = "neutral"
    sma20: Optional[float] = None
    sma50: Optional[float] = None
    bollinger: Optional[BollingerData] = None
    volume_trend: str = "unknown"
    momentum_1d: Optional[float] = None
    momentum_5d: Optional[float] = None
    momentum_20d: Optional[float] = None


# ── AI Analysis ───────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    ticker: str


class AIVoteResult(BaseModel):
    model_name: str
    direction: str  # up / down
    confidence: float
    risk_level: str  # low / medium / high
    reasoning: str
    round: int = 1
    is_mock: bool = False


class AnalysisResult(BaseModel):
    ticker: str
    round1_votes: List[AIVoteResult] = []
    round2_votes: List[AIVoteResult] = []
    final_direction: str
    final_confidence: float
    final_risk: str
    consensus_score: float
    aggregated_reasoning: str
    price_at_analysis: float = 0


# ── Trades & Portfolio ────────────────────────────────────────────────────────

class TradeRequest(BaseModel):
    ticker: str
    action: str  # buy / sell
    shares: float
    price: float


class TradeResponse(BaseModel):
    id: int
    ticker: str
    action: str
    shares: float
    price: float
    total: float
    pnl: Optional[float] = None
    timestamp: datetime


class HoldingData(BaseModel):
    ticker: str
    shares: float
    avg_price: float
    current_price: float
    value: float
    pnl: float
    pnl_percent: float


class PortfolioSnapshot(BaseModel):
    cash: float
    holdings: List[HoldingData] = []
    total_value: float
    pnl: float
    pnl_percent: float
    initial_balance: float = 100000.0


class FundsRequest(BaseModel):
    amount: float = Field(..., gt=0)
    action: str  # add / withdraw


# ── Position Sizing ───────────────────────────────────────────────────────────

class PositionSizeRecommendation(BaseModel):
    recommended_shares: float
    recommended_value: float
    fraction_used: float
    reasoning: str


# ── Training ─────────────────────────────────────────────────────────────────

class TrainingStatus(BaseModel):
    model_exists: bool
    last_trained: Optional[str] = None
    accuracy: Optional[float] = None
    samples_used: Optional[int] = None
    feature_importances: Optional[Dict[str, float]] = None
