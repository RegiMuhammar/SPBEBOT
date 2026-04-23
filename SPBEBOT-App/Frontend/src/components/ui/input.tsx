import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-12 w-full rounded-2xl border border-[var(--line)] bg-white/70 px-4 text-sm text-[var(--foreground)] outline-none transition focus:border-[var(--foreground)]",
        className,
      )}
      {...props}
    />
  ),
);

Input.displayName = "Input";
