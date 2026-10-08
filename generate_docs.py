from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime

OUTPUT = r"C:\Users\sohan\stock-trading-sim\NexusTrade_Documentation.pdf"

# ── Color Palette (Clean Executive Light Theme) ──────────────────────────────
PRIMARY_DARK  = colors.HexColor("#0f172a")  # Slate 900 - Dark charcoal headers
PRIMARY_BLUE  = colors.HexColor("#1e40af")  # Blue 800 - Deep brand blue
ACCENT_BLUE   = colors.HexColor("#2563eb")  # Blue 600 - Accent blue
TEAL_ACCENT   = colors.HexColor("#0f766e")  # Teal 700 - Subheadings
TEXT_DARK     = colors.HexColor("#1e293b")  # Slate 800 - Body text (crisp & high contrast)
TEXT_MUTED    = colors.HexColor("#64748b")  # Slate 500 - Secondary text
BG_LIGHT      = colors.HexColor("#f8fafc")  # Slate 50 - Alternating table rows
BG_HEADER     = colors.HexColor("#0f172a")  # Slate 900 - Table header BG
BG_CALLOUT    = colors.HexColor("#f0f9ff")  # Sky 50 - Callout box BG
BORDER_COLOR  = colors.HexColor("#cbd5e1")  # Slate 300 - Table grid lines
CODE_BG       = colors.HexColor("#f1f5f9")  # Slate 100 - Code block BG
CODE_BORDER   = colors.HexColor("#cbd5e1")  # Slate 300 - Code border

# ── Typography & Styles ──────────────────────────────────────────────────────
base_styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

TITLE_STYLE = S("DocTitle",
    fontSize=26, leading=32, textColor=PRIMARY_DARK,
    fontName="Helvetica-Bold", spaceAfter=4, alignment=TA_LEFT)

SUBTITLE_STYLE = S("DocSubtitle",
    fontSize=12.5, leading=17, textColor=PRIMARY_BLUE,
    fontName="Helvetica-Bold", spaceAfter=14, alignment=TA_LEFT)

H1 = S("H1",
    fontSize=15, leading=20, textColor=PRIMARY_DARK,
    fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6,
    keepWithNext=True)

H2 = S("H2",
    fontSize=11.5, leading=16, textColor=PRIMARY_BLUE,
    fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4,
    keepWithNext=True)

H3 = S("H3",
    fontSize=10, leading=14, textColor=TEAL_ACCENT,
    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3,
    keepWithNext=True)

BODY = S("BodyTextCustom",
    fontSize=9.5, leading=14.5, textColor=TEXT_DARK,
    fontName="Helvetica", spaceAfter=7, alignment=TA_JUSTIFY)

BODY_MUTED = S("BodyMutedCustom",
    fontSize=8.5, leading=13, textColor=TEXT_MUTED,
    fontName="Helvetica", spaceAfter=6)

BULLET = S("BulletCustom",
    fontSize=9.5, leading=14, textColor=TEXT_DARK,
    fontName="Helvetica", spaceAfter=4, leftIndent=14)

CODE_STYLE = S("CodeSnippet",
    fontSize=8.5, leading=13, textColor=PRIMARY_DARK,
    fontName="Courier", spaceAfter=6,
    backColor=CODE_BG, borderColor=CODE_BORDER, borderWidth=0.5,
    borderPadding=(6, 8, 6, 8))

TBL_HEADER = S("TblHeader", fontSize=9, leading=12, textColor=colors.white, fontName="Helvetica-Bold")
TBL_CELL   = S("TblCell", fontSize=8.5, leading=12.5, textColor=TEXT_DARK, fontName="Helvetica")
TBL_CELL_BOLD = S("TblCellBold", fontSize=8.5, leading=12.5, textColor=PRIMARY_DARK, fontName="Helvetica-Bold")

def hr():
    return HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10, spaceBefore=4)

