import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import { CircleAlert, LockKeyhole, ShieldCheck } from "lucide-react";
import { PageIntro } from "@/components/sections/PageIntro";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { DocumentsResponse } from "@/types/api";

function formatSize(size: number) {
  if (size > 1_000_000) return `${(size / 1_000_000).toFixed(2)} MB`;
  if (size > 1_000) return `${(size / 1_000).toFixed(2)} KB`;
  return `${size} B`;
}

type Notice = {
  kind: "success" | "error" | "info";
  text: string;
};

const STORAGE_KEY = "spbebot_documents_upload_unlocked";

export function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentsResponse | null>(null);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [accessCode, setAccessCode] = useState("");
  const [checkingAccess, setCheckingAccess] = useState(false);
  const [accessError, setAccessError] = useState<string | null>(null);
  const [uploadUnlocked, setUploadUnlocked] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem(STORAGE_KEY) === "true";
  });
  const [notice, setNotice] = useState<Notice | null>(null);

  useEffect(() => {
    let active = true;
    setDocumentsLoading(true);
    setDocumentsError(null);

    api
      .getDocuments()
      .then((result) => {
        if (!active) return;
        setDocuments(result);
      })
      .catch((error: Error) => {
        if (!active) return;
        setDocumentsError(error.message);
      })
      .finally(() => {
        if (!active) return;
        setDocumentsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [refreshKey]);

  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(null), 3000);
    return () => window.clearTimeout(timer);
  }, [notice]);

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      await api.uploadDocument(file);
      setUploadSuccess(`${file.name} berhasil ditambahkan ke koleksi dokumen.`);
      setNotice({ kind: "success", text: "Dokumen berhasil ditambahkan." });
      setRefreshKey((current) => current + 1);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Upload gagal.";
      setUploadError(message);
      setNotice({ kind: "error", text: message });
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleUnlock(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const key = accessCode.trim();
    if (!key) {
      setAccessError("Masukkan kunci akses terlebih dahulu.");
      setNotice({ kind: "error", text: "Kunci akses belum diisi." });
      return;
    }

    setCheckingAccess(true);
    setAccessError(null);

    try {
      const result = await api.verifyDocumentAccess(key);
      if (!result.allowed) {
        throw new Error("Kunci akses tidak valid.");
      }

      setUploadUnlocked(true);
      window.localStorage.setItem(STORAGE_KEY, "true");
      setAccessCode("");
      setNotice({ kind: "success", text: "Akses upload dibuka." });
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Kunci akses tidak valid.";
      setAccessError(message);
      setNotice({ kind: "error", text: message });
      setUploadUnlocked(false);
      window.localStorage.removeItem(STORAGE_KEY);
    } finally {
      setCheckingAccess(false);
    }
  }

  function handleRelock() {
    setUploadUnlocked(false);
    window.localStorage.removeItem(STORAGE_KEY);
    setAccessError(null);
    setNotice({ kind: "info", text: "Akses upload dikunci kembali." });
  }

  return (
    <div className="relative space-y-8">
      {notice ? (
        <div
          className={`fixed right-4 top-4 z-50 max-w-sm rounded-2xl border px-4 py-3 text-sm shadow-[var(--shadow)] backdrop-blur-xl ${
            notice.kind === "success"
              ? "border-emerald-200 bg-emerald-50/95 text-emerald-900"
              : notice.kind === "error"
                ? "border-rose-200 bg-rose-50/95 text-rose-900"
                : "border-sky-200 bg-sky-50/95 text-sky-900"
          }`}
        >
          <div className="flex items-start gap-3">
            {notice.kind === "error" ? (
              <CircleAlert className="mt-0.5 h-4 w-4 shrink-0" />
            ) : notice.kind === "success" ? (
              <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" />
            ) : (
              <LockKeyhole className="mt-0.5 h-4 w-4 shrink-0" />
            )}
            <p className="leading-6">{notice.text}</p>
          </div>
        </div>
      ) : null}

      <PageIntro
        eyebrow="Koleksi dokumen"
        title="Kumpulan dokumen SPBE yang dipakai sebagai sumber utama."
        description="Daftar dokumen bisa dilihat publik, sementara penambahan dokumen dibuka setelah kunci akses valid dimasukkan."
      />

      <section className="rounded-[32px] border border-[var(--line)] bg-[var(--surface-strong)] p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Akses upload</p>
            <p className="max-w-2xl text-sm leading-7 text-[var(--foreground)]">
              Masukkan kunci akses untuk membuka upload dokumen. Status ini disimpan di browser agar tidak perlu
              diulang terus saat sesi masih sama.
            </p>
          </div>
          <div className="rounded-full border border-[var(--line)] bg-white/70 px-4 py-2 text-xs uppercase tracking-[0.2em] text-[var(--muted)]">
            {uploadUnlocked ? "Upload terbuka" : "Upload terkunci"}
          </div>
        </div>

        {!uploadUnlocked ? (
          <form onSubmit={handleUnlock} className="mt-6 max-w-xl space-y-4">
            <div className="space-y-2">
              <label className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]" htmlFor="document-access-key">
                Kunci akses
              </label>
              <Input
                id="document-access-key"
                type="password"
                value={accessCode}
                onChange={(event) => setAccessCode(event.target.value)}
                placeholder="Masukkan kunci untuk membuka upload"
                autoComplete="off"
              />
            </div>
            {accessError ? <p className="text-sm text-[var(--accent)]">{accessError}</p> : null}
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="accent" type="submit" disabled={checkingAccess}>
                {checkingAccess ? "Memeriksa..." : "Buka upload"}
              </Button>
              <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
                Kunci benar akan membuka kontrol upload.
              </p>
            </div>
          </form>
        ) : (
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Button variant="outline" onClick={handleRelock}>
              Kunci ulang
            </Button>
            <p className="text-sm text-[var(--muted)]">Upload aktif. Kamu bisa menambah dokumen baru kapan saja.</p>
          </div>
        )}
      </section>

      <section className="relative overflow-hidden rounded-[36px] border border-[var(--line)] bg-[var(--surface)] p-6">
        {!uploadUnlocked ? (
          <div className="absolute inset-0 z-10 rounded-[36px] bg-white/18 backdrop-blur-[10px]" />
        ) : null}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Kelola dokumen</p>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-[var(--foreground)]">
              Upload file PDF, Markdown, atau TXT untuk menambah koleksi dokumen SPBE.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <label
              className={`inline-flex items-center rounded-full border px-5 py-3 text-sm font-medium transition ${
                uploadUnlocked
                  ? "cursor-pointer border-[var(--line)] bg-white/80 hover:border-[var(--foreground)]"
                  : "cursor-not-allowed border-[var(--line)] bg-white/45 text-[var(--muted)]"
              }`}
            >
              Pilih file
              <input
                type="file"
                accept=".pdf,.md,.txt"
                className="hidden"
                onChange={handleUpload}
                disabled={!uploadUnlocked}
              />
            </label>
            <Button variant="outline" onClick={() => setRefreshKey((current) => current + 1)}>
              Refresh list
            </Button>
          </div>
        </div>
        <div className="relative z-20">
          {uploading ? <p className="mt-4 text-sm text-[var(--muted)]">Mengunggah dokumen...</p> : null}
          {uploadSuccess ? <p className="mt-4 text-sm text-[var(--teal)]">{uploadSuccess}</p> : null}
          {uploadError ? <p className="mt-4 text-sm text-[var(--accent)]">{uploadError}</p> : null}
        </div>
      </section>

      {documentsLoading ? <div className="text-sm text-[var(--muted)]">Memuat dokumen...</div> : null}
      {documentsError ? <div className="text-sm text-[var(--accent)]">{documentsError}</div> : null}

      {documents ? (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">{documents.total} files indexed</p>
          </div>
          <div className="grid gap-4">
            {documents.items.map((item) => (
              <article
                key={item.path}
                className="grid gap-4 rounded-[30px] border border-[var(--line)] bg-[var(--surface)] p-6 md:grid-cols-[0.28fr_0.72fr]"
              >
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">{item.content_type}</p>
                  <h3 className="text-2xl font-medium tracking-[-0.04em]">{item.name}</h3>
                  <div className="space-y-1 text-sm text-[var(--muted)]">
                    <p>{formatSize(item.size_bytes)}</p>
                    {item.page_count ? <p>{item.page_count} halaman</p> : null}
                    <p>{item.path}</p>
                  </div>
                </div>
                <div className="border-t border-[var(--line)] pt-4 md:border-l md:border-t-0 md:pl-6 md:pt-0">
                  <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">Preview</p>
                  <p className="mt-3 text-sm leading-7 text-[var(--foreground)]">
                    {item.preview ?? "Preview belum tersedia untuk jenis file ini."}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
