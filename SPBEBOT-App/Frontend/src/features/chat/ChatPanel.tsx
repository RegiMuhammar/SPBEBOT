import { useState } from "react";
import { ArrowUpRight, Bot, ChevronDown, LoaderCircle, SendHorizonal, User2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ChatResponse } from "@/types/api";

type ChatPanelProps = {
  title: string;
  description: string;
  actionLabel: string;
  onSubmit: (question: string) => Promise<ChatResponse>;
};

export function ChatPanel({ title, description, actionLabel, onSubmit }: ChatPanelProps) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([
    {
      role: "assistant",
      content:
        "Halo, saya siap bantu terkait SPBE. Tanyakan domain, aspek, indikator, indeks nasional, atau ringkasan pedoman.",
    },
  ]);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sourceCount = result?.sources.length ?? 0;

  async function handleSubmit() {
    const trimmed = question.trim();
    if (!trimmed) return;

    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setLoading(true);
    setError(null);
    try {
      const next = await onSubmit(trimmed);
      setResult(next);
      setMessages((current) => [...current, { role: "assistant", content: next.answer }]);
      setQuestion("");
    } catch (submissionError) {
      setError(
        submissionError instanceof Error ? submissionError.message : "Permintaan gagal diproses.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6">
      <section className="overflow-hidden rounded-[32px] border border-[var(--line)] bg-[var(--surface)] shadow-[var(--shadow)]">
        <div className="border-b border-[var(--line)] px-6 py-5">
          <div className="space-y-2">
            <h3 className="text-2xl font-medium tracking-[-0.04em]">{title}</h3>
            <p className="max-w-2xl text-sm leading-6 text-[var(--muted)]">{description}</p>
          </div>
        </div>

        <div className="space-y-4 bg-white/30 px-4 py-5 md:px-6">
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {message.role === "assistant" ? (
                <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[var(--foreground)] text-white">
                  <Bot className="h-4 w-4" />
                </div>
              ) : null}

              <div
                className={`max-w-[85%] rounded-[24px] px-4 py-3 text-sm leading-7 ${
                  message.role === "assistant"
                    ? "bg-[var(--surface-strong)] text-[var(--foreground)]"
                    : "bg-[var(--foreground)] text-white"
                }`}
              >
                <p className="whitespace-pre-line">{message.content}</p>

                {message.role === "assistant" && result && index === messages.length - 1 ? (
                  <details className="group mt-3 rounded-2xl border border-[var(--line)] bg-white/55">
                    <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 text-xs font-medium uppercase tracking-[0.22em] text-[var(--muted)]">
                      <span>Session info</span>
                      <span className="rounded-full border border-[var(--line)] bg-white/70 px-2 py-0.5 text-[10px] tracking-[0.18em] text-[var(--muted)]">
                        {sourceCount} sources
                      </span>
                      <ChevronDown className="h-4 w-4 transition duration-200 group-open:rotate-180" />
                    </summary>
                    <div className="space-y-5 border-t border-[var(--line)] px-4 py-4">
                      <div className="space-y-3">
                        <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Sources</p>
                        {result.sources.length ? (
                          result.sources.map((source) => (
                            <div key={source.id} className="rounded-2xl border border-[var(--line)] bg-white/60 p-4">
                              <div className="flex items-center justify-between gap-4">
                                <h4 className="text-sm font-medium">{source.title}</h4>
                                <span className="text-xs text-[var(--muted)]">score {source.score}</span>
                              </div>
                              <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{source.excerpt}</p>
                              <p className="mt-2 text-[11px] uppercase tracking-[0.2em] text-[var(--muted)]">
                                {source.source}
                              </p>
                            </div>
                          ))
                        ) : (
                          <div className="rounded-2xl border border-dashed border-[var(--line)] bg-white/60 p-4">
                            <p className="text-sm font-medium text-[var(--foreground)]">
                              Jawaban ini belum menemukan konteks yang cukup di Pinecone.
                            </p>
                            <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
                              Coba pertanyaan yang lebih spesifik, sebutkan tahun, domain, indikator, atau kata kunci dokumen yang lebih jelas.
                            </p>
                          </div>
                        )}
                      </div>

                      <div className="space-y-3">
                        <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Next prompts</p>
                        <div className="space-y-2">
                          {result.follow_up_suggestions.map((item) => (
                            <button
                              key={item}
                              onClick={() => setQuestion(item)}
                              className="flex w-full items-center justify-between rounded-2xl border border-[var(--line)] bg-white/60 px-4 py-3 text-left text-sm transition hover:border-[var(--foreground)]"
                            >
                              {item}
                              <ArrowUpRight className="h-4 w-4 text-[var(--muted)]" />
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </details>
                ) : null}
              </div>

              {message.role === "user" ? (
                <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[var(--accent)] text-white">
                  <User2 className="h-4 w-4" />
                </div>
              ) : null}
            </div>
          ))}

          {loading ? (
            <div className="flex gap-3">
              <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[var(--foreground)] text-white">
                <Bot className="h-4 w-4" />
              </div>
              <div className="rounded-[24px] bg-[var(--surface-strong)] px-4 py-3 text-sm text-[var(--muted)]">
                SPBEBOT sedang menyusun jawaban...
              </div>
            </div>
          ) : null}
        </div>

        <div className="border-t border-[var(--line)] px-4 py-4 md:px-6">
          <Textarea
            placeholder="Tulis pertanyaan yang spesifik, misalnya: Jelaskan indikator untuk domain layanan atau tampilkan ringkasan indeks SPBE nasional 2021-2023."
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                void handleSubmit();
              }
            }}
            className="min-h-[120px] bg-white/65"
          />
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">
              {actionLabel} · Ctrl/Cmd + Enter untuk kirim
            </p>
            <Button variant="accent" onClick={() => void handleSubmit()} disabled={loading}>
              {loading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <SendHorizonal className="mr-2 h-4 w-4" />}
              {actionLabel}
            </Button>
          </div>
          {error ? <p className="text-sm text-[var(--accent)]">{error}</p> : null}
        </div>
      </section>
    </div>
  );
}
