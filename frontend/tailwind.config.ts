import type { Config } from "tailwindcss";

// Tailwind v4 uses CSS-first configuration (@theme in globals.css).
// This file is kept for content detection only.
const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./store/**/*.{js,ts,jsx,tsx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
};

export default config;
