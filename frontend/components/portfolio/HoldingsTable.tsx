"use client";
import { useTradingStore } from "@/store/tradingStore";
import { TrendingUp, TrendingDown } from "lucide-react";

export default function HoldingsTable() {
  const { holdings, setSelectedTicker } = useTradingStore();

  if (!holdings.length) {
    return (
      <div className="glass-card p-8 text-center">
        <p className="num text-sm" style={{ color: "var(--color-muted)" }}>
          No holdings yet.
          <br />
          Analyze a stock and execute a buy to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      <div
        className="px-5 py-3 border-b"
        style={{ borderColor: "var(--color-border)" }}
      >
        <h3 className="num font-bold text-sm" style={{ color: "var(--color-cyan)" }}>
          HOLDINGS
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr
              className="text-xs num"
              style={{ color: "var(--color-muted)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}
            >
              {["TICKER", "SHARES", "AVG COST", "CURR PRICE", "VALUE", "P&L", "P&L %"].map(
                (h) => (
                  <th key={h} className="px-4 py-2.5 text-left font-medium">
                    {h}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody>
            {holdings.map((h) => {
              const value = h.shares * h.currentPrice;
              const pnl = (h.currentPrice - h.avgPrice) * h.shares;
              const pnlPct = ((h.currentPrice - h.avgPrice) / h.avgPrice) * 100;
              const isPos = pnl >= 0;
              return (
                <tr
                  key={h.ticker}
                  onClick={() => setSelectedTicker(h.ticker)}
                  className="text-sm cursor-pointer transition-colors"
                  style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}
                  onMouseEnter={(e) =>
                    ((e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.04)")
                  }
                  onMouseLeave={(e) =>
                    ((e.currentTarget as HTMLElement).style.background = "transparent")
                  }
                >
                  <td className="px-4 py-3 num font-bold" style={{ color: "var(--color-cyan)" }}>
                    {h.ticker}
                  </td>
                  <td className="px-4 py-3 num">{h.shares}</td>
                  <td className="px-4 py-3 num">${h.avgPrice.toFixed(2)}</td>
                  <td className="px-4 py-3 num">${h.currentPrice.toFixed(2)}</td>
                  <td className="px-4 py-3 num">${value.toFixed(2)}</td>
                  <td
                    className="px-4 py-3 num flex items-center gap-1 font-bold"
                    style={{ color: isPos ? "var(--color-positive)" : "var(--color-negative)" }}
                  >
                    {isPos ? <TrendingUp size={12} /> : <TrendingDown size={12} />}$
                    {Math.abs(pnl).toFixed(2)}
                  </td>
                  <td
                    className="px-4 py-3 num font-bold"
                    style={{ color: isPos ? "var(--color-positive)" : "var(--color-negative)" }}
                  >
                    {isPos ? "+" : ""}
                    {pnlPct.toFixed(2)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
