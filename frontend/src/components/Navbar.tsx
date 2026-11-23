import React from "react";
import { Cpu, GitPullRequest, ExternalLink, Zap, Terminal, BookOpen, Sun, Moon } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { PageId } from "./Sidebar";

interface NavbarProps {
  systemHealth?: {
    status: string;
    has_github_token: boolean;
    slm_model: string;
    llm_provider: string;
  };
  onNavigate?: (page: PageId) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ systemHealth, onNavigate }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="w-full bg-paper-3/90 backdrop-blur-2xl border-b border-rule sticky top-0 z-40 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        {/* Brand / Logo */}
        <div
          className="flex items-center gap-3 cursor-pointer"
          onClick={() => onNavigate && onNavigate("overview")}
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-cyan-400 text-white flex items-center justify-center font-bold shadow-sm">
            <Zap className="w-4 h-4 fill-current" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base tracking-tight text-ink font-display">
              ReviewPilot
            </span>
            <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-accent-subtle text-accent border border-accent/25">
              Motion AI v2.0
            </span>
          </div>
        </div>

        {/* Live System Chips & Actions */}
        <div className="flex items-center gap-2.5 sm:gap-3.5 text-xs">
          {/* SLM Model Chip */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-paper-2 border border-rule text-ink-2">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-success shadow-sm" />
            </span>
            <span className="font-mono text-[11px]">
              SLM: {systemHealth?.slm_model || "qwen2.5-coder:1.5b"}
            </span>
          </div>

          {/* Engine Mode */}
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-paper-2 border border-rule text-ink-2">
            <Cpu className="w-3.5 h-3.5 text-accent" />
            <span className="font-mono text-[11px]">Hybrid Router</span>
          </div>

          {/* Manual Link Button */}
          {onNavigate && (
            <button
              onClick={() => onNavigate("manual")}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-paper-2 hover:bg-paper-hover border border-rule text-ink-2 hover:text-ink text-xs font-mono font-medium transition-all"
              title="Open System Manual & Guide"
            >
              <BookOpen className="w-3.5 h-3.5 text-accent" />
              <span className="hidden sm:inline">Manual</span>
            </button>
          )}

          {/* Theme Switcher Toggle */}
          <button
            onClick={toggleTheme}
            className="p-1.5 rounded-lg bg-paper-2 hover:bg-paper-hover border border-rule text-ink-2 hover:text-ink transition-colors"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4 text-warning" />
            ) : (
              <Moon className="w-4 h-4 text-accent" />
            )}
          </button>

          {/* OpenAPI Docs Link */}
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-accent text-accent-ink hover:opacity-90 text-xs font-mono font-medium transition-all shadow-sm"
          >
            <Terminal className="w-3 h-3" />
            <span>API Docs</span>
            <ExternalLink className="w-2.5 h-2.5 opacity-60" />
          </a>
        </div>
      </div>
    </header>
  );
};
