from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime

OUTPUT = r"C:\Users\sohan\stock-trading-sim\NexusTrade_Documentation.pdf"

# ── Colours ──────────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0a0e1a")
CYAN    = colors.HexColor("#00d4ff")
AMBER   = colors.HexColor("#f59e0b")
GREEN   = colors.HexColor("#10b981")
RED     = colors.HexColor("#ef4444")
LIGHT   = colors.HexColor("#e2e8f0")
MUTED   = colors.HexColor("#64748b")
CARD_BG = colors.HexColor("#111827")
BORDER  = colors.HexColor("#1e293b")

# ── Styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

TITLE_STYLE = S("Title",
    fontSize=28, leading=34, textColor=CYAN,
    fontName="Helvetica-Bold", spaceAfter=4, alignment=TA_LEFT)

SUBTITLE_STYLE = S("Subtitle",
    fontSize=13, leading=18, textColor=MUTED,
    fontName="Helvetica", spaceAfter=20, alignment=TA_LEFT)

H1 = S("H1",
    fontSize=18, leading=24, textColor=CYAN,
    fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=8)

H2 = S("H2",
    fontSize=14, leading=20, textColor=LIGHT,
    fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6)

H3 = S("H3",
    fontSize=11, leading=16, textColor=AMBER,
    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4)

BODY = S("Body",
    fontSize=10, leading=16, textColor=LIGHT,
    fontName="Helvetica", spaceAfter=8, alignment=TA_JUSTIFY)

BODY_MUTED = S("BodyMuted",
    fontSize=9, leading=14, textColor=MUTED,
    fontName="Helvetica", spaceAfter=6, alignment=TA_JUSTIFY)

CODE = S("Code",
    fontSize=8.5, leading=13, textColor=CYAN,
    fontName="Courier", spaceAfter=6,
    backColor=CARD_BG, borderPadding=(4, 6, 4, 6))

BULLET = S("Bullet",
    fontSize=10, leading=15, textColor=LIGHT,
    fontName="Helvetica", spaceAfter=4, leftIndent=16,
    bulletIndent=6)

def hr():
    return HRFlowable(width="100%", thickness=1, color=BORDER,
                      spaceAfter=10, spaceBefore=4)

def tbl(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0 if header else -1), CARD_BG),
        ("TEXTCOLOR",  (0, 0), (-1, 0), CYAN),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("LEADING",    (0, 0), (-1, -1), 14),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [NAVY, CARD_BG]),
        ("TEXTCOLOR",  (0, 1), (-1, -1), LIGHT),
        ("GRID",       (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]
    t.setStyle(TableStyle(style))
    return t

# ── Document ──────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="NexusTrade Documentation",
    author="NexusTrade AI System",
)

story = []

# ── Cover Page ────────────────────────────────────────────────────────────────
story.append(Spacer(1, 2*cm))
story.append(Paragraph("NEXUSTRADE", TITLE_STYLE))
story.append(Paragraph("AI-Powered Multi-Model Stock Trading Simulator", SUBTITLE_STYLE))
story.append(hr())
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("Project Documentation", H2))
story.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y')}", BODY_MUTED))
story.append(Spacer(1, 0.6*cm))

cover_info = [
    ["Stack",        "Next.js 16 · React 19 · FastAPI · Python · SQLite"],
    ["AI Models",    "Claude Sonnet · GPT-4o · Gemini 1.5 Pro · DeepSeek Chat"],
    ["Market Data",  "Finnhub (real-time) with deterministic mock fallback"],
    ["3D / Visuals", "Three.js particle field · lightweight-charts v5"],
    ["Paper Money",  "$100,000 virtual USD starting balance"],
    ["Repository",   "github.com/sohangowda11/TradeWithAi"],
]
story.append(tbl(cover_info, [3.5*cm, 12*cm], header=False))
story.append(PageBreak())

# ── 1. Introduction to Stock Trading ─────────────────────────────────────────
story.append(Paragraph("1. Introduction to Stock Trading", H1))
story.append(hr())

