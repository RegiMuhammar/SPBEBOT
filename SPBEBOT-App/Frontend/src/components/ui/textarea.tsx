import * as React from "react";
import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "min-h-[160px] w-full rounded-[24px] border border-[var(--line)] bg-white/70 px-4 py-4 text-sm text-[var(--foreground)] outline-none transition focus:border-[var(--foreground)]",
      className,
    )}
    {...props}
  />
));

Textarea.displayName = "Textarea";
