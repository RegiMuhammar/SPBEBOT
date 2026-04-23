import type {
  ChatResponse,
  DashboardResponse,
  DocumentAccessResponse,
  DocumentItem,
  DocumentsResponse,
  GraphPayload,
  GraphSearchResponse,
  OverviewResponse,
  PromptsResponse,
  ResearchResponse,
} from "@/types/api";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function uploadDocument(file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `HTTP ${response.status}`);
  }

  return response.json() as Promise<DocumentItem>;
}

export const api = {
  getOverview: () => request<OverviewResponse>("/content/overview"),
  getDocuments: () => request<DocumentsResponse>("/documents"),
  verifyDocumentAccess: (key: string) =>
    request<DocumentAccessResponse>("/documents/access", {
      method: "POST",
      body: JSON.stringify({ key }),
    }),
  getDashboard: () => request<DashboardResponse>("/content/dashboard"),
  getPromptTemplates: () => request<PromptsResponse>("/content/prompts"),
  getResearch: () => request<ResearchResponse>("/content/research"),
  getGraph: (full = false, indicatorsPerAspect = 3) =>
    request<GraphPayload>(
      `/graph?full=${String(full)}&indicators_per_aspect=${encodeURIComponent(String(indicatorsPerAspect))}`
    ),
  searchGraph: (query: string) => request<GraphSearchResponse>(`/graph/search?q=${encodeURIComponent(query)}`),
  vectorChat: (question: string) =>
    request<ChatResponse>("/chat/vector", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
  graphChat: (question: string) =>
    request<ChatResponse>("/chat/graph", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
  uploadDocument,
};
