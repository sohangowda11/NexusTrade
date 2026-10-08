import asyncio
import json
import random
import logging
from dataclasses import dataclass
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    name: str
    model_id: str
    provider: str
    weight: float = 1.0

    @property
    def enabled(self) -> bool:
        key_map = {
            "anthropic": settings.ANTHROPIC_API_KEY,
            "openai": settings.OPENAI_API_KEY,
            "google": settings.GOOGLE_API_KEY,
            "deepseek": settings.DEEPSEEK_API_KEY,
        }
        return bool(key_map.get(self.provider, ""))


MODELS = [
    ModelConfig("Claude Sonnet", "claude-sonnet-4-5", "anthropic"),
    ModelConfig("GPT-4o", "gpt-4o", "openai"),
    ModelConfig("Gemini 1.5 Pro", "gemini-1.5-pro", "google"),
    ModelConfig("DeepSeek Chat", "deepseek-chat", "deepseek"),
]


def build_analysis_prompt(ticker: str, price_summary: str, news_summary: str, indicators: dict) -> str:
    return f"""You are a quantitative stock analyst. Analyze the following data for {ticker} and provide a structured prediction.

PRICE DATA (last 30 days):
{price_summary}

RECENT NEWS (last 48 hours):
{news_summary}

TECHNICAL INDICATORS:
- RSI (14): {indicators.get('rsi', 'N/A')}
- MACD trend: {indicators.get('macd_trend', 'N/A')}
- 20-day SMA: {indicators.get('sma20', 'N/A')}
- 50-day SMA: {indicators.get('sma50', 'N/A')}
- Volume trend: {indicators.get('volume_trend', 'N/A')}
- 5-day momentum: {indicators.get('momentum_5d', 'N/A')}%

Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{{"direction": "up" or "down", "confidence": <integer 0-100>, "risk_level": "low" or "medium" or "high", "reasoning": "<2-3 sentence explanation>"}}"""


def build_discussion_prompt(ticker: str, own_vote: dict, other_votes: list) -> str:
    others = "\n".join([
        f"- {v['model']}: {v['direction']} ({v['confidence']}% confidence, {v['risk']} risk) — {v['reasoning']}"
        for v in other_votes
    ])
    return f"""You previously predicted {ticker} would go {own_vote['direction']} with {own_vote['confidence']}% confidence ({own_vote['risk_level']} risk).

Other AI analysts predicted:
{others}

Considering their perspectives and reasoning, update your prediction if warranted. Stay independent — only change if genuinely persuaded.
Respond ONLY with valid JSON (no markdown):
{{"direction": "up" or "down", "confidence": <integer 0-100>, "risk_level": "low" or "medium" or "high", "reasoning": "<2-3 sentences>"}}"""


def parse_ai_json(text: str) -> Optional[dict]:
    """Extract and validate JSON from an AI response."""
    text = text.strip()
    # Strip markdown code fences if present
    if "```" in text:
        start = text.find("{", text.find("```"))
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
    # Find first { ... }
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        text = text[start:end]
    except ValueError:
        return None
    try:
        data = json.loads(text)
        required = {"direction", "confidence", "risk_level", "reasoning"}
        if not required.issubset(data.keys()):
            return None
        if data["direction"] not in ("up", "down"):
            return None
        if not isinstance(data["confidence"], (int, float)) or not (0 <= data["confidence"] <= 100):
            return None
        if data["risk_level"] not in ("low", "medium", "high"):
            return None
        return data
    except Exception:
        return None


def mock_ai_response(model_name: str, ticker: str) -> dict:
    """Deterministic mock seeded by model+ticker — stable within a session."""
    seed = sum(ord(c) for c in model_name + ticker)
    rng = random.Random(seed)
    direction = "up" if rng.random() > 0.45 else "down"
    confidence = rng.randint(52, 82)
    risk = rng.choice(["low", "medium", "high"])
    tone = "positive momentum and improving fundamentals" if direction == "up" else "near-term headwinds and elevated valuation risk"
    reasoning = (
        f"{ticker} shows {tone} based on recent price action and technical structure. "
        f"{'RSI is recovering from oversold levels, supporting the bullish case.' if direction == 'up' else 'MACD histogram is turning negative, signaling potential downside.'} "
        f"Risk is {risk} given current market conditions and sector rotation dynamics."
    )
    return {"direction": direction, "confidence": confidence, "risk_level": risk, "reasoning": reasoning}


