# API

FastAPI backend untuk SPBEBOT.

## Stack

- FastAPI
- Python 3.11
- NetworkX untuk graph lokal berbasis JSON
- pypdf untuk metadata dokumen
- Vercel Blob (opsional) untuk storage dokumen production

## Menjalankan

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Sumber Graph Tanpa Neo4j Runtime

- API membaca file `app/data/neo4j_graph.json`, jadi runtime tidak perlu Docker/Neo4j.
- Jika ingin regenerate graph dari backup Neo4j, pakai script export satu kali:

```bash
pip install -r requirements-export.txt
python scripts/export_neo4j_graph.py
```

## Catatan

- File `.env` untuk API ini sudah dipisah agar hanya variabel yang dipakai.
- Visualisasi knowledge graph baru tidak lagi membutuhkan compute Neo4j cloud.
- Upload dokumen otomatis ke Vercel Blob jika `BLOB_READ_WRITE_TOKEN` tersedia, dan fallback ke local filesystem jika token belum ada.

## Deploy Vercel (API)

- Folder `SPBEBOT-App/API` sudah disiapkan untuk Vercel serverless dengan `index.py` dan `vercel.json`.
- Saat create project di Vercel:
  - Root Directory: `SPBEBOT-App/API`
  - Build Command: kosongkan (default)
  - Install Command: `pip install -r requirements.txt`
- Set environment variable yang dibutuhkan:
  - `GROQ_API_KEY` (jika fitur LLM dipakai)
  - `BLOB_READ_WRITE_TOKEN` (untuk storage dokumen)
  - `BLOB_ACCESS` = `private` atau `public` (opsional, default `private`)
  - `BLOB_PREFIX` (opsional, default `spbebot-docs`)
  - `OLLAMA_API_KEY` (untuk Ollama Cloud)
