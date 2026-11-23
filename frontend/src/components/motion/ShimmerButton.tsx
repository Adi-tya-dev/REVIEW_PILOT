import React from "react";

interface ShimmerButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  shimmerColor?: string;
  shimmerSize?: string;
  borderRadius?: string;
  shimmerDuration?: string;
  background?: string;
  className?: string;
  variant?: "primary" | "secondary" | "subtle";
  children?: React.ReactNode;
}

export const ShimmerButton = React.forwardRef<HTMLButtonElement, ShimmerButtonProps>(
  (
    {
      shimmerColor = "#ffffff",
      shimmerSize = "0.05em",
      shimmerDuration = "3.5s",
      borderRadius = "8px",
      background,
      className = "",
      variant = "primary",
      children,
      ...props
    },
    ref,
  ) => {
    // Dynamic background matching ReviewPilot color hierarchy
    const bgClass =
      variant === "primary"
        ? "bg-accent hover:bg-accent-hover text-accent-ink"
        : variant === "secondary"
        ? "bg-paper-2 hover:bg-paper-hover text-ink border border-rule"
        : "bg-transparent hover:bg-paper-hover text-ink-2";

    const backdropBg =
      variant === "primary"
        ? "bg-accent group-hover:bg-accent-hover"
        : variant === "secondary"
        ? "bg-paper-2 group-hover:bg-paper-hover"
        : "bg-paper-3";

    return (
      <button
        ref={ref}
        style={
          {
            "--spread": "90deg",
            "--shimmer-color": shimmerColor,
            "--radius": borderRadius,
            "--speed": shimmerDuration,
            "--cut": shimmerSize,
          } as React.CSSProperties
        }
        className={`group relative z-0 inline-flex cursor-pointer items-center justify-center overflow-hidden whitespace-nowrap px-4 py-2 text-xs font-semibold [border-radius:var(--radius)] transition-transform duration-200 active:scale-[0.98] shadow-sm ${bgClass} ${className}`}
        {...props}
      >
        {/* Subtle light sweep spark container */}
        <div className="-z-30 blur-[1px] absolute inset-0 overflow-visible opacity-40 [container-type:size]">
          <div className="absolute inset-0 h-[100cqh] animate-shimmer-slide [aspect-ratio:1] [border-radius:0] [mask:none]">
            <div className="animate-spin-around absolute -inset-full w-auto rotate-0 [background:conic-gradient(from_calc(270deg-(var(--spread)*0.5)),transparent_0,var(--shimmer-color)_var(--spread),transparent_var(--spread))] [translate:0_0]" />
          </div>
        </div>

        {/* Backdrop highlight matching primary token */}
        <div className={`absolute inset-[var(--cut)] -z-20 rounded-[inherit] ${backdropBg} transition-colors duration-200`} />

        {/* Content */}
        <span className="relative z-10 flex items-center gap-2">
          {children}
        </span>
      </button>
    );
  },
);

ShimmerButton.displayName = "ShimmerButton";


