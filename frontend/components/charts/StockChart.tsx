"use client";
import { useEffect, useRef } from "react";

export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function StockChart({
  ticker,
  candles,
}: {
  ticker: string;
  candles: Candle[];
}) {
  const chartRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<{ remove: () => void } | null>(null);

  useEffect(() => {
    if (!chartRef.current || !candles.length) return;

    const init = async () => {
      const lc = await import("lightweight-charts");

      // Clean up previous instance
      if (instanceRef.current) {
        instanceRef.current.remove();
        instanceRef.current = null;
      }

      const chart = lc.createChart(chartRef.current!, {
        width: chartRef.current!.clientWidth,
        height: 320,
        layout: {
          background: { color: "transparent" } as { color: string },
          textColor: "#64748b",
        },
        grid: {
          vertLines: { color: "rgba(255,255,255,0.04)" },
          horzLines: { color: "rgba(255,255,255,0.04)" },
        },
        crosshair: { mode: 1 },
        rightPriceScale: { borderColor: "rgba(255,255,255,0.08)" },
        timeScale: { borderColor: "rgba(255,255,255,0.08)", timeVisible: false },
      });

      instanceRef.current = chart;

      // Candlestick series — v5 uses chart.addSeries(SeriesType, options)
      const candleSeries = chart.addSeries(lc.CandlestickSeries, {
        upColor: "#10b981",
        downColor: "#ef4444",
        borderUpColor: "#10b981",
        borderDownColor: "#ef4444",
        wickUpColor: "#10b981",
        wickDownColor: "#ef4444",
      });

      const sorted = [...candles].sort((a, b) => a.time - b.time);
      candleSeries.setData(
        sorted.map((c) => ({
          time: c.time as lc.UTCTimestamp,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
        }))
      );

      // SMA 20 line
      if (sorted.length >= 20) {
        const sma20 = chart.addSeries(lc.LineSeries, {
          color: "#00d4ff",
          lineWidth: 1 as lc.LineWidth,
          priceLineVisible: false,
          lastValueVisible: false,
        });
        sma20.setData(
          sorted.slice(19).map((_, i) => ({
            time: sorted[i + 19].time as lc.UTCTimestamp,
            value:
              sorted.slice(i, i + 20).reduce((s, c) => s + c.close, 0) / 20,
          }))
        );
      }

      chart.timeScale().fitContent();

      const onResize = () => {
        if (chartRef.current && instanceRef.current) {
          (instanceRef.current as ReturnType<typeof lc.createChart>).applyOptions({
            width: chartRef.current.clientWidth,
          });
        }
      };
      window.addEventListener("resize", onResize);

      return () => {
        window.removeEventListener("resize", onResize);
      };
    };

    let cleanup: (() => void) | undefined;
    init().then((fn) => {
      cleanup = fn;
    });

    return () => {
      cleanup?.();
      if (instanceRef.current) {
        instanceRef.current.remove();
        instanceRef.current = null;
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [candles, ticker]);

  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="num font-bold" style={{ color: "var(--color-cyan)" }}>
          {ticker} — PRICE CHART
        </h3>
        <div
          className="flex items-center gap-3 text-xs num"
          style={{ color: "var(--color-muted)" }}
        >
          <span className="flex items-center gap-1">
            <span
              className="inline-block w-3"
              style={{ height: "2px", background: "var(--color-cyan)" }}
            />
            SMA 20
          </span>
          <span>60D · 1D candles</span>
        </div>
      </div>
      {candles.length === 0 ? (
        <div className="skeleton rounded-lg" style={{ height: "320px" }} />
      ) : (
        <div ref={chartRef} />
      )}
    </div>
  );
}
