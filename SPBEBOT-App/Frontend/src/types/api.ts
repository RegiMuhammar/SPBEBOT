export type OverviewResponse = {
  hero: {
    eyebrow: string;
    title: string;
    description: string;
    highlights: string[];
  };
  sections: Array<{ title: string; body: string }>;
  quick_facts: Array<{ label: string; value: string }>;
};

export type DocumentItem = {
  name: string;
  path: string;
  size_bytes: number;
  page_count?: number | null;
  preview?: string | null;
  content_type: string;
};

export type DocumentsResponse = {
  total: number;
  items: DocumentItem[];
};

export type DocumentAccessResponse = {
  allowed: boolean;
};

export type ChatSource = {
  id: string;
  title: string;
  source: string;
  score: number;
  excerpt: string;
};

export type ChatResponse = {
  mode: string;
  answer: string;
  question: string;
  sources: ChatSource[];
  follow_up_suggestions: string[];
};

export type GraphNode = {
  id: string;
  label: string;
  category: string;
  description: string;
  size: number;
  color: string;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  label: string;
};

export type GraphPayload = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: Record<string, number>;
};

export type GraphSearchResponse = {
  query: string;
  graph: GraphPayload;
  related_items: Array<{
    id: string;
    label: string;
    category: string;
    description: string;
    score: number;
  }>;
};

export type DashboardResponse = {
  total_index: number;
  domains: Array<{ code: string; name: string; value: number }>;
  aspects: Array<{ code: string; name: string; indicator_count: number }>;
};

export type PromptsResponse = {
  items: Array<{ id: string; title: string; prompt: string }>;
};

export type ResearchResponse = {
  summary: string;
  metrics: Array<{ metric: string; system_1: number; system_2: number }>;
  categories: Array<{
    name: string;
    questions: Array<{
      label: string;
      context_recall: number;
      context_precision: number;
      faithfulness: number;
    }>;
  }>;
};
