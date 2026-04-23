# SPBEBOT 🤖

SPBEBOT adalah Sistem Pemerintahan Berbasis Elektronik Bot, sebuah aplikasi yang dirancang untuk memfasilitasi dan mengoptimalkan proses evaluasi dan tanya jawab terkait dokumen SPBE. Aplikasi ini menggunakan teknologi Retrieval-Augmented Generation (RAG) untuk memberikan jawaban yang akurat berdasarkan dokumen referensi.

## 🌟 Fitur Utama

- **Knowledge Graph RAG Pipeline**: Dibangun menggunakan LangGraph untuk pemrosesan dokumen yang kompleks (essay, research, bizplan).
- **Vector Search Engine**: Menggunakan Pinecone dan Cohere API untuk embedding multibahasa berkinerja tinggi.
- **AI Review Engine**: Sistem evaluasi otomatis yang memberikan umpan balik spesifik pada dokumen berdasarkan heuristik pencarian web dan analisis semantik.

## 🏗️ Struktur Proyek

Proyek ini dibagi menjadi dua bagian utama di dalam direktori `SPBEBOT-App/`:

### 1. Backend (API)
- **Lokasi**: `SPBEBOT-App/API`
- **Teknologi**: FastAPI, Python, LangGraph, Pinecone, Cohere.
- **Fungsi**: Menangani logika RAG, manajemen knowledge graph, dan integrasi API AI.

### 2. Frontend
- **Lokasi**: `SPBEBOT-App/Frontend`
- **Teknologi**: Vite, React, TypeScript, TailwindCSS.
- **Fungsi**: Antarmuka pengguna untuk berinteraksi dengan SPBEBOT, menampilkan visualisasi knowledge graph, dan sistem review dokumen.

## 🚀 Cara Menjalankan Secara Lokal

### Prasyarat
- Python 3.9+
- Node.js & npm
- Akun Pinecone & Cohere untuk API Keys

### Setup Backend
1. Masuk ke direktori API: `cd SPBEBOT-App/API`
2. Buat virtual environment: `python -m venv .venv`
3. Aktivasi virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Instal dependensi: `pip install -r requirements.txt`
5. Konfigurasi `.env` dengan kredensial yang dibutuhkan.
6. Jalankan server: `uvicorn app.main:app --reload` (atau melalui script yang tersedia).

### Setup Frontend
1. Masuk ke direktori Frontend: `cd SPBEBOT-App/Frontend`
2. Instal dependensi: `npm install`
3. Konfigurasi `.env` sesuai `.env.example`.
4. Jalankan development server: `npm run dev`

## ☁️ Deployment
Proyek ini dikonfigurasi untuk dapat dideploy pada platform cloud native seperti **Vercel** (untuk FastAPI dan Vite Frontend).