def make_table(data, col_widths, header=True):
    formatted_data = []
    for row_idx, row in enumerate(data):
        formatted_row = []
        for col_idx, cell in enumerate(row):
            if row_idx == 0 and header:
                p = Paragraph(str(cell), TBL_HEADER)
            else:
                if col_idx == 0 and header:
                    p = Paragraph(str(cell), TBL_CELL_BOLD)
                else:
                    p = Paragraph(str(cell), TBL_CELL)
            formatted_row.append(p)
        formatted_data.append(formatted_row)
    
    t = Table(formatted_data, colWidths=col_widths)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0 if header else -1), BG_HEADER),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]
    if header and len(data) > 1:
        style.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]))
    elif not header:
        style.append(("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG_LIGHT]))
        
    t.setStyle(TableStyle(style))
    return t

def make_callout(title, text, width=17.0*cm):
    content = []
    if title:
        content.append(Paragraph(f"<b>{title}</b>", S("CalloutHeader", fontSize=9.5, leading=14, textColor=PRIMARY_BLUE, fontName="Helvetica-Bold", spaceAfter=3)))
    content.append(Paragraph(text, S("CalloutBody", fontSize=9, leading=13.5, textColor=TEXT_DARK, fontName="Helvetica", spaceAfter=0)))
    
    t = Table([[content]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CALLOUT),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
        ("LINELEFT",     (0, 0), (0, 0), 3.5, ACCENT_BLUE),
    ]))
    return t

# ── Dynamic Canvas with Header & Footer ──────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Top Banner on Cover Page
            self.saveState()
            self.setFillColor(PRIMARY_DARK)
            self.rect(0, 842 - 12, 595, 12, fill=True, stroke=False)
            self.setFillColor(ACCENT_BLUE)
            self.rect(0, 842 - 16, 595, 4, fill=True, stroke=False)
            self.restoreState()
            return

        self.saveState()
        # Top Running Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(PRIMARY_DARK)
        self.drawString(54, 842 - 34, "NEXUSTRADE")
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        self.drawString(120, 842 - 34, "|   AI-Powered Stock Trading Simulator")
        self.drawRightString(595 - 54, 842 - 34, "Technical Documentation")
        
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 842 - 40, 595 - 54, 842 - 40)

        # Bottom Running Footer
        self.line(54, 45, 595 - 54, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        self.drawString(54, 32, "NexusTrade Documentation — Educational & Technical Reference")
        self.drawRightString(595 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        
        self.restoreState()

# ── Document Setup ────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=1.9*cm, rightMargin=1.9*cm,
    topMargin=1.8*cm, bottomMargin=1.8*cm,
    title="NexusTrade Documentation",
    author="NexusTrade Team",
)

story = []

# ── Cover Page ────────────────────────────────────────────────────────────────
story.append(Spacer(1, 1.5*cm))
story.append(Paragraph("NEXUSTRADE", TITLE_STYLE))
story.append(Paragraph("AI-Powered Multi-Model Stock Trading Simulator", SUBTITLE_STYLE))
story.append(hr())
story.append(Spacer(1, 0.4*cm))

story.append(make_callout(
    "Executive Overview",
    "NexusTrade is a full-stack, enterprise-grade stock trading simulator that harnesses multi-agent AI deliberation "
    "(Claude, GPT-4o, Gemini 1.5 Pro, DeepSeek Chat) to analyze stock market trends, deliberate across multiple rounds, "
    "and execute paper trades with intelligent Kelly-criterion position sizing. This document provides complete architectural, "
    "mathematical, and implementation details."
))

story.append(Spacer(1, 0.6*cm))
story.append(Paragraph("Project Metadata & Tech Stack", H2))

cover_info = [
    ["System Component", "Technology & Details"],
    ["Frontend Stack",   "Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS v4 · Zustand"],
    ["Backend Stack",    "FastAPI · Python 3.11 · SQLAlchemy 2 · SQLite / PostgreSQL · Pydantic v2"],
    ["AI Intelligence",  "Claude Sonnet · GPT-4o · Gemini 1.5 Pro · DeepSeek Chat (2-Round Deliberation)"],
    ["Market Data",      "Finnhub API (Real-time candles & news) with full deterministic mock fallback"],
    ["Visualizations",   "Three.js particle canvas · TradingView lightweight-charts v5"],
    ["Paper Wallet",     "$100,000 starting virtual balance with FIFO cost basis tracking"],
    ["Repository URL",   "https://github.com/sohangowda11/NexusTrade.git"],
]
story.append(make_table(cover_info, [4.5*cm, 12.5*cm]))

story.append(Spacer(1, 0.6*cm))
story.append(Paragraph(f"Documentation Generated: {datetime.now().strftime('%B %d, %Y')}", BODY_MUTED))
story.append(PageBreak())

# ── 1. Introduction to Stock Trading ─────────────────────────────────────────
story.append(Paragraph("1. Introduction to Stock Trading & Paper Trading", H1))
story.append(hr())

story.append(Paragraph("What Is a Stock?", H2))
story.append(Paragraph(
    "A stock (equity share) represents a fractional ownership unit in a publicly traded corporation. "
    "When companies require growth capital, they issue shares via an Initial Public Offering (IPO). "
    "Owning shares entitles shareholders to proportionate equity ownership, voting rights, and potential dividend distributions.", BODY))

story.append(Paragraph("How Prices Move: Market Microstructure", H2))
story.append(Paragraph(
    "Stock prices fluctuate continuously based on real-time order matching between buyers (bids) and sellers (asks). "
    "Prices are driven by corporate earnings reports, macroeconomic metrics (interest rates, inflation, GDP growth), "
    "industry sector rotation, geopolitical events, and market sentiment.", BODY))

story.append(Paragraph("Core Financial Terminology", H2))
terms = [
    ["Term", "Technical Definition"],
    ["Market Cap", "Total market value of outstanding shares = Share Price × Shares Outstanding"],
    ["Volatility", "Standard deviation of price returns over a specified period. High volatility indicates greater price swings"],
    ["Bid / Ask Spread", "Bid = maximum price buyers offer. Ask = minimum price sellers accept. Spread = Ask − Bid"],
    ["Volume", "Total number of shares traded during a given timeframe. High volume validates price breakouts"],
    ["P/E Ratio", "Price-to-Earnings ratio = Share Price / Earnings Per Share (EPS). Evaluates valuation relative to earnings"],
    ["Bull / Bear Market", "Bull = sustained upward market trend (+20% from lows). Bear = sustained downward trend (-20% from highs)"],
    ["Liquidity", "The ease with which an asset can be converted into cash without affecting market price"],
]
story.append(make_table(terms, [4.0*cm, 13.0*cm]))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("Why Paper Trading Matters", H2))
story.append(Paragraph(
    "Paper trading simulates live stock transactions using virtual funds while tracking real market prices. "
    "It allows traders and quantitative models to evaluate entry/exit rules, refine risk parameters, and measure strategy performance "
    "without risking capital. NexusTrade is a simulated trading environment — all trades use virtual currency.", BODY))

