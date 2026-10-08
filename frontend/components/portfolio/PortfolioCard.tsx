"use client";
import { useTradingStore } from "@/store/tradingStore";
import { TrendingUp, TrendingDown, DollarSign, Plus, Minus } from "lucide-react";
import { useState } from "react";
import { adjustFunds } from "@/lib/api";

export default function PortfolioCard() {
  const { cash, holdings, addFunds, withdrawFunds } = useTradingStore();
  const holdingsValue = holdings.reduce((s, h) => s + h.shares * h.currentPrice, 0);
  const totalValue = cash + holdingsValue;
  const pnl = totalValue - 100000;
  const pnlPct = (pnl / 100000) * 100;
  const isPos = pnl >= 0;

  const [amount, setAmount] = useState("");
  const [mode, setMode] = useState<"add" | "withdraw" | null>(null);

  const handleAdjust = async () => {
    const val = parseFloat(amount);
    if (!val || val <= 0) return;
    try {
      await adjustFunds(val, mode!);
    } catch { /* API may not be running, use local store */ }
    if (mode === "add") addFunds(val);
    else withdrawFunds(val);
    setAmount("");
    setMode(null);
  };

  return (
    <div className="glass-card p-5 glow-cyan">
      {/* Value */}
      <p className="text-xs num mb-1" style={{ color: "var(--color-muted)" }}>
        TOTAL PORTFOLIO VALUE
      </p>
      <p
        className="text-4xl num font-bold mb-1 animate-count"
        style={{ color: "var(--color-cyan)" }}
      >
        ${totalValue.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </p>

      {/* P&L */}
      <div className="flex items-center gap-2 mb-5">
        {isPos ? (
          <TrendingUp size={15} color="var(--color-positive)" />
        ) : (
          <TrendingDown size={15} color="var(--color-negative)" />
        )}
        <span
          className="num text-sm font-bold"
          style={{ color: isPos ? "var(--color-positive)" : "var(--color-negative)" }}
        >
          {isPos ? "+" : ""}
          {pnl.toLocaleString("en-US", { minimumFractionDigits: 2 })} (
          {isPos ? "+" : ""}
          {pnlPct.toFixed(2)}%)
        </span>
        <span className="text-xs" style={{ color: "var(--color-muted)" }}>
          all time
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="rounded-lg p-3" style={{ background: "rgba(255,255,255,0.04)" }}>
          <p className="text-xs mb-0.5" style={{ color: "var(--color-muted)" }}>Cash</p>
          <p className="num font-bold">
            ${cash.toLocaleString("en-US", { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="rounded-lg p-3" style={{ background: "rgba(255,255,255,0.04)" }}>
          <p className="text-xs mb-0.5" style={{ color: "var(--color-muted)" }}>Positions</p>
          <p className="num font-bold">{holdings.length} stocks</p>
        </div>
        <div className="rounded-lg p-3" style={{ background: "rgba(255,255,255,0.04)" }}>
          <p className="text-xs mb-0.5" style={{ color: "var(--color-muted)" }}>Invested</p>
          <p className="num font-bold">
            ${holdingsValue.toLocaleString("en-US", { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="rounded-lg p-3" style={{ background: "rgba(255,255,255,0.04)" }}>
          <p className="text-xs mb-0.5" style={{ color: "var(--color-muted)" }}>Return</p>
          <p
            className="num font-bold"
            style={{ color: isPos ? "var(--color-positive)" : "var(--color-negative)" }}
          >
            {isPos ? "+" : ""}
            {pnlPct.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Add / withdraw funds */}
      <div className="flex gap-2">
        <button
          onClick={() => setMode(mode === "add" ? null : "add")}
          className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg text-xs num transition-all"
          style={{
            background: mode === "add" ? "rgba(16,185,129,0.2)" : "rgba(16,185,129,0.08)",
            color: "var(--color-positive)",
            border: "1px solid rgba(16,185,129,0.3)",
          }}
        >
          <Plus size={12} /> Add Funds
        </button>
        <button
          onClick={() => setMode(mode === "withdraw" ? null : "withdraw")}
          className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg text-xs num transition-all"
          style={{
            background: mode === "withdraw" ? "rgba(239,68,68,0.2)" : "rgba(239,68,68,0.08)",
            color: "var(--color-negative)",
            border: "1px solid rgba(239,68,68,0.3)",
          }}
        >
          <Minus size={12} /> Withdraw
        </button>
      </div>

      {mode && (
        <div className="mt-3 flex gap-2">
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAdjust()}
            placeholder="Amount (USD)"
            className="flex-1 px-3 py-2 rounded-lg num text-sm outline-none"
            style={{
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.12)",
              color: "var(--color-text)",
            }}
          />
          <button
            onClick={handleAdjust}
            className="px-4 py-2 rounded-lg num text-sm font-bold"
            style={{
              background: mode === "add" ? "rgba(16,185,129,0.2)" : "rgba(239,68,68,0.2)",
              color: mode === "add" ? "var(--color-positive)" : "var(--color-negative)",
            }}
          >
            OK
          </button>
        </div>
      )}
    </div>
  );
}
