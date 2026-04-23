import { ChatPanel } from "@/features/chat/ChatPanel";
import { PageIntro } from "@/components/sections/PageIntro";
import { api } from "@/lib/api";

export function VectorChatPage() {
  return (
    <div className="space-y-8">
      <PageIntro
        eyebrow="Tanya dokumen"
        title="Cari jawaban dari dokumen SPBE dengan pertanyaan yang lebih spesifik."
        description="Halaman ini membantu menemukan potongan informasi yang paling relevan dari kumpulan dokumen SPBE."
      />
      <ChatPanel
        title="Chatbot SPBE"
        description="Gunakan mode ini untuk pertanyaan umum seputar kebijakan, indeks, indikator, dan ringkasan pedoman."
        actionLabel="Kirim ke vector chat"
        onSubmit={api.vectorChat}
      />
    </div>
  );
}