story.append(PageBreak())

# ── 2. AI Voting & Deliberation Architecture ─────────────────────────────────
story.append(Paragraph("2. Multi-Model AI Voting & Deliberation Engine", H1))
story.append(hr())

story.append(Paragraph("Architectural Overview", H2))
story.append(Paragraph(
    "NexusTrade models stock market decision-making as a multi-agent consensus problem. "
    "Rather than depending on a single LLM, the engine queries four distinct state-of-the-art models in parallel, "
    "processes their independent outputs, and conducts a secondary discussion round where models evaluate peer perspectives.", BODY))

story.append(make_callout(
    "Key Innovation: 2-Round Multi-Agent Deliberation",
    "Single-agent LLM prompts suffer from hallucination and bias. NexusTrade introduces a structured 2-round protocol: "
    "Round 1 gathers un-anchored independent votes. Round 2 presents each model with an anonymized summary of peer reasoning, "
    "allowing models to refine or uphold their predictions based on cross-examination."
))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("Model Input Prompt Structure", H2))
story.append(Paragraph("Every AI model receives a standardized contextual prompt containing:", BODY))
for item in [
    "Ticker Symbol & Company Overview (e.g., AAPL, NVDA, TSLA)",
    "Real-time Price Metrics: Current price, day change %, 52-week high/low",
    "Technical Indicators: RSI (14), MACD Signal Line & Histogram, SMA 20, SMA 50, Bollinger Bands",
    "News Sentiment: Top 5 recent Finnhub market news headlines (last 48 hours)",
    "Strict Output Constraint: Structured JSON output contract",
]:
    story.append(Paragraph(f"• {item}", BULLET))