story.append(Paragraph("What Is a Stock?", H2))
story.append(Paragraph(
    "A stock (also called a share or equity) represents a fractional ownership stake in a company. "
    "When a company wants to raise capital, it can divide itself into millions of equal pieces and sell them to the public "
    "through a process called an IPO (Initial Public Offering). Each piece is one share. If you own 100 shares of a company "
    "that has 1,000,000 shares outstanding, you own 0.01% of that company.", BODY))

story.append(Paragraph("How Prices Move", H2))
story.append(Paragraph(
    "Stock prices are determined by supply and demand on an exchange. When more people want to buy a stock than sell it, "
    "the price rises. When more people want to sell, it falls. The underlying drivers of this supply/demand are: "
    "company earnings reports, macroeconomic data (interest rates, inflation, GDP), news and sentiment, "
    "analyst upgrades/downgrades, sector rotation, and broader market trends.", BODY))

story.append(Paragraph("Key Terms", H2))
terms = [
    ["Term", "Definition"],
    ["Market Cap", "Total value of all shares = Share Price × Shares Outstanding"],
    ["Volatility", "How much a stock's price swings. High volatility = larger moves, more risk"],
    ["Bid / Ask", "Bid = highest price a buyer will pay. Ask = lowest a seller will accept"],
    ["Volume", "Number of shares traded in a period. High volume confirms price moves"],
    ["P/E Ratio", "Price-to-Earnings: how much investors pay per $1 of earnings"],
    ["Bull / Bear", "Bull market = prices rising broadly. Bear market = prices falling broadly"],
    ["Liquidity", "How easily you can buy/sell without moving the price. Large caps = high liquidity"],
]
story.append(tbl(terms, [3.5*cm, 12*cm]))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("Types of Risk", H2))
story.append(Paragraph(
    "Market risk: the whole market falls (e.g., 2008 financial crisis). "
    "Sector risk: a specific industry is hurt (e.g., oil stocks when crude prices crash). "
    "Company-specific risk: a single company has bad news (earnings miss, lawsuit, CEO resignation). "
    "Liquidity risk: you cannot sell when you want to. "
    "The key insight behind diversification is that company-specific and sector risks can be reduced by holding many different stocks.", BODY))

story.append(Paragraph("Why Paper Trading Matters", H2))
story.append(Paragraph(
    "Paper trading means simulating trades with fake money but using real market prices. "
    "It lets you develop intuition, test strategies, and learn from mistakes without losing real capital. "
    "Professional traders often paper-trade a new strategy for months before committing real money. "
    "NexusTrade is a paper trading simulator — all money is virtual, all trades are simulated, "
    "and no real brokerage integration exists.", BODY))

story.append(PageBreak())

# ── 2. The AI Voting & Discussion System ──────────────────────────────────────
story.append(Paragraph("2. The AI Voting & Discussion System", H1))
story.append(hr())

story.append(Paragraph("Overview", H2))
story.append(Paragraph(
    "The core innovation of NexusTrade is treating stock analysis as a multi-agent deliberation problem. "
    "Rather than relying on a single AI model's opinion, the system queries four different large language models "
    "in parallel, collects their independent analyses, then runs a second 'discussion' round where each model "
    "sees what the others said and can revise its view. The final signal is an aggregate of these revised votes.", BODY))

story.append(Paragraph("What Each Model Receives (The Prompt)", H2))
story.append(Paragraph("Every model gets an identical structured prompt containing:", BODY))
for item in [
    "Ticker symbol being analyzed",
    "Current price, day change %, high, and low",
    "RSI (14-period), MACD trend, SMA 20, SMA 50, volume trend, 5-day momentum",
    "Up to 5 recent news headlines from Finnhub (last 48 hours)",
    "Explicit JSON output format requirement",
]:
    story.append(Paragraph(f"• {item}", BULLET))

