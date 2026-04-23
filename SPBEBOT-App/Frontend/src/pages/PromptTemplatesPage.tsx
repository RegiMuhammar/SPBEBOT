import { PageIntro } from "@/components/sections/PageIntro";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useApiQuery } from "@/hooks/useApiQuery";
import { PromptsResponse } from "@/types/api";

export function PromptTemplatesPage() {
  const { data, loading, error } = useApiQuery<PromptsResponse>(() => api.getPromptTemplates(), []);

  async function copyPrompt(prompt: string) {
    await navigator.clipboard.writeText(prompt);
  }

  return (
    <div className="space-y-8">
      <PageIntro
        eyebrow="Kumpulan panduan"
        title="Template yang membantu menjawab kebutuhan SPBE yang sering muncul."
        description="Setiap template dirancang agar bisa dipakai ulang saat mencari penjelasan, ringkasan, atau arah pembahasan."
      />

      {loading ? <div className="text-sm text-[var(--muted)]">Memuat template...</div> : null}
      {error ? <div className="text-sm text-[var(--accent)]">{error}</div> : null}

      {data ? (
        <div className="grid gap-4">
          {data.items.map((item, index) => (
            <div key={item.id} className="rounded-[30px] border border-[var(--line)] bg-[var(--surface)] p-6">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="space-y-3">
                  <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">
                    template {String(index + 1).padStart(2, "0")}
                  </p>
                  <h3 className="text-2xl font-medium tracking-[-0.04em]">{item.title}</h3>
                  <p className="max-w-3xl text-sm leading-7 text-[var(--foreground)]">{item.prompt}</p>
                </div>
                <Button variant="outline" onClick={() => copyPrompt(item.prompt)}>
                  Salin prompt
                </Button>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
