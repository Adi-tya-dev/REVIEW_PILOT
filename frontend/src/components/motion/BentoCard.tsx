import React from "react";
import { motion } from "framer-motion";
import { BorderBeam } from "./BorderBeam";

interface BentoCardProps {
  title: string;
  subtitle?: string;
  icon?: any;
  value?: React.ReactNode;
  badge?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
  showBeam?: boolean;
  beamColorFrom?: string;
  beamColorTo?: string;
  onClick?: () => void;
}

export const BentoCard: React.FC<BentoCardProps> = ({
  title,
  subtitle,
  icon: Icon,
  value,
  badge,
  children,
  className = "",
  showBeam = false,
  beamColorFrom = "#6366f1",
  beamColorTo = "#06b6d4",
  onClick,
}) => {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 350, damping: 25 }}
      onClick={onClick}
      className={`group relative surface-card p-4 sm:p-5 overflow-hidden transition-all duration-200 ${
        onClick ? "cursor-pointer" : ""
      } ${className}`}
    >
      {/* Background ambient radial glow */}
      <div className="pointer-events-none absolute -inset-px opacity-0 transition-opacity duration-200 group-hover:opacity-100 bg-[radial-gradient(ellipse_at_top_right,rgba(79,70,229,0.08),transparent_70%)]" />

      {/* Optional Border Beam */}
      {showBeam && (
        <BorderBeam
          size={180}
          duration={12}
          colorFrom={beamColorFrom}
          colorTo={beamColorTo}
        />
      )}

      {/* Top Header */}
      <div className="relative z-10 flex items-start justify-between gap-3 mb-2.5">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            {Icon && (
              <div className="p-1 rounded-md bg-accent-subtle text-accent transition-transform group-hover:scale-105">
                <Icon className="w-3.5 h-3.5" />
              </div>
            )}
            <h3 className="text-xs font-semibold text-ink font-display tracking-tight">{title}</h3>
          </div>
          {subtitle && <p className="text-[11px] text-muted leading-relaxed">{subtitle}</p>}
        </div>
        {badge && <div className="shrink-0">{badge}</div>}
      </div>

      {/* Main Metric Value */}
      {value && <div className="relative z-10 my-1">{value}</div>}

      {/* Body / Children */}
      {children && <div className="relative z-10 mt-2">{children}</div>}
    </motion.div>
  );
};

