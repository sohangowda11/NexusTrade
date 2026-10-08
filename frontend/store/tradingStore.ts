"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Holding {
  ticker: string;
  shares: number;
  avgPrice: number;
  currentPrice: number;
}

export interface Trade {
  id: string;
  ticker: string;
  action: "buy" | "sell";
  shares: number;
  price: number;
  total: number;
  timestamp: string;
  pnl?: number;
}

export interface AIVote {
  model_name: string;
  direction: "up" | "down";
  confidence: number;
  risk_level: "low" | "medium" | "high";
  reasoning: string;
  round?: number;
  is_mock?: boolean;
}

export interface AnalysisResult {
  ticker: string;
  round1_votes: AIVote[];
  round2_votes: AIVote[];
  final_direction: "up" | "down" | "uncertain";
  final_confidence: number;
  final_risk: "low" | "medium" | "high";
  consensus_score: number;
  aggregated_reasoning: string;
  price_at_analysis?: number;
}

interface TradingState {
  cash: number;
  holdings: Holding[];
  trades: Trade[];
  watchlist: string[];
  selectedTicker: string;
  analysisResults: Record<string, AnalysisResult>;
  isAnalyzing: boolean;

  // Actions
  addFunds: (amount: number) => void;
  withdrawFunds: (amount: number) => void;
  setSelectedTicker: (ticker: string) => void;
  setAnalysisResult: (ticker: string, result: AnalysisResult) => void;
  setIsAnalyzing: (val: boolean) => void;
  addTrade: (trade: Trade) => void;
  updateHolding: (ticker: string, shares: number, price: number, action: "buy" | "sell") => void;
  updateCurrentPrice: (ticker: string, price: number) => void;
}

export const useTradingStore = create<TradingState>()(
  persist(
    (set) => ({
      cash: 100000,
      holdings: [],
      trades: [],
      watchlist: ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"],
      selectedTicker: "AAPL",
      analysisResults: {},
      isAnalyzing: false,

      addFunds: (amount) => set((s) => ({ cash: s.cash + amount })),
      withdrawFunds: (amount) =>
        set((s) => ({ cash: Math.max(0, s.cash - amount) })),
      setSelectedTicker: (ticker) => set({ selectedTicker: ticker }),
      setAnalysisResult: (ticker, result) =>
        set((s) => ({ analysisResults: { ...s.analysisResults, [ticker]: result } })),
      setIsAnalyzing: (val) => set({ isAnalyzing: val }),
      addTrade: (trade) => set((s) => ({ trades: [trade, ...s.trades].slice(0, 200) })),

      updateHolding: (ticker, shares, price, action) =>
        set((s) => {
          const upper = ticker.toUpperCase();
          if (action === "buy") {
            const existing = s.holdings.find((h) => h.ticker === upper);
            if (existing) {
              const newShares = existing.shares + shares;
              return {
                cash: s.cash - shares * price,
                holdings: s.holdings.map((h) =>
                  h.ticker === upper
                    ? { ...h, shares: newShares, avgPrice: (h.avgPrice * h.shares + price * shares) / newShares, currentPrice: price }
                    : h
                ),
              };
            }
            return {
              cash: s.cash - shares * price,
              holdings: [...s.holdings, { ticker: upper, shares, avgPrice: price, currentPrice: price }],
            };
          } else {
            return {
              cash: s.cash + shares * price,
              holdings: s.holdings
                .map((h) => h.ticker === upper ? { ...h, shares: h.shares - shares, currentPrice: price } : h)
                .filter((h) => h.shares > 0.0001),
            };
          }
        }),

      updateCurrentPrice: (ticker, price) =>
        set((s) => ({
          holdings: s.holdings.map((h) =>
            h.ticker === ticker.toUpperCase() ? { ...h, currentPrice: price } : h
          ),
        })),
    }),
    { name: "nexustrade-v1" }
  )
);
