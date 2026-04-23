import { PageIntro } from "@/components/sections/PageIntro";
import { api } from "@/lib/api";
import { useApiQuery } from "@/hooks/useApiQuery";
import { ResearchResponse } from "@/types/api";

export function ResearchPage() {
  const { data, loading, error } = useApiQuery<ResearchResponse>(() => api.getResearch(), []);

  return (
    <div className="space-y-8">
      <PageIntro
        eyebrow="Research results"
        title="Ringkasan evaluasi dua sistem RAG dalam format yang lebih analitis."
        description="Halaman ini menerjemahkan isi riset dari aplikasi lama ke tampilan perbandingan yang lebih rapi dan mudah dipindai."
      />

      {loading ? <div className="text-sm text-[var(--muted)]">Memuat hasil penelitian...</div> : null}
      {error ? <div className="text-sm text-[var(--accent)]">{error}</div> : null}

      {data ? (
        <>
          <section className="rounded-[32px] border border-[var(--line)] bg-[var(--surface)] p-6">
            <p className="max-w-3xl text-sm leading-7 text-[var(--foreground)]">{data.summary}</p>
          </section>

          <section className="rounded-[36px] border border-[var(--line)] bg-[var(--surface-strong)] p-8">
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Metrics</p>
            <div className="mt-6 space-y-5">
              {data.metrics.map((metric) => (
                <div key={metric.metric} className="grid gap-4 border-t border-[var(--line)] py-4 md:grid-cols-[220px_1fr]">
                  <div>
                    <p className="text-sm font-medium">{metric.metric}</p>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
                        <span>RAG Sistem 1</span>
                        <span>{metric.system_1.toFixed(2)}</span>
                      </div>
                      <div className="h-2 rounded-full bg-black/8">
                        <div className="h-2 rounded-full bg-[var(--accent)]" style={{ width: `${metric.system_1 * 100}%` }} />
                      </div>
                    </div>
                    <div>
                      <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
                        <span>RAG Sistem 2</span>
                        <span>{metric.system_2.toFixed(2)}</span>
                      </div>
                      <div className="h-2 rounded-full bg-black/8">
                        <div className="h-2 rounded-full bg-[var(--teal)]" style={{ width: `${metric.system_2 * 100}%` }} />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            {data.categories.map((category) => (
              <div key={category.name} className="rounded-[32px] border border-[var(--line)] bg-[var(--surface)] p-6">
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">{category.name}</p>
                <div className="mt-4 space-y-4">
                  {category.questions.map((question) => (
                    <div key={question.label} className="rounded-2xl border border-[var(--line)] bg-white/50 p-4">
                      <p className="text-sm font-medium">{question.label}</p>
                      <div className="mt-3 grid grid-cols-3 gap-3 text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
                        <span>Recall {question.context_recall.toFixed(2)}</span>
                        <span>Precision {question.context_precision.toFixed(2)}</span>
                        <span>Faithfulness {question.faithfulness.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </section>
        </>
      ) : null}
    </div>
  );
}