story.append(Paragraph("What Each Model Returns", H2))
story.append(Paragraph("Models are instructed to respond with strict JSON only:", BODY))
story.append(Paragraph(
    '{"direction": "up" or "down",  "confidence": 0-100,  "risk_level": "low"/"medium"/"high",  '
    '"reasoning": "2-3 sentence explanation"}', CODE))

story.append(Paragraph("Round 1: Independent Analysis", H2))
story.append(Paragraph(
    "All four models are called simultaneously using Python's asyncio.gather(), meaning they run in true parallel "
    "(limited only by network latency). Each model analyzes the same data independently, with no knowledge of "
    "what the others are saying. This independence is critical — it avoids 'groupthink' where one influential "
    "opinion anchors all the others.", BODY))

story.append(Paragraph("Round 2: The Discussion", H2))
story.append(Paragraph(
    "After Round 1, each model is sent a new prompt that includes its own Round 1 vote plus a summary of the "
    "other three models' directions, confidence levels, and reasoning. The model is asked: 'Considering their "
    "perspectives, would you revise your prediction?' This simulates how a real investment committee might work — "
    "analysts present their views, hear challenges, and either hold their ground or update based on new arguments. "
    "Round 2 votes are what the final signal is based on.", BODY))

story.append(Paragraph("Why Only 2 Rounds?", H2))
story.append(Paragraph(
    "Each round costs real money in API tokens. With 4 models and 2 rounds, that is 8 API calls per analysis. "
    "Research on multi-agent deliberation shows that most information exchange happens in the first discussion round — "
    "additional rounds produce diminishing returns while costs compound. The system is designed to cap at 2 rounds "
    "to balance insight quality against cost.", BODY))

story.append(Paragraph("Aggregation Algorithm", H2))
agg = [
    ["Signal", "How Computed"],
    ["Final Direction", "Majority vote among Round 2 directions. Tie = 'uncertain'"],
    ["Final Confidence", "Weighted average of confidence scores from the majority side"],
    ["Final Risk",       "Worst-case escalation: if any model says 'high', result is 'high'"],
    ["Consensus Score",  "% of models that voted with the majority. 100% = full agreement"],
]
story.append(tbl(agg, [4*cm, 11.5*cm]))

story.append(Paragraph("Mock Mode", H2))
story.append(Paragraph(
    "If an API key is missing or a model call fails, the system falls back to a deterministic mock response. "
    "The mock is seeded by the model name + ticker symbol, so it produces the same 'fake vote' every time for "
    "that combination within a session. This means the UI is fully functional with zero API keys — "
    "great for development and demonstration.", BODY))

story.append(PageBreak())

# ── 3. Paper Trading Engine ───────────────────────────────────────────────────
story.append(Paragraph("3. Paper Trading Engine", H1))
story.append(hr())

story.append(Paragraph("Virtual Wallet", H2))
story.append(Paragraph(
    "Every user starts with $100,000 in virtual USD. This balance is stored in a SQLite database (the Portfolio table) "
    "and is persistent across sessions. You can manually add or withdraw funds at any time through the portfolio panel "
    "in the UI — there is no upper limit, because it is fake money.", BODY))

story.append(Paragraph("Executing a Buy", H2))
story.append(Paragraph(
    "When you buy shares: (1) the system checks you have enough cash, (2) deducts the total cost "
    "(shares × price) from your cash balance, (3) creates or updates a Holding record for that ticker. "
    "If you already own shares, the new purchase is averaged into your existing position using a "
    "weighted average cost basis formula:", BODY))
story.append(Paragraph(
    "new_avg_price = (old_avg × old_shares + new_price × new_shares) / (old_shares + new_shares)", CODE))

story.append(Paragraph("Executing a Sell", H2))
story.append(Paragraph(
    "When you sell shares: (1) the system checks you actually hold enough shares to sell, (2) calculates "
    "realized P&L using the FIFO average cost basis: P&L = (current_price - avg_cost) × shares_sold, "
    "(3) adds the proceeds back to your cash, (4) reduces the holding. If shares reach zero, "
    "the holding record is deleted.", BODY))

