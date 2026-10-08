"use client";
import Link from "next/link";
import { useTradingStore } from "@/store/tradingStore";
import { Activity, BarChart2, Clock, TrendingUp, Zap } from "lucide-react";

export default function Navbar() {
  const { cash, holdings } = useTradingStore();
  const holdingsValue = holdings.reduce((s, h) => s + h.shares * h.currentPrice, 0);
  const totalValue = cash + holdingsValue;

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-3"
      style={{
        background: "rgba(10, 14, 26, 0.85)",
        backdropFilter: "blur(24px)",
        borderBottom: "1px solid rgba(0, 212, 255, 0.12)",
      }}
    >
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #00d4ff22, #7c3aed22)", border: "1px solid rgba(0,212,255,0.3)" }}
          >
            <Zap size={16} style={{ color: "var(--color-cyan)" }} />
          </div>
          <span
            className="text-lg font-bold tracking-widest"
            style={{ fontFamily: "var(--font-mono)", color: "var(--color-cyan)" }}
          >
            NEXUS<span style={{ color: "var(--color-text)" }}>TRADE</span>
          </span>
        </div>
        <div className="flex items-center gap-1 ml-4">
          <div className="pulse-dot" />
          <span className="text-xs font-mono" style={{ color: "var(--color-positive)" }}>
            LIVE
          </span>
        </div>
      </div>

      {/* Nav Links */}
      <div className="hidden md:flex items-center gap-1">
        {[
          { label: "Dashboard", href: "/", icon: BarChart2 },
          { label: "Portfolio", href: "#portfolio", icon: TrendingUp },
          { label: "Analysis", href: "#analysis", icon: Activity },
          { label: "History", href: "#history", icon: Clock },
        ].map(({ label, href, icon: Icon }) => (
          <Link
            key={label}
            href={href}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors"
            style={{ color: "var(--color-muted)" }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.color = "var(--color-text)";
              (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.05)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.color = "var(--color-muted)";
              (e.currentTarget as HTMLElement).style.background = "transparent";
            }}
          >
            <Icon size={14} />
            {label}
          </Link>
        ))}
      </div>

      {/* Wallet */}
      <div
        className="glass-card px-4 py-2 flex items-center gap-2"
        style={{ borderColor: "rgba(0,212,255,0.2)" }}
      >
        <span className="text-xs" style={{ color: "var(--color-muted)" }}>Portfolio</span>
        <span
          className="num font-bold text-sm"
          style={{ color: "var(--color-cyan)" }}
        >
          ${totalValue.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      </div>
    </nav>
  );
}