async def call_anthropic(prompt: str, model_id: str) -> Optional[dict]:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = await client.messages.create(
            model=model_id,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return parse_ai_json(msg.content[0].text)
    except Exception as e:
        logger.warning(f"Anthropic call failed: {e}")
        return None


async def call_openai_compat(prompt: str, model_id: str, api_key: str, base_url: Optional[str] = None) -> Optional[dict]:
    try:
        from openai import AsyncOpenAI
        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        client = AsyncOpenAI(**kwargs)
        resp = await client.chat.completions.create(
            model=model_id,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return parse_ai_json(resp.choices[0].message.content or "")
    except Exception as e:
        logger.warning(f"OpenAI-compat call failed ({model_id}): {e}")
        return None


async def call_google(prompt: str, model_id: str) -> Optional[dict]:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel(model_id)
        resp = await asyncio.to_thread(model.generate_content, prompt)
        return parse_ai_json(resp.text)
    except Exception as e:
        logger.warning(f"Google call failed: {e}")
        return None


async def call_model(model: ModelConfig, prompt: str) -> Optional[dict]:
    if not model.enabled:
        return None
    if model.provider == "anthropic":
        return await call_anthropic(prompt, model.model_id)
    elif model.provider == "openai":
        return await call_openai_compat(prompt, model.model_id, settings.OPENAI_API_KEY)
    elif model.provider == "google":
        return await call_google(prompt, model.model_id)
    elif model.provider == "deepseek":
        return await call_openai_compat(
            prompt, model.model_id, settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
    return None


def aggregate_votes(votes: list) -> dict:
    if not votes:
        return {"direction": "uncertain", "confidence": 0, "risk_level": "high", "consensus_score": 0}
    up_votes = [v for v in votes if v["direction"] == "up"]
    down_votes = [v for v in votes if v["direction"] == "down"]
    if len(up_votes) > len(down_votes):
        direction, majority = "up", up_votes
    elif len(down_votes) > len(up_votes):
        direction, majority = "down", down_votes
    else:
        direction, majority = "uncertain", votes
    confidence = sum(v["confidence"] for v in majority) / len(majority) if majority else 0
    risks = [v["risk_level"] for v in votes]
    risk = "high" if "high" in risks else ("medium" if "medium" in risks else "low")
    consensus_score = (max(len(up_votes), len(down_votes)) / len(votes)) * 100 if votes else 0
    return {
        "direction": direction,
        "confidence": round(confidence, 1),
        "risk_level": risk,
        "consensus_score": round(consensus_score, 1),
    }


async def run_analysis_session(ticker: str, price_summary: str, news_summary: str, indicators: dict) -> dict:
    prompt = build_analysis_prompt(ticker, price_summary, news_summary, indicators)

    async def get_vote_r1(model: ModelConfig) -> dict:
        try:
            result = await asyncio.wait_for(call_model(model, prompt), timeout=25.0)
        except asyncio.TimeoutError:
            result = None
        if result is None:
            result = mock_ai_response(model.name, ticker)
            result["is_mock"] = True
        result["model_name"] = model.name
        result["round"] = 1
        return result

    r1_tasks = [get_vote_r1(m) for m in MODELS]
    r1_raw = await asyncio.gather(*r1_tasks, return_exceptions=True)
    r1_votes = [v for v in r1_raw if isinstance(v, dict)]

    # Round 2: discussion
    async def get_vote_r2(model: ModelConfig, own_r1: dict) -> dict:
        others = [
            {"model": v["model_name"], "direction": v["direction"],
             "confidence": v["confidence"], "risk": v["risk_level"], "reasoning": v["reasoning"]}
            for v in r1_votes if v["model_name"] != model.name
        ]
        disc_prompt = build_discussion_prompt(ticker, own_r1, others)
        try:
            result = await asyncio.wait_for(call_model(model, disc_prompt), timeout=25.0)
        except asyncio.TimeoutError:
            result = None
        if result is None:
            # Keep round-1 answer as the round-2 answer
            result = {k: own_r1[k] for k in ("direction", "confidence", "risk_level", "reasoning")}
            result["is_mock"] = True
        result["model_name"] = model.name
        result["round"] = 2
        return result

    r2_tasks = []
    for i, model in enumerate(MODELS):
        matching_r1 = next((v for v in r1_votes if v["model_name"] == model.name), None)
        if matching_r1:
            r2_tasks.append(get_vote_r2(model, matching_r1))

    r2_raw = await asyncio.gather(*r2_tasks, return_exceptions=True)
    r2_votes = [v for v in r2_raw if isinstance(v, dict)]

    aggregated = aggregate_votes(r2_votes)
    aggregated_reasoning = " | ".join(
        f"{v['model_name']}: {v['reasoning'][:120]}" for v in r2_votes[:2]
    )

    return {
        "ticker": ticker,
        "round1_votes": r1_votes,
        "round2_votes": r2_votes,
        "final_direction": aggregated["direction"],
        "final_confidence": aggregated["confidence"],
        "final_risk": aggregated["risk_level"],
        "consensus_score": aggregated["consensus_score"],
        "aggregated_reasoning": aggregated_reasoning,
    }
