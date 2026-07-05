import { forwardRef } from "react";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-nexus-cyan text-nexus-bg hover:bg-nexus-cyan/90 shadow-glow-cyan font-semibold",
  secondary:
    "bg-nexus-surface2 text-nexus-text border border-nexus-border hover:border-nexus-cyan/50 hover:text-nexus-cyan",
  ghost: "bg-transparent text-nexus-muted hover:text-nexus-text hover:bg-white/5",
  danger: "bg-transparent text-nexus-red border border-nexus-red/40 hover:bg-nexus-red/10",
};

const sizeClasses: Record<Size, string> = {
  sm: "text-xs px-2.5 py-1.5 gap-1.5",
  md: "text-sm px-3.5 py-2 gap-2",
  lg: "text-base px-5 py-3 gap-2",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", className = "", children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`focus-ring inline-flex items-center justify-center rounded-md transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-40 ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