story.append(Paragraph("Position Sizing: The Kelly Criterion", H2))
story.append(Paragraph(
    "The AI system can recommend how many shares to buy, not just whether to buy. "
    "It uses a simplified Kelly Criterion — a mathematical formula from gambling theory "
    "that tells you the optimal fraction of your bankroll to bet given your edge:", BODY))
story.append(Paragraph("Kelly fraction  f = max(0,  2p − 1)", CODE))
story.append(Paragraph(
    "Where p = confidence / 100. So 70% confidence → f = 0.40 (bet 40% of available cash). "
    "This raw fraction is then capped by a risk tier multiplier to prevent catastrophic overexposure:", BODY))
risk_tbl = [
    ["Risk Level", "Cap",  "Example: 70% confidence, $50,000 cash"],
    ["Low",        "15%",  "min(40%, 15%) × $50,000 = $7,500 position"],
    ["Medium",     "10%",  "min(40%, 10%) × $50,000 = $5,000 position"],
    ["High",        "5%",  "min(40%, 5%)  × $50,000 = $2,500 position"],
]
story.append(tbl(risk_tbl, [3*cm, 2.5*cm, 10*cm]))

story.append(Paragraph("P&L Tracking", H2))
story.append(Paragraph(
    "Unrealized P&L: (current_price - avg_cost) × shares held. Updates every time the watchlist "
    "quote refreshes (every 30 seconds). Realized P&L: calculated at sell time and stored permanently "
    "in the Trade record. All-time P&L: total_portfolio_value - $100,000 starting balance. "
    "Win rate: percentage of completed sell trades where realized P&L was positive.", BODY))

story.append(PageBreak())

# ── 4. System Architecture ───────────────────────────────────────────────────
story.append(Paragraph("4. System Architecture", H1))
story.append(hr())

story.append(Paragraph("Frontend", H2))
arch_front = [
    ["Technology",      "Purpose"],
    ["Next.js 16",      "React framework, App Router, Server + Client components"],
    ["React 19",        "UI rendering, concurrent features"],
    ["TypeScript",      "Type safety across all components and API calls"],
    ["Tailwind CSS v4", "Utility classes with @theme CSS-first configuration"],
    ["Zustand",         "Persistent client state: wallet, holdings, trades, watchlist"],
    ["React Query",     "Server state: API data fetching, caching, background refresh"],
    ["Three.js",        "3D particle field in the hero section"],
    ["lightweight-charts v5", "Professional candlestick charts (TradingView library)"],
    ["framer-motion",   "Animated card entrances, loading states"],
    ["Lucide React",    "Icon library"],
    ["axios",           "HTTP client for backend API calls"],
]
story.append(tbl(arch_front, [4.5*cm, 11*cm]))

story.append(Paragraph("Backend", H2))
arch_back = [
    ["Technology",    "Purpose"],
    ["FastAPI",       "Async Python web framework, automatic OpenAPI docs"],
    ["SQLAlchemy 2",  "ORM for database models and queries"],
    ["SQLite",        "Local database (upgradeable to PostgreSQL for production)"],
    ["Pydantic v2",   "Request/response validation and serialization"],
    ["httpx",         "Async HTTP client for Finnhub API calls"],
    ["APScheduler",   "Weekly model retraining cron job"],
    ["scikit-learn",  "GradientBoostingClassifier for the meta-model"],
    ["numpy",         "Technical indicator computations"],
]
story.append(tbl(arch_back, [4.5*cm, 11*cm]))

