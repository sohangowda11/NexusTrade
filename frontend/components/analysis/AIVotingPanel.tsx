"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Loader2, Zap, AlertTriangle, Shield } from "lucide-react";
import type { AnalysisResult, AIVote } from "@/store/tradingStore";

const MODEL_COLORS: Record<string, string> = {
  "Claude Sonnet": "#a855f7",
  "GPT-4o":        "#22c55e",
  "Gemini 1.5 Pro":"#3b82f6",
  "DeepSeek Chat": "#f97316",
};

const RISK_CONFIG = {
  low:    { label: "LOW RISK",  color: "#10b981", Icon: Shield },
  medium: { label: "MED RISK",  color: "#f59e0b", Icon: AlertTriangle },
  high:   { label: "HIGH RISK", color: "#ef4444", Icon: AlertTriangle },
};

function ModelCard({ vote, index }: { vote: AIVote; index: number }) {
  const color = MODEL_COLORS[vote.model_name] || "var(--color-cyan)";
  const isUp = vote.direction === "up";
  const risk = RISK_CONFIG[vote.risk_level] ?? RISK_CONFIG.medium;
  const RiskIcon = risk.Icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.35 }}
      className="glass-card p-4 relative overflow-hidden"
      style={{ borderColor: color + "22" }}
    >
      <div
        className="absolute top-0 left-0 w-0.5 h-full"
        style={{ backgroundColor: color }}
      />
      <div className="pl-3 space-y-2">
        {/* Header row */}
        <div className="flex items-center justify-between">
          <span
            className="ticker-badge text-xs px-2 py-0.5 rounded"
            style={{ background: color + "18", color }}
          >
            {vote.model_name}
          </span>
          <div
            className="flex items-center gap-1 font-bold text-sm"
            style={{ color: isUp ? "var(--color-positive)" : "var(--color-negative)" }}
          >
            {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {vote.direction.toUpperCase()}
          </div>
        </div>

        {/* Confidence bar */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span style={{ color: "var(--color-muted)" }}>Confidence</span>
            <span className="num font-bold" style={{ color: "var(--color-cyan)" }}>
              {vote.confidence}%
            </span>
          </div>
          <div
            className="h-1.5 rounded-full overflow-hidden"
            style={{ background: "rgba(255,255,255,0.08)" }}
          >
            <motion.div
              className="h-full rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${vote.confidence}%` }}
              transition={{ delay: index * 0.08 + 0.25, duration: 0.7, ease: "easeOut" }}
              style={{ background: `linear-gradient(90deg, ${color}88, ${color})` }}
            />
          </div>
        </div>

        {/* Risk */}
        <div className="flex items-center gap-1">
          <RiskIcon size={11} color={risk.color} />
          <span className="text-xs num" style={{ color: risk.color }}>
            {risk.label}
          </span>
          {vote.is_mock && (
            <span className="ml-auto text-xs" style={{ color: "var(--color-muted)" }}>
              [MOCK]
            </span>
          )}
        </div>

        {/* Reasoning */}
        <p
          className="text-xs leading-relaxed"
          style={{
            color: "var(--color-muted)",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {vote.reasoning}
        </p>
      </div>
    </motion.div>
  );
}

export default function AIVotingPanel({
  ticker,
  isLoading,
  result,
  onAnalyze,
}: {
  ticker: string;
  isLoading: boolean;
  result: AnalysisResult | null;
  onAnalyze: () => void;
}) {
  const [round, setRound] = useState<1 | 2>(2);
  const votes =
    round === 1
      ? result?.round1_votes ?? result?.round2_votes ?? []
      : result?.round2_votes ?? [];
  const isUp = result?.final_direction === "up";

  return (
    <div className="glass-card p-5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="num font-bold text-lg" style={{ color: "var(--color-cyan)" }}>
            AI COUNCIL
          </h2>
          <p className="text-xs" style={{ color: "var(--color-muted)" }}>
            Multi-model consensus
          </p>
        </div>
        <button
          onClick={onAnalyze}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg num text-sm font-bold transition-all disabled:opacity-60"
          style={{
            background: isLoading ? "rgba(0,212,255,0.06)" : "rgba(0,212,255,0.15)",
            color: "var(--color-cyan)",
            border: "1px solid var(--color-cyan)",
          }}
        >
          {isLoading ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Zap size={14} />
          )}
          {isLoading ? "ANALYZING..." : `ANALYZE ${ticker}`}
        </button>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex-1 flex flex-col items-center justify-center gap-5">
          <div
            className="w-14 h-14 rounded-full border-2 border-t-transparent animate-spin"
            style={{ borderColor: "var(--color-cyan)", borderTopColor: "transparent" }}
          />
          <p className="num text-sm animate-pulse" style={{ color: "var(--color-cyan)" }}>
            CONSULTING AI ADVISORS...
          </p>
          <div className="w-full space-y-2">
            {["Claude Sonnet", "GPT-4o", "Gemini 1.5 Pro", "DeepSeek Chat"].map((m) => (
              <div key={m} className="skeleton h-16 w-full" />
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {!isLoading && result && (
        <>
          {/* Round toggle */}
          {result.round1_votes?.length > 0 && (
            <div className="flex gap-2 mb-4">
              {([1, 2] as const).map((r) => (
                <button
                  key={r}
                  onClick={() => setRound(r)}
                  className="px-3 py-1 rounded text-xs num transition-all"
                  style={{
                    background: round === r ? "rgba(0,212,255,0.15)" : "transparent",
                    color: round === r ? "var(--color-cyan)" : "var(--color-muted)",
                    border: `1px solid ${round === r ? "var(--color-cyan)" : "rgba(255,255,255,0.1)"}`,
                  }}
                >
                  ROUND {r}
                </button>
              ))}
            </div>
          )}

          {/* Vote cards */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {votes.map((v, i) => (
              <ModelCard key={v.model_name + round} vote={v} index={i} />
            ))}
          </div>

          {/* Consensus signal */}
          <div
            className="glass-card p-4 mt-auto"
            style={{
              borderColor: isUp ? "#10b98144" : "#ef444444",
              background: isUp ? "rgba(16,185,129,0.04)" : "rgba(239,68,68,0.04)",
            }}
          >
            <p className="text-xs num mb-3" style={{ color: "var(--color-muted)" }}>
              CONSENSUS SIGNAL
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {isUp ? (
                  <TrendingUp size={36} color="var(--color-positive)" />
                ) : (
                  <TrendingDown size={36} color="var(--color-negative)" />
                )}
                <div>
                  <p
                    className="text-2xl num font-bold"
                    style={{ color: isUp ? "var(--color-positive)" : "var(--color-negative)" }}
                  >
                    {result.final_direction.toUpperCase()}
                  </p>
                  <p className="text-xs" style={{ color: "var(--color-muted)" }}>
                    {result.consensus_score.toFixed(0)}% model agreement
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-3xl num font-bold" style={{ color: "var(--color-cyan)" }}>
                  {result.final_confidence.toFixed(0)}%
                </p>
                <p className="text-xs" style={{ color: "var(--color-muted)" }}>
                  confidence
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Empty state */}
      {!isLoading && !result && (
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-3 py-12">
          <Zap size={44} style={{ color: "var(--color-cyan)", opacity: 0.25 }} />
          <p className="num text-sm" style={{ color: "var(--color-muted)" }}>
            Click ANALYZE to consult
            <br />4 AI models simultaneously
          </p>
        </div>
      )}
    </div>
  );
}
