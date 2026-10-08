"use client";
import { useTradingStore } from "@/store/tradingStore";
import { useState } from "react";

const PAGE_SIZE = 10;

export default function TradeHistory() {
  const { trades } = useTradingStore();
  const [page, setPage] = useState(0);
  const totalPages = Math.ceil(trades.length / PAGE_SIZE);
  const visible = trades.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  if (!trades.length) {
    return (
      <div className="glass-card p-8 text-center">
        <p className="num text-sm" style={{ color: "var(--color-muted)" }}>
          No trades yet.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      <div
        className="px-5 py-3 border-b flex items-center justify-between"
        style={{ borderColor: "var(--color-border)" }}
      >
        <h3 className="num font-bold text-sm" style={{ color: "var(--color-cyan)" }}>
          TRADE HISTORY
        </h3>
        <span className="num text-xs" style={{ color: "var(--color-muted)" }}>
          {trades.length} trades
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr
              className="text-xs num"
              style={{ color: "var(--color-muted)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}
            >
              {["DATE", "TICKER", "ACTION", "SHARES", "PRICE", "TOTAL", "P&L"].map((h) => (
                <th key={h} className="px-4 py-2.5 text-left font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((t) => {
              const hasPN = t.pnl !== undefined && t.pnl !== null;
              const isPos = (t.pnl ?? 0) >= 0;
              return (
                <tr
                  key={t.id}
                  className="text-sm transition-colors"
                  style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}
                  onMouseEnter={(e) =>
                    ((e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.03)")
                  }
                  onMouseLeave={(e) =>
                    ((e.currentTarget as HTMLElement).style.background = "transparent")
                  }
                >
                  <td className="px-4 py-3 num text-xs" style={{ color: "var(--color-muted)" }}>
                    {new Date(t.timestamp).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 num font-bold" style={{ color: "var(--color-cyan)" }}>
                    {t.ticker}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className="num text-xs px-2 py-0.5 rounded font-bold"
                      style={{
                        background:
                          t.action === "buy" ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
                        color:
                          t.action === "buy" ? "var(--color-positive)" : "var(--color-negative)",
                      }}
                    >
                      {t.action.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3 num">{t.shares}</td>
                  <td className="px-4 py-3 num">${t.price.toFixed(2)}</td>
                  <td className="px-4 py-3 num">${t.total.toFixed(2)}</td>
                  <td
                    className="px-4 py-3 num"
                    style={{
                      color: !hasPN
                        ? "var(--color-muted)"
                        : isPos
                        ? "var(--color-positive)"
                        : "var(--color-negative)",
                    }}
                  >
                    {!hasPN
                      ? "—"
                      : `${isPos ? "+" : ""}$${Math.abs(t.pnl!).toFixed(2)}`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div
          className="flex items-center justify-between px-5 py-3 border-t"
          style={{ borderColor: "var(--color-border)" }}
        >
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="num text-xs px-3 py-1 rounded disabled:opacity-30"
            style={{ color: "var(--color-muted)", border: "1px solid rgba(255,255,255,0.1)" }}
          >
            ← Prev
          </button>
          <span className="num text-xs" style={{ color: "var(--color-muted)" }}>
            {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            className="num text-xs px-3 py-1 rounded disabled:opacity-30"
            style={{ color: "var(--color-muted)", border: "1px solid rgba(255,255,255,0.1)" }}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