story.append(Paragraph("JSON Response Schema", H2))
story.append(Paragraph(
    '{"direction": "up" | "down", "confidence": 0-100, "risk_level": "low" | "medium" | "high", "reasoning": "Concise justification"}', CODE_STYLE))

story.append(Paragraph("Consensus Aggregation Algorithm", H2))
agg = [
    ["Signal Output", "Mathematical Aggregation Rule"],
    ["Final Direction", "Majority vote among Round 2 predictions. Ties default to 'uncertain'"],
    ["Final Confidence", "Weighted average of confidence scores from models supporting the majority vote"],
    ["Final Risk Level", "Conservative Escalation: If ANY model flags 'high' risk, overall risk escalates to 'high'"],
    ["Consensus Score",  "Percentage of models aligned with majority direction (e.g., 4/4 = 100%, 3/4 = 75%)"],
]
story.append(make_table(agg, [4.0*cm, 13.0*cm]))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("Deterministic Mock Mode Fallback", H2))
story.append(Paragraph(
    "If API keys are omitted or network requests fail, the backend seamlessly routes to a deterministic mock service. "
    "Mock outputs are deterministically hashed from ticker symbol + model ID, providing consistent demonstration signals "
    "without requiring paid API credentials.", BODY))

story.append(PageBreak())

# ── 3. Paper Trading Engine & Risk Management ────────────────────────────────
story.append(Paragraph("3. Paper Trading Engine & Risk Management", H1))
story.append(hr())

story.append(Paragraph("Virtual Portfolio & Account Balance", H2))
story.append(Paragraph(
    "Every session initializes with $100,000.00 in virtual USD cash balance, stored within the SQLite database. "
    "Users can perform simulated buy/sell orders, deposit/withdraw virtual capital, and track position performance in real-time.", BODY))

story.append(Paragraph("FIFO Cost Basis & Average Price Calculation", H2))
story.append(Paragraph(
    "When accumulating shares across multiple orders, the system updates the weighted average cost basis:", BODY))
story.append(Paragraph("New Average Cost = (Existing Shares × Existing Avg Cost + New Shares × New Price) / Total Shares", CODE_STYLE))

story.append(Paragraph("Optimal Position Sizing: The Kelly Criterion", H2))
story.append(Paragraph(
    "NexusTrade features automated position sizing based on Kelly Criterion gambling math. "
    "The Kelly fraction determines the optimal percentage of available cash to allocate:", BODY))
story.append(Paragraph("Kelly Fraction f* = max(0,  2 × p − 1)    [where p = model_confidence / 100]", CODE_STYLE))

story.append(Paragraph("Risk-Adjusted Position Caps", H2))
story.append(Paragraph("To prevent over-leveraging, the Kelly fraction is capped by the risk level of the analysis signal:", BODY))

risk_tbl = [
    ["Signal Risk Level", "Maximum Cash Allocation Cap", "Example Execution ($50,000 Cash, 70% Confidence → f* = 40%)"],
    ["Low Risk",          "15% max allocation",          "min(40%, 15%) × $50,000 = $7,500 position size"],
    ["Medium Risk",       "10% max allocation",          "min(40%, 10%) × $50,000 = $5,000 position size"],
    ["High Risk",         "5% max allocation",           "min(40%, 5%)  × $50,000 = $2,500 position size"],
]
story.append(make_table(risk_tbl, [3.2*cm, 4.5*cm, 9.3*cm]))

story.append(PageBreak())

# ── 4. System Architecture & Data Schema ──────────────────────────────────────
story.append(Paragraph("4. Full-Stack System Architecture & Data Schemas", H1))
story.append(hr())

