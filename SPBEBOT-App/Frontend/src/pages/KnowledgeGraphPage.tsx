import { useState } from "react";
import { Search } from "lucide-react";
import { PageIntro } from "@/components/sections/PageIntro";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { GraphViewMode, KnowledgeGraphCanvas } from "@/features/graph/KnowledgeGraphCanvas";
import { api } from "@/lib/api";
import { useApiQuery } from "@/hooks/useApiQuery";
import { GraphPayload, GraphSearchResponse } from "@/types/api";

export function KnowledgeGraphPage() {
  const { data, loading, error } = useApiQuery<GraphPayload>(() => api.getGraph(false, 3), []);
  const [query, setQuery] = useState("");
  const [searchResult, setSearchResult] = useState<GraphSearchResponse | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);
  const [fullGraph, setFullGraph] = useState<GraphPayload | null>(null);
  const [loadingFullGraph, setLoadingFullGraph] = useState(false);
  const [viewMode, setViewMode] = useState<GraphViewMode>("fast");
  const [canvasRendering, setCanvasRendering] = useState(false);

  async function loadFullGraph() {
    if (fullGraph) {
      setFullGraph(null);
      return;
    }

    setLoadingFullGraph(true);
    setSearchError(null);

    try {
      const graph = await api.getGraph(true);
      setFullGraph(graph);
      setSearchResult(null);
      // Auto-switch ke fast untuk graph besar agar tidak freeze
      if (graph.nodes.length > 350) {
        setViewMode("fast");
      }
    } catch (requestError) {
      setSearchError(requestError instanceof Error ? requestError.message : "Memuat graph penuh gagal.");
    } finally {
      setLoadingFullGraph(false);
    }
  }

  async function runSearch() {
    if (!query.trim()) {
      setSearchResult(null);
      return;
    }

    setSearching(true);
    setSearchError(null);

    try {
      const result = await api.searchGraph(query);
      setSearchResult(result);
    } catch (requestError) {
      setSearchError(requestError instanceof Error ? requestError.message : "Pencarian graph gagal.");
    } finally {
      setSearching(false);
    }
  }

  const graph = searchResult?.graph ?? fullGraph ?? data ?? null;
  const isFullMode = !!fullGraph && !searchResult;
  const totalInGraph = graph?.stats?.total_nodes_in_graph;
  const shownNodes = graph?.stats?.nodes;

  return (
    <div className="space-y-8">
      <PageIntro
        eyebrow="Peta SPBE"
        title="Lihat hubungan antar unsur evaluasi SPBE secara visual."
        description="Halaman ini menyajikan struktur domain, aspek, indikator, dan rujukan penting agar mudah ditelusuri dan dipahami."
      />

      <section className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <div className="flex flex-col gap-3 rounded-[28px] border border-[var(--line)] bg-[var(--surface)] p-5 md:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]" />
              <Input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") runSearch();
                }}
                className="pl-10"
                placeholder="Cari domain, aspek, indikator, atau istilah seperti audit TIK."
              />
            </div>
            <Button variant="accent" onClick={runSearch} disabled={searching || loadingFullGraph || canvasRendering}>
              {searching ? "Mencari..." : canvasRendering ? "Merender..." : "Cari graph"}
            </Button>
            <Button
              variant="outline"
              className="bg-[#ececec] border-[#d6d6d6] text-[#1f1f1f] hover:bg-[#e2e2e2]"
              onClick={loadFullGraph}
              disabled={loadingFullGraph || searching || canvasRendering}
            >
              {loadingFullGraph
                ? "Memuat..."
                : canvasRendering
                  ? "Merender..."
                  : fullGraph
                    ? "Kembali Ringan"
                    : "Muat Graph Penuh"}
            </Button>
          </div>
          <div className="flex flex-wrap items-center gap-2 rounded-[20px] border border-[var(--line)] bg-white/60 p-3">
            <span className="px-2 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">View Mode</span>
            <Button
              size="sm"
              variant={viewMode === "fast" ? "accent" : "outline"}
              onClick={() => setViewMode("fast")}
              disabled={canvasRendering}
            >
              Fast
            </Button>
            <Button
              size="sm"
              variant={viewMode === "balanced" ? "accent" : "outline"}
              onClick={() => setViewMode("balanced")}
              disabled={canvasRendering}
            >
              Balanced
            </Button>
            <Button
              size="sm"
              variant={viewMode === "detail" ? "accent" : "outline"}
              onClick={() => setViewMode("detail")}
              disabled={canvasRendering}
            >
              Detail
            </Button>
          </div>

          {/* Status messages */}
          {loading ? <div className="text-sm text-[var(--muted)]">Memuat graph lokal ringan...</div> : null}

          {isFullMode && shownNodes != null && totalInGraph != null && totalInGraph > shownNodes ? (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm text-amber-800">
              Mode penuh aktif — menampilkan <strong>{shownNodes}</strong> node terkonektif dari total{" "}
              <strong>{totalInGraph}</strong> node. Gunakan <em>Fast</em> mode untuk performa terbaik.
            </div>
          ) : isFullMode ? (
            <div className="text-sm text-[var(--muted)]">
              Mode penuh aktif. Performa browser bisa menurun pada perangkat tertentu.
            </div>
          ) : null}

          {viewMode === "fast" ? (
            <div className="text-sm text-[var(--muted)]">Fast mode: layout cepat (concentric), label dan edge disederhanakan.</div>
          ) : viewMode === "balanced" ? (
            <div className="text-sm text-[var(--muted)]">Balanced mode: layout fcose — seimbang antara kerapihan dan performa.</div>
          ) : (
            <div className="text-sm text-[var(--muted)]">Detail mode: fcose quality tinggi, lebih lambat di graph besar.</div>
          )}

          {canvasRendering ? (
            <div className="text-sm text-[var(--muted)]">Graph sedang dirender, mohon tunggu sebentar...</div>
          ) : null}
          {error ? <div className="text-sm text-[var(--accent)]">{error}</div> : null}
          {searchError ? <div className="text-sm text-[var(--accent)]">{searchError}</div> : null}

          {graph ? (
            <div className="relative">
              <KnowledgeGraphCanvas graph={graph} viewMode={viewMode} onRenderingChange={setCanvasRendering} />
              {canvasRendering ? (
                <div className="pointer-events-none absolute inset-0 grid place-items-center rounded-[28px] bg-white/55 backdrop-blur-[1px]">
                  <div className="rounded-full border border-[var(--line)] bg-white/90 px-4 py-2 text-sm text-[var(--foreground)]">
                    Merender graph...
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>

        <aside className="space-y-4">
          <div className="rounded-[28px] border border-[var(--line)] bg-[var(--surface-strong)] p-6">
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Stats</p>
            <div className="mt-5 grid gap-4">
              {graph
                ? Object.entries(graph.stats)
                    .filter(([key]) => key !== "total_nodes_in_graph")
                    .map(([key, value]) => (
                      <div key={key} className="border-t border-[var(--line)] pt-4">
                        <p className="text-3xl font-medium">{value}</p>
                        <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">{key}</p>
                      </div>
                    ))
                : null}
            </div>
          </div>

          <div className="rounded-[28px] border border-[var(--line)] bg-[var(--surface)] p-6">
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Related nodes</p>
            <div className="mt-5 space-y-3">
              {searchResult?.related_items?.length ? (
                searchResult.related_items.slice(0, 6).map((item) => (
                  <div key={item.id} className="rounded-2xl border border-[var(--line)] bg-white/50 p-4">
                    <div className="flex items-center justify-between gap-4">
                      <h3 className="text-sm font-medium">{item.label}</h3>
                      <span className="text-xs text-[var(--muted)]">{item.score}</span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{item.description}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm leading-6 text-[var(--muted)]">
                  Jalankan pencarian untuk melihat node yang paling relevan dan subgraph fokusnya.
                </p>
              )}
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}