story.append(Paragraph("Database Schema", H2))
db = [
    ["Table",              "Key Columns"],
    ["Portfolio",          "id, cash_balance, created_at, updated_at"],
    ["Holding",            "id, portfolio_id, ticker, shares, avg_price"],
    ["Trade",              "id, portfolio_id, ticker, action, shares, price, total, pnl, timestamp"],
    ["AnalysisSession",    "id, ticker, final_direction, final_confidence, final_risk, consensus_score, price_at_analysis, price_24h_later, timestamp"],
    ["AIVote",             "id, session_id, model_name, direction, confidence, risk_level, reasoning, discussion_round, was_correct"],
    ["ModelPerformance",   "id, model_name, ticker, correct_predictions, total_predictions, accuracy"],
]
story.append(tbl(db, [4*cm, 11.5*cm]))

story.append(Paragraph("Data Flow: Analyze a Stock", H2))
flow = [
    ["Step", "Action"],
    ["1", "User clicks ANALYZE AAPL in the AI Voting Panel"],
    ["2", "Frontend calls POST /api/analysis/run {ticker: 'AAPL'}"],
    ["3", "Backend fetches quote, 60-day candles, and news from Finnhub in parallel"],
    ["4", "TechnicalAnalysisService computes RSI, MACD, Bollinger Bands, SMA, volume trend"],
    ["5", "ai_service builds the analysis prompt and calls all 4 models in parallel (Round 1)"],
    ["6", "Each model's vote is collected; models that fail fall back to mock responses"],
    ["7", "Discussion prompts built; all 4 models called again in parallel (Round 2)"],
    ["8", "Votes aggregated: majority direction, weighted confidence, risk escalation"],
    ["9", "AnalysisSession + 8 AIVote rows written to SQLite"],
    ["10","Result JSON returned to frontend; Zustand store updated; UI animates in"],
]
story.append(tbl(flow, [1.5*cm, 14*cm]))

story.append(PageBreak())

# ── 5. Technical Indicators ──────────────────────────────────────────────────
story.append(Paragraph("5. Technical Indicators", H1))
story.append(hr())

story.append(Paragraph("RSI — Relative Strength Index", H2))
story.append(Paragraph(
    "RSI measures how overbought or oversold a stock is on a 0-100 scale, using the last 14 trading days. "
    "Formula: RSI = 100 − 100/(1 + RS), where RS = average gain over 14 days / average loss over 14 days. "
    "RSI > 70: stock may be overbought (price could pull back). RSI < 30: stock may be oversold (possible bounce). "
    "RSI around 50: neutral momentum.", BODY))

story.append(Paragraph("MACD — Moving Average Convergence Divergence", H2))
story.append(Paragraph(
    "MACD uses three exponential moving averages: the 12-day EMA, 26-day EMA, and a 9-day signal line. "
    "MACD line = EMA(12) − EMA(26). Signal line = EMA(9) of the MACD line. "
    "Histogram = MACD − Signal. When the histogram is positive (MACD above signal), trend is bullish. "
    "When negative, trend is bearish. The MACD 'crossover' (when MACD crosses above signal) is a classic "
    "buy signal; crossing below is a sell signal.", BODY))

story.append(Paragraph("Bollinger Bands", H2))
story.append(Paragraph(
    "Bollinger Bands place an upper and lower envelope around the 20-day SMA, each 2 standard deviations away. "
    "Upper band = SMA(20) + 2σ. Lower band = SMA(20) − 2σ. "
    "When price touches or exceeds the upper band, the stock may be overbought. "
    "When it touches the lower band, it may be oversold. 'Band squeeze' (bands narrowing) signals that a "
    "large move is coming, though not which direction.", BODY))

story.append(Paragraph("SMA — Simple Moving Average", H2))
story.append(Paragraph(
    "SMA(20) and SMA(50) are the average closing prices over the last 20 and 50 days. "
    "Golden Cross: SMA(50) crosses above SMA(200) — historically bullish. "
    "Death Cross: SMA(50) crosses below SMA(200) — historically bearish. "
    "Price trading above SMA(20) is generally considered short-term bullish.", BODY))

story.append(Paragraph("Volume Trend", H2))
story.append(Paragraph(
    "Volume trend compares the 5-day average volume against the 20-day average. "
    "Above average (ratio > 1.2): unusual interest, move is more likely to sustain. "
    "Below average (ratio < 0.8): low conviction, price move may reverse. "
    "Volume always confirms or denies a price move — a price rise on low volume is weak.", BODY))