story.append(Paragraph("Frontend Technology Stack", H2))
arch_front = [
    ["Technology",      "Role & Implementation Purpose"],
    ["Next.js 16",      "React Framework with App Router, SSR, and Client Component optimization"],
    ["React 19",        "Modern UI library with concurrent rendering primitives"],
    ["TypeScript",      "Strict static typing across API payloads, state stores, and component props"],
    ["Tailwind CSS v4", "CSS-first utility design system with customized fintech color tokens"],
    ["Zustand",         "Lightweight persistent client state (wallet, holdings, trade history)"],
    ["React Query",     "Server state management, background polling, and cache invalidation"],
    ["Three.js",        "Canvas particle field hero visual background"],
    ["lightweight-charts", "TradingView high-performance canvas stock chart component"],
]
story.append(make_table(arch_front, [4.5*cm, 12.5*cm]))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("Backend Technology Stack", H2))
arch_back = [
    ["Framework / Library", "Role & Implementation Purpose"],
    ["FastAPI",            "Asynchronous Python web framework with OpenAPI validation"],
    ["SQLAlchemy 2",       "Object-Relational Mapping (ORM) for database models"],
    ["SQLite / PostgreSQL","Relational storage for trades, portfolios, and AI session history"],
    ["scikit-learn",       "GradientBoostingClassifier for meta-model training on past AI predictions"],
    ["httpx",              "Async HTTP client for parallel LLM and market API calls"],
]
story.append(make_table(arch_back, [4.5*cm, 12.5*cm]))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("Database Schema Definitions", H2))
db_schema = [
    ["Table Name",       "Primary Columns & Descriptions"],
    ["Portfolio",        "id (PK), cash_balance (Float), created_at, updated_at"],
    ["Holding",          "id (PK), portfolio_id (FK), ticker (String), shares (Float), avg_price (Float)"],
    ["Trade",            "id (PK), portfolio_id (FK), ticker, action (BUY/SELL), shares, price, total, pnl, timestamp"],
    ["AnalysisSession",  "id (PK), ticker, final_direction, final_confidence, final_risk, consensus_score, timestamp"],
    ["AIVote",           "id (PK), session_id (FK), model_name, direction, confidence, risk_level, reasoning, round"],
]
story.append(make_table(db_schema, [4.0*cm, 13.0*cm]))

story.append(PageBreak())

# ── 5. Technical Indicators ──────────────────────────────────────────────────
story.append(Paragraph("5. Technical Analysis Indicators", H1))
story.append(hr())

story.append(Paragraph("RSI (Relative Strength Index - 14 Period)", H2))
story.append(Paragraph(
    "RSI measures momentum on a 0-100 scale. RSI > 70 indicates overbought conditions (potential pullback), "
    "while RSI < 30 indicates oversold conditions (potential reversal bounce).", BODY))

story.append(Paragraph("MACD (Moving Average Convergence Divergence)", H2))
story.append(Paragraph(
    "MACD compares 12-period and 26-period EMAs against a 9-period Signal line. "
    "Positive histogram values confirm bullish momentum; negative values signal bearish pressure.", BODY))

story.append(Paragraph("Bollinger Bands (20 Period, 2 Standard Deviations)", H2))
story.append(Paragraph(
    "Bollinger Bands define high/low volatility envelopes around the 20-day SMA. "
    "Band squeezes indicate impending volatility expansion.", BODY))

story.append(Paragraph("Simple Moving Averages (SMA 20 & SMA 50)", H2))
story.append(Paragraph(
    "SMA 20 tracks short-term trends, while SMA 50 tracks medium-term direction. "
    "Golden Cross (SMA 50 > SMA 200) signifies long-term bullish bias.", BODY))

story.append(Spacer(1, 0.4*cm))
story.append(PageBreak())

# ── 6. Custom Meta-Model Training ───────────────────────────────────────────
story.append(Paragraph("6. Machine Learning Meta-Model Training", H1))
story.append(hr())

story.append(Paragraph("How Meta-Model Training Works", H2))
story.append(Paragraph(
    "NexusTrade includes a scikit-learn meta-model (GradientBoostingClassifier) that learns which AI models are historically "
    "most accurate under specific market conditions. Rather than replacing LLMs, the meta-model acts as a data-driven referee.", BODY))

