import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "var(--color-paper)",
        "paper-2": "var(--color-paper-2)",
        "paper-3": "var(--color-paper-3)",
        "paper-hover": "var(--color-paper-hover)",
        ink: "var(--color-ink)",
        "ink-2": "var(--color-ink-2)",
        muted: "var(--color-muted)",
        rule: "var(--color-rule)",
        "rule-subtle": "var(--color-rule-subtle)",
        "ink-rule": "var(--color-ink-rule)",
        accent: "var(--color-accent)",
        "accent-hover": "var(--color-accent-hover)",
        "accent-subtle": "var(--color-accent-subtle)",
        "accent-2": "var(--color-accent-2)",
        "accent-ink": "var(--color-accent-ink)",
        "cloud-llm": "var(--color-cloud-llm)",
        "cloud-llm-bg": "var(--color-cloud-llm-bg)",
        focus: "var(--color-focus)",
        success: "var(--color-success)",
        "success-bg": "var(--color-success-bg)",
        "success-ink": "var(--color-success-ink)",
        warning: "var(--color-warning)",
        "warning-bg": "var(--color-warning-bg)",
        "warning-ink": "var(--color-warning-ink)",
        error: "var(--color-error)",
        "error-bg": "var(--color-error-bg)",
        "error-ink": "var(--color-error-ink)",
      },
      fontFamily: {
        sans: ["var(--font-body)", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        display: ["var(--font-display)", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        subtle: "var(--shadow-subtle)",
        card: "var(--shadow-card)",
        hover: "var(--shadow-hover)",
        neon: "0 0 25px rgba(99, 102, 241, 0.25)",
        "neon-cyan": "0 0 25px rgba(6, 182, 212, 0.25)",
        "neon-green": "0 0 25px rgba(16, 185, 129, 0.25)",
      },
      borderWidth: {
        hair: "var(--rule-hair)",
        bar: "var(--rule-bar)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        card: "var(--radius-card)",
        lg: "var(--radius-lg)",
        pill: "var(--radius-pill)",
      },
      animation: {
        "border-beam": "border-beam var(--duration) linear infinite",
        "shimmer-slide": "shimmer-slide var(--speed) ease-in-out infinite alternate",
        "spin-around": "spin-around var(--speed) infinite linear",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "beam-travel": "beam-travel 3s linear infinite",
      },
      keyframes: {
        "border-beam": {
          "100%": {
            "offset-distance": "100%",
          },
        },
        "shimmer-slide": {
          to: {
            transform: "translate(calc(100cqw - 100%), 0)",
          },
        },
        "spin-around": {
          "0%": {
            transform: "translateY(0%) rotate(0deg)",
          },
          "100%": {
            transform: "translateY(0%) rotate(360deg)",
          },
        },
        "beam-travel": {
          "0%": { strokeDashoffset: "100%" },
          "100%": { strokeDashoffset: "0%" },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
