"use client";
import { useState } from "react";
import { useTradingStore, AnalysisResult } from "@/store/tradingStore";
import { executeTrade } from "@/lib/api";
import { ShoppingCart, TrendingDown, AlertTriangle } from "lucide-react";

interface Props {
  ticker: string;
  currentPrice: number;
  analysisResult?: AnalysisResult | null;
}

export default function TradeExecutor({ ticker, currentPrice, analysisResult }: Props) {
  const { cash, holdings, addTrade, updateHolding } = useTradingStore();
  const [action, setAction] = useState<"buy" | "sell">("buy");
  const [shares, setShares] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  const holding = holdings.find((h) => h.ticker === ticker.toUpperCase());
  const total = parseFloat(shares || "0") * currentPrice;

  // Kelly-criterion recommendation
  const getRecommendation = () => {
    if (!analysisResult) return null;
    const p = analysisResult.final_confidence / 100;
    const kelly = Math.max(0, 2 * p - 1);
    const caps: Record<string, number> = { low: 0.15, medium: 0.10, high: 0.05 };
    const cap = caps[analysisResult.final_risk] ?? 0.10;
    const fraction = Math.min(kelly, cap);
    const value = cash * fraction;
    const recShares = Math.floor(value / currentPrice);
    return { shares: recShares, value: recShares * currentPrice, fraction };
  };

  const rec = getRecommendation();

  const handleTrade = async () => {
    const qty = parseFloat(shares);
    if (!qty || qty <= 0) { setError("Enter a valid share count"); return; }
    if (action === "buy" && qty * currentPrice > cash) { setError("Insufficient cash"); return; }
    if (action === "sell" && (!holding || holding.shares < qty)) {
      setError(`Only ${holding?.shares ?? 0} shares available`); return;
    }
    setError(null);
    setSubmitting(true);
    const tradeReq = { ticker, action, shares: qty, price: currentPrice };
    try {
      await executeTrade(tradeReq);
    } catch {
      /* fall through to local store */
    }
    updateHolding(ticker, qty, currentPrice, action);
    addTrade({
      id: Date.now().toString(),
      ticker,
      action,
      shares: qty,
      price: currentPrice,
      total: qty * currentPrice,
      timestamp: new Date().toISOString(),
      pnl: action === "sell" && holding ? (currentPrice - holding.avgPrice) * qty : undefined,
    });
    setSuccess(`${action === "buy" ? "Bought" : "Sold"} ${qty} × ${ticker} @ $${currentPrice.toFixed(2)}`);
    setShares("");
    setSubmitting(false);
    setTimeout(() => setSuccess(null), 4000);
  };

  return (
    <div className="glass-card p-5">
      <h3 className="num font-bold text-sm mb-4" style={{ color: "var(--color-cyan)" }}>
        EXECUTE TRADE
      </h3>

      {/* Buy / Sell toggle */}
      <div className="flex gap-2 mb-4">
        {(["buy", "sell"] as const).map((a) => (
          <button
            key={a}
            onClick={() => setAction(a)}
            className="flex-1 py-2 rounded-lg num text-sm font-bold transition-all"
            style={{
              background:
                action === a
                  ? a === "buy"
                    ? "rgba(16,185,129,0.2)"
                    : "rgba(239,68,68,0.2)"
                  : "rgba(255,255,255,0.05)",
              color:
                action === a
                  ? a === "buy"
                    ? "var(--color-positive)"
                    : "var(--color-negative)"
                  : "var(--color-muted)",
              border: `1px solid ${
                action === a
                  ? a === "buy"
                    ? "rgba(16,185,129,0.4)"
                    : "rgba(239,68,68,0.4)"
                  : "rgba(255,255,255,0.08)"
              }`,
            }}
          >
            {a === "buy" ? <ShoppingCart size={14} className="inline mr-1" /> : <TrendingDown size={14} className="inline mr-1" />}
            {a.toUpperCase()}
          </button>
        ))}
      </div>

      {/* AI Recommendation */}
      {rec && analysisResult && action === "buy" && rec.shares > 0 && (
        <div
          className="rounded-lg p-3 mb-4 text-xs"
          style={{ background: "rgba(0,212,255,0.06)", border: "1px solid rgba(0,212,255,0.15)" }}
        >
          <p className="num font-bold mb-1" style={{ color: "var(--color-cyan)" }}>
            AI RECOMMENDATION
          </p>
          <p style={{ color: "var(--color-muted)" }}>
            {rec.shares} shares (${rec.value.toFixed(0)}) — {(rec.fraction * 100).toFixed(1)}% of cash
            · based on {analysisResult.final_confidence.toFixed(0)}% confidence,{" "}
            {analysisResult.final_risk} risk
          </p>
          <button
            className="mt-2 num text-xs underline"
            style={{ color: "var(--color-cyan)" }}
            onClick={() => setShares(rec.shares.toString())}
          >
            Use this
          </button>
        </div>
      )}

      {/* Shares input */}
      <div className="mb-4">
        <label className="text-xs mb-1 block" style={{ color: "var(--color-muted)" }}>
          Shares
        </label>
        <input
          type="number"
          min="1"
          value={shares}
          onChange={(e) => setShares(e.target.value)}
          placeholder="0"
          className="w-full px-3 py-2.5 rounded-lg num text-sm outline-none"
          style={{
            background: "rgba(255,255,255,0.06)",
            border: "1px solid rgba(255,255,255,0.12)",
            color: "var(--color-text)",
          }}
        />
      </div>

      {/* Summary */}
      <div
        className="rounded-lg p-3 mb-4 grid grid-cols-2 gap-2 text-xs"
        style={{ background: "rgba(255,255,255,0.03)" }}
      >
        <div>
          <p style={{ color: "var(--color-muted)" }}>Price</p>
          <p className="num font-bold">${currentPrice.toFixed(2)}</p>
        </div>
        <div>
          <p style={{ color: "var(--color-muted)" }}>Total</p>
          <p className="num font-bold">${total.toFixed(2)}</p>
        </div>
        <div>
          <p style={{ color: "var(--color-muted)" }}>Available Cash</p>
          <p className="num font-bold">${cash.toLocaleString("en-US", { maximumFractionDigits: 0 })}</p>
        </div>
        {holding && (
          <div>
            <p style={{ color: "var(--color-muted)" }}>Holdings</p>
            <p className="num font-bold">{holding.shares} shares</p>
          </div>
        )}
      </div>

      {error && (
        <div
          className="flex items-center gap-2 p-2 rounded mb-3 text-xs"
          style={{ background: "rgba(239,68,68,0.1)", color: "var(--color-negative)" }}
        >
          <AlertTriangle size={12} /> {error}
        </div>
      )}

      {success && (
        <div
          className="p-2 rounded mb-3 text-xs num"
          style={{ background: "rgba(16,185,129,0.1)", color: "var(--color-positive)" }}
        >
          ✓ {success}
        </div>
      )}

      <button
        onClick={handleTrade}
        disabled={submitting || !shares || parseFloat(shares) <= 0}
        className="w-full py-3 rounded-lg num font-bold text-sm transition-all disabled:opacity-40"
        style={{
          background:
            action === "buy" ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)",
          color: action === "buy" ? "var(--color-positive)" : "var(--color-negative)",
          border: `1px solid ${action === "buy" ? "rgba(16,185,129,0.4)" : "rgba(239,68,68,0.4)"}`,
        }}
      >
        {submitting ? "EXECUTING..." : `${action.toUpperCase()} ${shares || "0"} × ${ticker}`}
      </button>
    </div>
  );
}