story.append(PageBreak())

# ── 6. Custom Model Training ─────────────────────────────────────────────────
story.append(Paragraph("6. Custom Model Training", H1))
story.append(hr())

story.append(Paragraph("What 'Training Your Own Model' Actually Means", H2))
story.append(Paragraph(
    "This is NOT training a new large language model from scratch — that would require millions of dollars "
    "and months of GPU time. Instead, NexusTrade trains a lightweight 'meta-model': a classifier that learns "
    "which AI models (or combinations of them) tend to be right. Think of it as a referee that has watched "
    "thousands of rounds and learned whose opinions to trust most.", BODY))

story.append(Paragraph("The Feature Matrix", H2))
story.append(Paragraph(
    "Each row in the training dataset represents one completed AnalysisSession where the 24-hour price outcome "
    "is already known. The features for each row are:", BODY))
features = [
    ["Feature", "Description"],
    ["claude_dir / gpt_dir / gemini_dir / deepseek_dir", "1=up, 0=down, -1=no vote"],
    ["claude_conf / gpt_conf / gemini_conf / deepseek_conf", "confidence / 100 (normalized 0-1)"],
    ["claude_risk / gpt_risk / gemini_risk / deepseek_risk", "0=low, 1=medium, 2=high"],
    ["consensus_score",  "Fraction of models that agreed with majority"],
    ["weekday",          "Day of week (0=Mon to 6=Sun), normalized"],
    ["hour",             "Hour of day (0-23), normalized — markets behave differently at open vs close"],
]
story.append(tbl(features, [6*cm, 9.5*cm]))

story.append(Paragraph("The Label", H2))
story.append(Paragraph(
    "Label = 1 if the consensus direction prediction turned out to be correct 24 hours later "
    "(i.e., final_direction == 'up' AND price_24h_later > price_at_analysis, or vice versa). "
    "Label = 0 if the prediction was wrong.", BODY))

story.append(Paragraph("Why GradientBoosting?", H2))
story.append(Paragraph(
    "GradientBoostingClassifier from scikit-learn is ideal here because: the dataset is small (tabular rows, "
    "not images or text), it handles mixed feature types well, it is interpretable via feature importances "
    "(you can see which AI model's votes matter most), and it does not require a GPU. "
    "The model uses 100 estimators and max_depth=3 to prevent overfitting on small datasets.", BODY))

story.append(Paragraph("Data Requirements", H2))
story.append(Paragraph(
    "The system requires a minimum of 20 labeled samples (analysis sessions with known 24h outcomes) before "
    "training is attempted. With fewer samples, the model would just memorize the training data. "
    "As you use NexusTrade over days and weeks, the dataset grows. The system retrains automatically "
    "every Sunday at 2am via APScheduler.", BODY))

story.append(Paragraph("Feature Importances", H2))
story.append(Paragraph(
    "After training, the model reports feature importances — which features it found most predictive. "
    "For example, if claude_conf has high importance, it means Claude's confidence score has been the "
    "most reliable predictor of correct outcomes in your history. This is how the system 'learns' which "
    "AI advisor to trust most over time.", BODY))

story.append(PageBreak())

# ── 7. Setup & Running ───────────────────────────────────────────────────────
story.append(Paragraph("7. Setup & Running Locally", H1))
story.append(hr())

story.append(Paragraph("Prerequisites", H2))
for item in ["Node.js 18+ (for the Next.js frontend)", "Python 3.11+ (for the FastAPI backend)",
             "git (for version control)"]:
    story.append(Paragraph(f"• {item}", BULLET))

