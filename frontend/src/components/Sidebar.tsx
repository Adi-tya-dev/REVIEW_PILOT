import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  FolderGit2,
  GitPullRequest,
  SearchCode,
  Network,
  FileCheck2,
  Box,
  FileSearch,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Sun,
  Moon,
  Sparkles,
  Zap,
} from "lucide-react";
import { BorderBeam } from "./motion/BorderBeam";
import { useTheme } from "../context/ThemeContext";

export type PageId =
  | "overview"
  | "repos"
  | "pr-review"
  | "static-analysis"
  | "model-routing"
  | "test-cases"
  | "docker-results"
  | "evidence"
  | "benchmarks"
  | "manual";

interface SidebarProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
}

interface NavItem {
  id: PageId;
  label: string;
  icon: any;
  badge?: string;
  badgeColor?: "indigo" | "cyan" | "emerald";
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onSelectPage }) => {
  const [collapsed, setCollapsed] = useState<boolean>(false);
  const { theme, toggleTheme } = useTheme();

  const sections: { title: string; items: NavItem[] }[] = [
    {
      title: "Core Platform",
      items: [
        { id: "overview", label: "Overview", icon: LayoutDashboard },
        { id: "repos", label: "Repositories", icon: FolderGit2 },
        { id: "pr-review", label: "Pull Requests", icon: GitPullRequest },
        { id: "static-analysis", label: "Static Analysis", icon: SearchCode },
      ],
    },
    {
      title: "AI Engine & Evidence",
      items: [
        {
          id: "model-routing",
          label: "Model Routing",
          icon: Network,
          badge: "Hybrid",
          badgeColor: "indigo",
        },
        { id: "test-cases", label: "Generated Tests", icon: FileCheck2 },
        { id: "docker-results", label: "Docker Execution", icon: Box },
        { id: "evidence", label: "Reproducibility", icon: FileSearch },
        {
          id: "benchmarks",
          label: "Research Benchmark",
          icon: BarChart3,
          badge: "Eval",
          badgeColor: "cyan",
        },
      ],
    },
    {
      title: "Documentation",
      items: [
        {
          id: "manual",
          label: "Website Manual",
          icon: BookOpen,
          badge: "Guide",
          badgeColor: "emerald",
        },
      ],
    },
  ];

  return (
    <aside
      className={`h-full overflow-y-auto shrink-0 transition-all duration-300 ease-out bg-paper-3/95 backdrop-blur-2xl border-r border-rule flex flex-col justify-between relative z-20 select-none ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      {/* Top subtle ambient mesh glow */}
      <div className="pointer-events-none absolute top-0 left-0 right-0 h-36 bg-gradient-to-b from-accent/10 to-transparent" />

      <div className="p-3 relative z-10 space-y-4">
        {sections.map((section, sIdx) => (
          <div key={sIdx} className="space-y-1">
            {!collapsed && (
              <div className="flex items-center justify-between px-3 py-1.5 mb-1">
                <span className="text-[10px] font-bold font-mono tracking-widest text-muted uppercase">
                  {section.title}
                </span>
                {sIdx === 0 && (
                  <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-success shadow-sm" />
                  </span>
                )}
              </div>
            )}

            <nav className="space-y-1">
              {section.items.map((item) => {
                const isActive = currentPage === item.id;
                const Icon = item.icon;

                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectPage(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all text-left relative group ${
                      isActive
                        ? "text-ink font-semibold shadow-sm"
                        : "text-muted hover:text-ink hover:bg-paper-hover"
                    }`}
                    title={collapsed ? item.label : undefined}
                  >
                    {/* Active Motion Glass Pill Indicator */}
                    {isActive && (
                      <motion.div
                        layoutId="activeNavIndicator"
                        className="absolute inset-0 rounded-xl bg-accent-subtle/70 border border-accent/30 overflow-hidden"
                        transition={{ type: "spring", stiffness: 380, damping: 30 }}
                      >
                        {/* Left Glowing Accent Bar */}
                        <div className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-accent shadow-sm" />
                      </motion.div>
                    )}

                    <div className="flex items-center gap-3 relative z-10">
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-all duration-200 ${
                          isActive
                            ? "text-accent scale-110"
                            : "text-muted group-hover:text-ink group-hover:scale-105"
                        }`}
                      />
                      {!collapsed && (
                        <span className="tracking-tight font-display truncate">
                          {item.label}
                        </span>
                      )}
                    </div>

                    {!collapsed && item.badge && (
                      <span
                        className={`relative z-10 text-[10px] font-mono px-2 py-0.5 rounded-full font-medium transition-all border ${
                          item.badgeColor === "cyan"
                            ? "bg-accent-2/15 text-accent-2 border-accent-2/30"
                            : item.badgeColor === "emerald"
                            ? "bg-success-bg text-success border-success/30"
                            : "bg-accent-subtle text-accent border-accent/30"
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Footer / System Telemetry Card, Theme Toggle, & Collapse Toggle */}
      <div className="p-3 border-t border-rule space-y-3 relative z-10">
        {/* Theme Toggle Pill */}
        {!collapsed ? (
          <button
            onClick={toggleTheme}
            className="w-full flex items-center justify-between px-3.5 py-2 rounded-xl bg-paper-2 hover:bg-paper-hover border border-rule text-xs transition-colors"
          >
            <div className="flex items-center gap-2 text-ink-2 font-mono text-[11px]">
              {theme === "dark" ? (
                <>
                  <Moon className="w-3.5 h-3.5 text-accent" />
                  <span>Dark Mode</span>
                </>
              ) : (
                <>
                  <Sun className="w-3.5 h-3.5 text-warning" />
                  <span>Light Mode</span>
                </>
              )}
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-paper-3 text-muted border border-rule">
              Switch
            </span>
          </button>
        ) : (
          <button
            onClick={toggleTheme}
            className="w-full flex justify-center p-2 rounded-lg hover:bg-paper-hover text-muted hover:text-ink transition-colors"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          >
            {theme === "dark" ? <Moon className="w-4 h-4 text-accent" /> : <Sun className="w-4 h-4 text-warning" />}
          </button>
        )}

        {/* System Telemetry Bento Card */}
        {!collapsed ? (
          <div className="relative surface-card p-3 rounded-xl border border-rule bg-paper-2 overflow-hidden space-y-2">
            <BorderBeam size={150} duration={12} colorFrom="#6366f1" colorTo="#06b6d4" />

            <div className="relative z-10 flex items-center justify-between text-xs font-mono">
              <span className="text-muted text-[11px]">Backend API</span>
              <span className="inline-flex items-center gap-1 font-semibold text-success text-[11px]">
                <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
                Live: 8000
              </span>
            </div>
            <div className="relative z-10 flex items-center justify-between text-xs font-mono">
              <span className="text-muted text-[11px]">SLM Provider</span>
              <span className="font-semibold text-ink text-[11px]">Ollama 1.5B</span>
            </div>
            <div className="relative z-10 flex items-center justify-between text-xs font-mono">
              <span className="text-muted text-[11px]">Acceleration</span>
              <span className="font-semibold text-accent text-[11px]">CUDA Active</span>
            </div>
          </div>
        ) : (
          <div className="flex justify-center py-1">
            <span
              className="w-2.5 h-2.5 rounded-full bg-success animate-pulse"
              title="Backend Engine Live"
            />
          </div>
        )}

        {/* Collapse button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center gap-1.5 py-1.5 rounded-lg hover:bg-paper-hover text-muted hover:text-ink text-xs font-mono transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          {!collapsed && <span className="text-[11px]">Collapse Navigation</span>}
        </button>
      </div>
    </aside>
  );
};
