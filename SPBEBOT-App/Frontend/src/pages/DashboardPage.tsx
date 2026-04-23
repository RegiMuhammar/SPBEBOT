import { PageIntro } from "@/components/sections/PageIntro";
import { api } from "@/lib/api";
import { useApiQuery } from "@/hooks/useApiQuery";
import { DashboardResponse } from "@/types/api";

export function DashboardPage() {
  const { data, loading, error } = useApiQuery<DashboardResponse>(() => api.getDashboard(), []);

  return (
    <div className="space-y-8">
      <PageIntro
        eyebrow="Indeks SPBE"
        title="Ringkasan nilai untuk membaca kondisi SPBE secara cepat."
        description="Halaman ini menampilkan gambaran umum agar domain dan aspek bisa dipahami tanpa harus membuka banyak bagian sekaligus."
      />

      {loading ? <div className="text-sm text-[var(--muted)]">Memuat dashboard...</div> : null}
      {error ? <div className="text-sm text-[var(--accent)]">{error}</div> : null}

      {data ? (
        <>
          <section className="rounded-[40px] border border-[var(--line)] bg-[var(--foreground)] p-8 text-[var(--background)]">
            <p className="text-xs uppercase tracking-[0.24em] text-white/55">Nilai indeks total</p>
            <div className="mt-6 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
              <p className="display-serif text-8xl italic">{data.total_index.toFixed(2)}</p>
              <p className="max-w-xl text-sm leading-7 text-white/70">
                Fokus utama tetap pada angka total, lalu domain ditampilkan sebagai rincian yang mudah dibaca.
              </p>
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-4">
            {data.domains.map((domain) => (
              <div key={domain.code} className="rounded-[28px] border border-[var(--line)] bg-[var(--surface)] p-6">
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">{domain.code}</p>
                <p className="mt-6 text-4xl font-medium tracking-[-0.06em]">{domain.value.toFixed(2)}</p>
                <p className="mt-2 text-sm text-[var(--muted)]">{domain.name}</p>
              </div>
            ))}
          </section>

          <section className="rounded-[36px] border border-[var(--line)] bg-[var(--surface-strong)] p-8">
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Aspek SPBE</p>
            <div className="mt-6 space-y-4">
              {data.aspects.map((aspect) => (
                <div
                  key={aspect.code}
                  className="grid gap-4 border-t border-[var(--line)] py-4 md:grid-cols-[120px_1fr_100px]"
                >
                  <p className="text-sm font-medium">{aspect.code}</p>
                  <p className="text-sm leading-7">{aspect.name}</p>
                  <p className="text-right text-sm text-[var(--muted)]">{aspect.indicator_count} indikator</p>
                </div>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