story.append(Paragraph("Feature Matrix Representation", H2))
features = [
    ["Feature Category", "Input Features & Normalization"],
    ["Model Directional Votes", "claude_dir, gpt_dir, gemini_dir, deepseek_dir (Encoded: 1=UP, 0=DOWN, -1=NONE)"],
    ["Model Confidence",        "claude_conf, gpt_conf, gemini_conf, deepseek_conf (Normalized 0.0 to 1.0)"],
    ["Model Risk Flags",        "claude_risk, gpt_risk, gemini_risk, deepseek_risk (Encoded: 0=Low, 1=Med, 2=High)"],
    ["Consensus & Time",        "consensus_score (0-100), weekday (0-6), hour_of_day (0-23)"],
]
story.append(make_table(features, [5.0*cm, 12.0*cm]))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("Training Trigger & Execution", H2))
story.append(Paragraph(
    "The meta-model requires a minimum of 20 historical sessions with verified 24-hour outcome labels before training. "
    "An automated background cron job (APScheduler) retrains the classifier every Sunday at 02:00 AM.", BODY))

story.append(PageBreak())

# ── 7. Setup & Execution Guide ───────────────────────────────────────────────
story.append(Paragraph("7. Local Setup & Execution Guide", H1))
story.append(hr())

story.append(Paragraph("Prerequisites", H2))
for item in ["Node.js 18+ & npm", "Python 3.11+", "Git"]:
    story.append(Paragraph(f"• {item}", BULLET))

story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("Step-by-Step Installation", H2))
steps = [
    ["Step", "Action & Command"],
    ["1. Clone Repository",  "git clone https://github.com/sohangowda11/NexusTrade.git"],
    ["2. Setup Backend",     "cd NexusTrade/backend  &&  pip install -r requirements.txt"],
    ["3. Environment Config","copy backend\\.env.example backend\\.env"],
    ["4. Launch Backend",    "cd backend  &&  uvicorn app.main:app --reload --port 8000"],
    ["5. Setup Frontend",    "cd frontend  &&  npm install"],
    ["6. Launch Frontend",   "cd frontend  &&  npm run dev"],
    ["7. Access App",        "Open http://localhost:3000 in your web browser"],
]
story.append(make_table(steps, [3.8*cm, 13.2*cm]))
story.append(Spacer(1, 0.4*cm))

story.append(Paragraph("API Keys Configuration (Optional)", H2))
keys = [
    ["Provider",  "Environment Variable", "Description"],
    ["Finnhub",   "FINNHUB_API_KEY",      "Real-time stock candles & news headlines"],
    ["Anthropic", "ANTHROPIC_API_KEY",    "Claude Sonnet multi-agent voting"],
    ["OpenAI",    "OPENAI_API_KEY",       "GPT-4o multi-agent voting"],
    ["Google",    "GOOGLE_API_KEY",       "Gemini 1.5 Pro multi-agent voting"],
    ["DeepSeek",  "DEEPSEEK_API_KEY",     "DeepSeek Chat multi-agent voting"],
]
story.append(make_table(keys, [3.0*cm, 5.0*cm, 9.0*cm]))

story.append(PageBreak())

# ── 8. Disclaimers & Notes ───────────────────────────────────────────────────
story.append(Paragraph("8. Educational Disclaimers", H1))
story.append(hr())

story.append(make_callout(
    "IMPORTANT DISCLAIMER — NOT FINANCIAL ADVICE",
    "NexusTrade is strictly an educational software simulation. Predictions, consensus signals, and Kelly criterion "
    "calculations generated by this software do NOT constitute financial advice, investment recommendations, or trading endorsements. "
    "Never make real-world financial investments based on AI model predictions or paper trading outputs."
))

story.append(Spacer(1, 1.0*cm))
story.append(hr())
story.append(Paragraph("NexusTrade Technical Documentation — Built with Next.js 16, FastAPI, and Multi-Agent LLMs.", BODY_MUTED))

# ── Build Document ───────────────────────────────────────────────────────────
doc.build(story, canvasmaker=NumberedCanvas)
print(f"PDF successfully generated: {OUTPUT}")