story.append(Paragraph("Step-by-Step Setup", H2))
steps = [
    ["Step", "Command / Action"],
    ["1. Clone repo",       "git clone https://github.com/sohangowda11/TradeWithAi.git"],
    ["2. Backend deps",     "cd TradeWithAi/backend  →  pip install -r requirements.txt"],
    ["3. Create .env",      "copy backend\\.env.example backend\\.env  (then fill in keys)"],
    ["4. Start backend",    "cd backend  →  uvicorn app.main:app --reload --port 8000"],
    ["5. Frontend deps",    "cd frontend  →  npm install"],
    ["6. Start frontend",   "cd frontend  →  npm run dev"],
    ["7. Open browser",     "http://localhost:3000"],
]
story.append(tbl(steps, [3.5*cm, 12*cm]))

story.append(Paragraph("API Keys (all optional — mock mode works without them)", H2))
keys = [
    ["Service",    "Where to get it",                          "Env var"],
    ["Finnhub",    "finnhub.io → Dashboard → API Key",         "FINNHUB_API_KEY"],
    ["Anthropic",  "console.anthropic.com → API Keys",         "ANTHROPIC_API_KEY"],
    ["OpenAI",     "platform.openai.com → API Keys",           "OPENAI_API_KEY"],
    ["Google",     "aistudio.google.com → Get API Key",        "GOOGLE_API_KEY"],
    ["DeepSeek",   "platform.deepseek.com → API Keys",         "DEEPSEEK_API_KEY"],
]
story.append(tbl(keys, [3*cm, 7.5*cm, 5*cm]))

story.append(PageBreak())

# ── 8. Limitations & Disclaimers ─────────────────────────────────────────────
story.append(Paragraph("8. Limitations & Disclaimers", H1))
story.append(hr())

disclaimers = [
    ("NOT Financial Advice",
     "NexusTrade is an educational simulation tool. Nothing in this application "
     "constitutes financial advice, investment recommendations, or trading signals for real markets. "
     "Do not make real investment decisions based on this system's output."),

    ("LLMs Do Not Have Real-Time Data",
     "Claude, GPT-4o, Gemini, and DeepSeek were trained on historical text data with knowledge cutoffs. "
     "They reason from patterns in their training data, not from actual current market knowledge. "
     "Their 'analysis' is a synthesis of general financial reasoning, not privileged market intelligence."),

    ("Past Accuracy Does Not Predict Future Accuracy",
     "Even if the custom meta-model shows high accuracy on historical votes, this does not guarantee "
     "future performance. Markets are non-stationary — conditions change, correlations break down, "
     "and black swan events invalidate all technical signals simultaneously."),

    ("Paper vs. Real Trading",
     "Paper trading eliminates psychological factors (fear, greed, FOMO) that heavily influence "
     "real trading performance. A strategy that works perfectly in simulation often performs worse "
     "when real money is at stake."),

    ("API Rate Limits and Costs",
     "Running 8 AI API calls per analysis across 4 providers can be expensive at scale. "
     "Each analysis session costs roughly $0.02-0.50 in API tokens depending on providers used. "
     "The backend enforces a MAX_AI_COST_PER_ANALYSIS cap ($0.50 by default) configurable in settings."),

    ("24-Hour Outcome Window",
     "The system evaluates prediction accuracy by checking if the price moved in the predicted "
     "direction 24 hours after the analysis. This is a significant oversimplification — real trading "
     "involves multiple timeframes, stop losses, position sizing, and exit strategies."),

    ("SQLite for Development Only",
     "The default database is SQLite. For any production deployment handling concurrent users, "
     "this should be upgraded to PostgreSQL (Supabase, Railway, or Neon all offer free tiers)."),
]

for title, text in disclaimers:
    story.append(Paragraph(title, H3))
    story.append(Paragraph(text, BODY))
    story.append(Spacer(1, 0.2*cm))

story.append(Spacer(1, 1*cm))
story.append(hr())
story.append(Paragraph(
    "NexusTrade is a portfolio/learning project. "
    "Built with Next.js 16, FastAPI, Three.js, and 4 LLM APIs.",
    BODY_MUTED))

# ── Build ─────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written to: {OUTPUT}")
