import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";
import { PageIntro } from "@/components/sections/PageIntro";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useApiQuery } from "@/hooks/useApiQuery";
import { OverviewResponse } from "@/types/api";

export function OverviewPage() {
  const { data, loading, error } = useApiQuery<OverviewResponse>(() => api.getOverview(), []);

  if (loading) return <div className="text-sm text-[var(--muted)]">Memuat overview platform...</div>;
  if (error || !data) return <div className="text-sm text-[var(--accent)]">{error ?? "Gagal memuat data."}</div>;

  return (
    <div className="space-y-12">
      <PageIntro
        eyebrow={data.hero.eyebrow}
        title={data.hero.title}
        description={data.hero.description}
      />

      <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="relative overflow-hidden rounded-[40px] border border-[var(--line)] bg-[var(--foreground)] p-8 text-[var(--background)] shadow-[var(--shadow)]"
        >
          <div
            className="absolute inset-0 opacity-35"
            style={{
              backgroundImage:
                "linear-gradient(130deg, rgba(255,255,255,0.06), rgba(255,255,255,0) 35%), url('/editorial-data-weave.png')",
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          />
          <div className="relative z-10 flex h-full flex-col justify-between gap-8">
            <div className="space-y-5">
              <p className="text-xs uppercase tracking-[0.24em] text-white/55">Ringkasan aplikasi</p>
              <h3 className="max-w-xl text-4xl font-medium leading-tight tracking-[-0.05em]">
                Satu ruang untuk membaca pedoman, menelusuri dokumen, dan melihat konteks evaluasi SPBE.
              </h3>
              <div className="grid gap-3 md:grid-cols-3">
                {data.quick_facts.map((fact) => (
                  <div key={fact.label} className="border-t border-white/15 pt-4">
                    <p className="text-3xl font-medium">{fact.value}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.18em] text-white/60">{fact.label}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link to="/chat/vector">
                <Button variant="accent" size="lg">
                  Mulai eksplorasi
                </Button>
              </Link>
              <Link to="/knowledge-graph">
                <Button variant="outline" size="lg" className="border-white/20 text-white hover:bg-white/10">
                  Buka graph
                </Button>
              </Link>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="rounded-[40px] border border-[var(--line)] bg-[var(--surface)] p-8"
        >
          <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Yang bisa dilakukan</p>
          <div className="mt-8 space-y-5">
            {data.hero.highlights.map((item, index) => (
              <div key={item} className="flex items-start gap-4 border-t border-[var(--line)] pt-5">
                <span className="display-serif text-3xl italic text-[var(--accent)]">0{index + 1}</span>
                <p className="text-sm leading-7 text-[var(--foreground)]">{item}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {data.sections.map((section, index) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + index * 0.08, duration: 0.5 }}
            className="rounded-[32px] border border-[var(--line)] bg-white/65 p-7"
          >
            <p className="text-xs uppercase tracking-[0.22em] text-[var(--muted)]">{section.title}</p>
            <p className="mt-4 text-lg leading-8 text-[var(--foreground)]">{section.body}</p>
          </motion.div>
        ))}
      </section>

      <section className="rounded-[40px] border border-[var(--line)] bg-[var(--surface-strong)] p-8">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Alur pakai</p>
            <h3 className="mt-3 max-w-2xl text-3xl font-medium tracking-[-0.04em]">
              Mulai dari dokumen, lanjut ke tanya jawab, lalu lihat gambaran besar dan temuan pentingnya.
            </h3>
          </div>
          <Link
            to="/documents"
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--accent)] transition hover:gap-3"
          >
            Buka ruang dokumen
            <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
