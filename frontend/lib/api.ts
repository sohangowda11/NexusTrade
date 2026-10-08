import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 60000, // AI calls can take up to 30s
});

// Market
export const fetchQuote = (ticker: string) =>
  api.get(`/api/market/quote/${ticker}`).then((r) => r.data);

export const fetchCandles = (ticker: string, days = 60) =>
  api.get(`/api/market/candles/${ticker}`, { params: { days } }).then((r) => r.data);

export const fetchNews = (ticker: string, days = 2) =>
  api.get(`/api/market/news/${ticker}`, { params: { days } }).then((r) => r.data);

export const fetchIndicators = (ticker: string) =>
  api.get(`/api/market/indicators/${ticker}`).then((r) => r.data);

export const fetchBatchQuotes = (tickers: string[]) =>
  api.get("/api/market/batch-quotes", { params: { tickers: tickers.join(",") } }).then((r) => r.data);

export const searchTickers = (q: string) =>
  api.get("/api/market/search", { params: { q } }).then((r) => r.data);

// Portfolio
export const fetchPortfolio = () =>
  api.get("/api/portfolio").then((r) => r.data);

export const adjustFunds = (amount: number, action: "add" | "withdraw") =>
  api.post("/api/portfolio/funds", { amount, action }).then((r) => r.data);

// Trades
export const executeTrade = (req: {
  ticker: string;
  action: string;
  shares: number;
  price: number;
}) => api.post("/api/trades/execute", req).then((r) => r.data);

export const fetchTradeHistory = (limit = 50, offset = 0) =>
  api.get("/api/trades/history", { params: { limit, offset } }).then((r) => r.data);

export const fetchTradePerformance = () =>
  api.get("/api/trades/performance").then((r) => r.data);

export const fetchPositionSize = (params: {
  ticker: string;
  confidence: number;
  risk_level: string;
  current_price: number;
}) => api.post("/api/trades/position-size", null, { params }).then((r) => r.data);

// Analysis
export const runAnalysis = (ticker: string) =>
  api.post("/api/analysis/run", { ticker }).then((r) => r.data);

export const fetchAnalysisHistory = (ticker: string, limit = 20) =>
  api.get(`/api/analysis/history/${ticker}`, { params: { limit } }).then((r) => r.data);

// Training
export const fetchTrainingStatus = () =>
  api.get("/api/training/status").then((r) => r.data);

export const triggerTraining = () =>
  api.post("/api/training/train").then((r) => r.data);
