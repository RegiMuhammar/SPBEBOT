import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";

type PageIntroProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function PageIntro({ eyebrow, title, description }: PageIntroProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 22 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-4xl space-y-5 pb-10"
    >
      <Badge>{eyebrow}</Badge>
      <h2 className="max-w-3xl text-4xl font-medium leading-tight tracking-[-0.04em] text-[var(--foreground)] md:text-6xl">
        {title}
      </h2>
      <p className="max-w-2xl text-base leading-7 text-[var(--muted)] md:text-lg">{description}</p>
    </motion.div>
  );
}
