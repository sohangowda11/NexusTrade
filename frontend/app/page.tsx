"use client";
import { useState, useEffect, Suspense, lazy } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTradingStore } from "@/store/tradingStore";
import { fetchCandles, fetchQuote, runAnalysis } from "@/lib/api";

import WatchlistStrip from "@/components/market/WatchlistStrip";
import AIVotingPanel from "@/components/analysis/AIVotingPanel";
import TradeExecutor from "@/components/analysis/TradeExecutor";
import PortfolioCard from "@/components/portfolio/PortfolioCard";
import HoldingsTable from "@/components/portfolio/HoldingsTable";
import TradeHistory from "@/components/portfolio/TradeHistory";

// Lazy-load heavy Three.js + chart components
const ParticleField = lazy(() => import("@/components/three/ParticleField"));
const StockChart = lazy(() => import("@/components/charts/StockChart"));

function StatBadge({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div
      className="glass-card px-4 py-3 flex flex-col gap-0.5"
      style={{ borderColor: color ? color + "33" : undefined }}
    >
      <span className="text-xs" style={{ color: "var(--color-muted)" }}>
        {label}
      </span>
      <span className="num font-bold text-lg" style={{ color: color ?? "var(--color-text)" }}>
        {value}
      </span>
    </div>
  );
}

export default function DashboardPage() {
  const {
    selectedTicker,
    isAnalyzing,
    setIsAnalyzing,
    setAnalysisResult,
    analysisResults,
    cash,
    holdings,
    trades,
    updateCurrentPrice,
  } = useTradingStore();

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  // Live quote for selected ticker
  const { data: quote } = useQuery({
    queryKey: ["quote", selectedTicker],
    queryFn: () => fetchQuote(selectedTicker),
    refetchInterval: 20_000,
    staleTime: 10_000,
    enabled: mounted,
  });

  // Update holding current price when quote refreshes
  useEffect(() => {
    if (quote?.current_price) {
      updateCurrentPrice(selectedTicker, quote.current_price);
    }
  }, [quote, selectedTicker, updateCurrentPrice]);

  // Candle data
  const { data: candles = [] } = useQuery({
    queryKey: ["candles", selectedTicker],
    queryFn: () => fetchCandles(selectedTicker, 60),
    staleTime: 60_000,
    enabled: mounted,
  });

  const currentPrice = quote?.current_price ?? 0;
  const changePct = quote?.change_pct ?? 0;
  const isUp = changePct >= 0;

  // Portfolio stats
  const holdingsValue = holdings.reduce((s, h) => s + h.shares * h.currentPrice, 0);
  const totalValue = cash + holdingsValue;
  const pnl = totalValue - 100000;
  const pnlPct = (pnl / 100000) * 100;
  const sells = trades.filter((t) => t.action === "sell");
  const winRate =
    sells.length > 0
      ? ((sells.filter((t) => (t.pnl ?? 0) > 0).length / sells.length) * 100).toFixed(0)
      : "—";

  const currentAnalysis = analysisResults[selectedTicker] ?? null;

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const result = await runAnalysis(selectedTicker);
      // Map snake_case backend keys to our store shape
      setAnalysisResult(selectedTicker, {
        ticker: result.ticker,
        round1_votes: result.round1_votes ?? [],
        round2_votes: result.round2_votes ?? [],
        final_direction: result.final_direction,
        final_confidence: result.final_confidence,
        final_risk: result.final_risk,
        consensus_score: result.consensus_score,
        aggregated_reasoning: result.aggregated_reasoning,
        price_at_analysis: result.price_at_analysis,
      });
    } catch (e) {
      console.error("Analysis failed:", e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (!mounted) return null;

  return (
    <div
      className="min-h-screen bg-grid"
      style={{ background: "var(--bg-primary)" }}
    >
      {/* ── Hero ──────────────────────────────────────────────────── */}
      <div
        className="relative overflow-hidden px-6 py-10"
        style={{
          background: "linear-gradient(180deg, rgba(0,212,255,0.04) 0%, transparent 100%)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <Suspense fallback={null}>
          <ParticleField className="opacity-40" />
        </Suspense>

        <div className="relative z-10 max-w-7xl mx-auto">
          <div className="mb-6">
            <p className="num text-xs mb-2 tracking-widest" style={{ color: "var(--color-cyan)" }}>
              ◆ NEXUSTRADE
            </p>
            <h1
              className="text-3xl md:text-4xl font-bold mb-2"
              style={{
                background: "linear-gradient(135deg, #fff 60%, var(--color-cyan))",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              AI-POWERED MARKET INTELLIGENCE
            </h1>
            <p className="text-sm" style={{ color: "var(--color-muted)" }}>
              4 AI models vote · discuss · reach consensus · you trade with $100K virtual capital
            </p>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatBadge
              label="Portfolio Value"
              value={`$${totalValue.toLocaleString("en-US", { maximumFractionDigits: 0 })}`}
              color="var(--color-cyan)"
            />
            <StatBadge
              label="All-Time P&L"
              value={`${pnl >= 0 ? "+" : ""}$${Math.abs(pnl).toFixed(0)} (${pnlPct.toFixed(1)}%)`}
              color={pnl >= 0 ? "var(--color-positive)" : "var(--color-negative)"}
            />
            <StatBadge label="Total Trades" value={trades.length.toString()} />
            <StatBadge label="Win Rate" value={winRate === "—" ? "—" : `${winRate}%`} />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">
        {/* ── Watchlist Strip ────────────────────────────────────── */}
        <WatchlistStrip />

        {/* ── Selected Ticker Header ─────────────────────────────── */}
        <div className="flex items-end gap-4">
          <h2
            className="text-3xl num font-bold"
            style={{ color: "var(--color-text)" }}
          >
            {selectedTicker}
          </h2>
          {currentPrice > 0 && (
            <>
              <span className="text-2xl num font-bold" style={{ color: "var(--color-cyan)" }}>
                ${currentPrice.toFixed(2)}
              </span>
              <span
                className="num text-sm font-bold"
                style={{ color: isUp ? "var(--color-positive)" : "var(--color-negative)" }}
              >
                {isUp ? "+" : ""}{changePct.toFixed(2)}%
              </span>
            </>
          )}
        </div>

        {/* ── Main Grid: Chart + AI Panel + Trade ────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart — takes 2 cols */}
          <div className="lg:col-span-2 space-y-4">
            <Suspense fallback={<div className="skeleton h-80 rounded-xl" />}>
              <StockChart ticker={selectedTicker} candles={candles} />
            </Suspense>
            <TradeExecutor
              ticker={selectedTicker}
              currentPrice={currentPrice}
              analysisResult={currentAnalysis}
            />
          </div>

          {/* AI Panel */}
          <div className="lg:col-span-1">
            <AIVotingPanel
              ticker={selectedTicker}
              isLoading={isAnalyzing}
              result={currentAnalysis}
              onAnalyze={handleAnalyze}
            />
          </div>
        </div>

        {/* ── Portfolio Section ──────────────────────────────────── */}
        <div
          id="portfolio"
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="md:col-span-1">
            <PortfolioCard />
          </div>
          <div className="md:col-span-2">
            <HoldingsTable />
          </div>
        </div>

        {/* ── Trade History ──────────────────────────────────────── */}
        <div id="history">
          <TradeHistory />
        </div>

        {/* Footer */}
        <div className="py-8 text-center">
          <p className="text-xs" style={{ color: "var(--color-muted)" }}>
            NexusTrade is a paper trading simulator. Not financial advice. AI predictions are not guaranteed.
          </p>
        </div>
      </div>
    </div>
  );
}
