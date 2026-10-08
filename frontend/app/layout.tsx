import type { Metadata } from "next";
import "./globals.css";
import Providers from "@/components/layout/Providers";
import Navbar from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "NexusTrade — AI-Powered Stock Simulator",
  description: "Multi-model AI stock trading simulator with paper money",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ background: "var(--bg-primary)", minHeight: "100vh" }}>
        <Providers>
          <Navbar />
          <main style={{ paddingTop: "64px" }}>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
