import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "bg-base": "#0B1220",
        card: "#111827",
        elevated: "#161F2E",
        inset: "#0E1626",
        border: "#1E293B",
        "border-strong": "#334155",
        primary: "#3B82F6",
        "primary-hover": "#2563EB",
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        info: "#38BDF8",
        "text-primary": "#F8FAFC",
        "text-secondary": "#94A3B8",
        "text-muted": "#64748B",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;