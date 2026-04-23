import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
// @ts-expect-error — cytoscape-fcose tidak menyediakan type declaration resmi
import fcose from "cytoscape-fcose";
import { GraphPayload } from "@/types/api";

// Daftarkan extension fcose sekali saja (idempotent)
try { cytoscape.use(fcose); } catch { /* sudah terdaftar */ }

export type GraphViewMode = "fast" | "balanced" | "detail";

type KnowledgeGraphCanvasProps = {
  graph: GraphPayload;
  viewMode?: GraphViewMode;
  onRenderingChange?: (rendering: boolean) => void;
};

const CATEGORY_RANK: Record<string, number> = {
  root: 10,
  spbe: 10,
  domain: 9,
  aspek: 8,
  aspect: 8,
  indikator: 7,
  indicator: 7,
  level: 6,
  document: 5,
  bab_pedoman: 4,
  poin_pedoman: 3,
  entity: 2,
  question: 1,
};

/**
 * Batas aman node yang dirender di canvas.
 * Backend sudah membatasi ke MAX_FULL_GRAPH_NODES (700), tapi ini
 * sebagai safety net di frontend agar browser tidak freeze.
 */
const MAX_RENDER_NODES = 750;

export function KnowledgeGraphCanvas({
  graph,
  viewMode = "balanced",
  onRenderingChange,
}: KnowledgeGraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const layoutCacheRef = useRef<Record<string, Record<string, { x: number; y: number }>>>({});

  useEffect(() => {
    if (!containerRef.current) return;

    // Batasi node jika melebihi MAX_RENDER_NODES (safety net frontend)
    const allNodes = graph.nodes.slice(0, MAX_RENDER_NODES);
    const nodeIdSet = new Set(allNodes.map((n) => n.id));
    const allEdges = graph.edges.filter(
      (e) => nodeIdSet.has(e.source) && nodeIdSet.has(e.target),
    );

    const totalNodes = allNodes.length;
    const totalEdges = allEdges.length;

    // Threshold graph "besar" disesuaikan dengan batas baru (700 node)
    const isLargeGraph = totalNodes > 350 || totalEdges > 700;
    const isFast = viewMode === "fast";
    const isDetail = viewMode === "detail";
    const showNodeLabels = isDetail || (!isFast && !isLargeGraph);
    const showArrows = isDetail || !isLargeGraph;

    const graphKey = `${viewMode}:${totalNodes}:${totalEdges}:${allNodes[0]?.id ?? "none"}:${
      allNodes[allNodes.length - 1]?.id ?? "none"
    }`;

    let cancelled = false;
    let loadingTimeout: ReturnType<typeof setTimeout> | undefined;
    onRenderingChange?.(true);

    const instance = cytoscape({
      container: containerRef.current,
      elements: [
        ...allNodes.map((node) => ({
          data: {
            id: node.id,
            label: node.label,
            description: node.description,
            category: node.category,
            size: node.size,
            color: node.color,
          },
        })),
        ...allEdges.map((edge) => ({
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.label,
          },
        })),
      ],
      style: [
        {
          selector: "node",
          style: {
            "background-color": "data(color)",
            label: showNodeLabels ? "data(label)" : "",
            color: "#111111",
            "font-size": isDetail ? 11 : 10,
            "font-weight": 600,
            "text-wrap": "wrap",
            "text-max-width": isDetail ? "120px" : "90px",
            "text-valign": "bottom",
            "text-margin-y": 8,
            width: "mapData(size, 1, 3.5, 18, 62)",
            height: "mapData(size, 1, 3.5, 18, 62)",
          },
        },
        {
          selector: "edge",
          style: {
            width: isDetail ? 1.2 : isLargeGraph ? 0.85 : 1.0,
            "curve-style": isFast && isLargeGraph ? "haystack" : "bezier",
            "line-color": "rgba(17,17,17,0.2)",
            "target-arrow-color": showArrows ? "rgba(17,17,17,0.2)" : "rgba(0,0,0,0)",
            "target-arrow-shape": showArrows ? "triangle" : "none",
            "arrow-scale": showArrows ? 0.8 : 0,
          },
        },
      ],
      layout: { name: "preset", fit: true, padding: 24, animate: false },
      wheelSensitivity: 0.2,
      textureOnViewport: true,
      hideEdgesOnViewport: isFast && isLargeGraph,
      hideLabelsOnViewport: !isDetail && isLargeGraph,
      motionBlur: false,
      pixelRatio: 1,
      minZoom: 0.08,
      maxZoom: 3.2,
    });

    const finishRendering = () => {
      if (cancelled) return;
      onRenderingChange?.(false);
      if (loadingTimeout) clearTimeout(loadingTimeout);
    };

    const cached = layoutCacheRef.current[graphKey];
    if (cached) {
      instance.nodes().forEach((node) => {
        const pos = cached[node.id()];
        if (pos) node.position(pos);
      });
      instance.fit(undefined, 24);
      instance.center();
      finishRendering();
    } else {
      // ----------------------------------------------------------------
      // Pemilihan layout:
      //  fast       → concentric (O(n), sangat cepat)
      //  balanced   → fcose (force-directed modern, jauh lebih cepat dari cose)
      //  detail     → fcose quality "proof" (lebih akurat tapi lebih lambat)
      // ----------------------------------------------------------------
      // Cytoscape extensions (fcose, concentric) memiliki opsi tambahan
      // (fit, padding, dll.) yang tidak ada di BaseLayoutOptions.
      // Cast via unknown diperlukan karena @types/cytoscape hanya tahu
      // layout bawaan, bukan extension yang didaftarkan secara runtime.
      const layoutOptions = (
        isFast
          ? {
              name: "concentric",
              fit: true,
              padding: 24,
              animate: false,
              startAngle: (-3 * Math.PI) / 4,
              sweep: 2 * Math.PI,
              minNodeSpacing: 10,
              concentric: (node: cytoscape.NodeSingular) =>
                CATEGORY_RANK[node.data("category")] ?? 0,
              levelWidth: () => 1,
            }
          : isDetail
            ? {
                name: "fcose",
                fit: true,
                padding: 24,
                animate: false,
                quality: isLargeGraph ? "default" : "proof",
                randomize: true,
                nodeRepulsion: isLargeGraph ? 6500 : 8000,
                idealEdgeLength: isLargeGraph ? 70 : 90,
                edgeElasticity: 0.45,
                gravity: isLargeGraph ? 0.35 : 0.25,
                gravityRange: 3.8,
                numIter: isLargeGraph ? 2500 : 5000,
                nodeSeparation: 80,
                packComponents: true,
              }
            : {
                name: "fcose",
                fit: true,
                padding: 24,
                animate: false,
                quality: "default",
                randomize: true,
                nodeRepulsion: isLargeGraph ? 5000 : 7000,
                idealEdgeLength: isLargeGraph ? 60 : 80,
                edgeElasticity: 0.4,
                gravity: isLargeGraph ? 0.4 : 0.3,
                gravityRange: 3.8,
                numIter: isLargeGraph ? 1500 : 3000,
                nodeSeparation: 60,
                packComponents: true,
              }
      ) as unknown as cytoscape.LayoutOptions;

      const layout = instance.layout(layoutOptions);

      layout.one("layoutstop", () => {
        if (!cancelled) {
          const positions: Record<string, { x: number; y: number }> = {};
          instance.nodes().forEach((node) => {
            positions[node.id()] = node.position();
          });
          layoutCacheRef.current[graphKey] = positions;
        }
        finishRendering();
      });

      // Timeout safety: 20 detik untuk graph penuh, 10 detik untuk overview
      loadingTimeout = setTimeout(
        () => { finishRendering(); },
        isLargeGraph ? 20000 : 10000,
      );

      requestAnimationFrame(() => {
        if (!cancelled) layout.run();
      });
    }

    return () => {
      cancelled = true;
      if (loadingTimeout) clearTimeout(loadingTimeout);
      onRenderingChange?.(false);
      instance.destroy();
    };
  }, [graph, viewMode, onRenderingChange]);

  return <div ref={containerRef} className="h-[560px] rounded-[28px] border border-[var(--line)] bg-white/65" />;
}
