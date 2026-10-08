"use client";
import { useQuery } from "@tanstack/react-query";
import { fetchBatchQuotes } from "@/lib/api";
import { useTradingStore } from "@/store/tradingStore";
import { TrendingUp, TrendingDown, Plus } from "lucide-react";
import { useState } from "react";

export default function WatchlistStrip() {
  const { watchlist, selectedTicker, setSelectedTicker } = useTradingStore();
  const [adding, setAdding] = useState(false);
  const [newTicker, setNewTicker] = useState("");

  const { data: quotes } = useQuery({
    queryKey: ["batch-quotes", watchlist],
    queryFn: () => fetchBatchQuotes(watchlist),
    refetchInterval: 30_000,
    staleTime: 10_000,
  });

  const handleAdd = () => {
    const t = newTicker.trim().toUpperCase();
    if (t && !watchlist.includes(t)) {
      useTradingStore.setState((s) => ({ watchlist: [...s.watchlist, t] }));
    }
    setNewTicker("");
    setAdding(false);
  };

  return (
    <div className="flex items-center gap-2 overflow-x-auto py-1 scrollbar-hide">
      {watchlist.map((ticker) => {
        const q = quotes?.[ticker];
        const pct = q?.change_pct ?? 0;
        const isUp = pct >= 0;
        const isSelected = ticker === selectedTicker;

        return (
          <button
            key={ticker}
            onClick={() => setSelectedTicker(ticker)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg whitespace-nowrap flex-shrink-0 transition-all"
            style={{
              background: isSelected ? "rgba(0,212,255,0.12)" : "rgba(255,255,255,0.04)",
              border: `1px solid ${isSelected ? "var(--color-cyan)" : "rgba(255,255,255,0.08)"}`,
              color: isSelected ? "var(--color-cyan)" : "var(--color-text)",
            }}
          >
            <span className="ticker-badge font-bold">{ticker}</span>
            {q ? (
              <>
                <span className="num text-xs">${q.current_price?.toFixed(2)}</span>
                <span
                  className="flex items-center gap-0.5 num text-xs font-bold"
                  style={{ color: isUp ? "var(--color-positive)" : "var(--color-negative)" }}
                >
                  {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                  {Math.abs(pct).toFixed(2)}%
                </span>
              </>
            ) : (
              <span className="skeleton h-3 w-12" />
            )}
          </button>
        );
      })}

      {/* Add ticker */}
      {adding ? (
        <div className="flex items-center gap-1 flex-shrink-0">
          <input
            autoFocus
            value={newTicker}
            onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
            onKeyDown={(e) => { if (e.key === "Enter") handleAdd(); if (e.key === "Escape") setAdding(false); }}
            placeholder="TICKER"
            maxLength={6}
            className="w-20 px-2 py-1.5 rounded num text-xs outline-none"
            style={{
              background: "rgba(0,212,255,0.08)",
              border: "1px solid var(--color-cyan)",
              color: "var(--color-cyan)",
            }}
          />
          <button
            onClick={handleAdd}
            className="px-2 py-1.5 rounded text-xs num"
            style={{ background: "rgba(0,212,255,0.15)", color: "var(--color-cyan)" }}
          >
            Add
          </button>
        </div>
      ) : (
        <button
          onClick={() => setAdding(true)}
          className="flex items-center gap-1 px-3 py-2 rounded-lg flex-shrink-0 text-xs transition-all"
          style={{ border: "1px dashed rgba(255,255,255,0.15)", color: "var(--color-muted)" }}
        >
          <Plus size={12} /> Add
        </button>
      )}
    </div>
  );
}
