import { ChatPanel } from "@/features/chat/ChatPanel";
import { PageIntro } from "@/components/sections/PageIntro";
import { api } from "@/lib/api";

export function GraphChatPage() {
  return (
    <div className="space-y-8">
      <PageIntro
        eyebrow="Peta keterkaitan"
        title="Ajukan pertanyaan untuk menelusuri hubungan antar unsur SPBE."
        description="Mode ini membantu membaca keterkaitan domain, aspek, indikator, dan bahan evaluasi dalam satu alur."
      />
      <ChatPanel
        title="Graph Chat"
        description="Cocok untuk menelusuri hubungan domain, aspek, indikator, dan bahan evaluasi pada graph lokal."
        actionLabel="Kirim ke graph chat"
        onSubmit={api.graphChat}
      />
    </div>
  );
}
