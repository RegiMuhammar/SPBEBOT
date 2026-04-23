import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/pages/DashboardPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { GraphChatPage } from "@/pages/GraphChatPage";
import { KnowledgeGraphPage } from "@/pages/KnowledgeGraphPage";
import { OverviewPage } from "@/pages/OverviewPage";
import { PromptTemplatesPage } from "@/pages/PromptTemplatesPage";
import { ResearchPage } from "@/pages/ResearchPage";
import { VectorChatPage } from "@/pages/VectorChatPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/chat/vector" element={<VectorChatPage />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
        <Route path="/chat/graph" element={<GraphChatPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/prompt-templates" element={<PromptTemplatesPage />} />
        <Route path="/research" element={<ResearchPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
