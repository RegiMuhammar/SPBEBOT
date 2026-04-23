# Analisis Kelayakan Deployment SPBEBOT di Vercel

Berdasarkan pengecekan terhadap arsitektur codebase saat ini, rencana Anda untuk men-deploy aplikasi ini ke **Vercel** adalah langkah yang **sangat layak (highly feasible) dan direkomendasikan**.

Aplikasi SPBEBOT Anda kini menggunakan pendekatan arsitektur komputasi *cloud-native*. Anda telah memisahkan beban *AI engine* ke provider eksternal (Groq untuk LLM, Cohere untuk Embedding, dan Pinecone untuk Vector Database). Hal ini membuat backend FastAPI Anda menjadi "stateless" (tidak menyimpan state/data persisten secara lokal) dan sangat ideal untuk Vercel Serverless Functions.

Berikut adalah analisis teknis yang komprehensif terkait rencana tersebut.

---

## 1. Analisis Arsitektur

### ✅ Frontend (React + Vite + Tailwind)
- **Kecocokan:** 100% cocok. Vercel dibangun dengan dukungan *first-class* untuk ekosistem React dan Vite.
- **Kinerja:** Proses build (`npm run build`) dan *serving* aset statis akan didistribusikan secara otomatis melalui Edge Network global Vercel.

### ✅ Backend (FastAPI Python)
- **Kecocokan:** Sangat mendukung. File `vercel.json` dan `index.py` yang Anda miliki menunjukkan bahwa aplikasi ini sudah disiapkan menggunakan `@vercel/python` *builder*.
- **Penyimpanan Berkas (File Storage):** Pada `app/services/document_service.py`, Anda sudah menyiapkan integrasi cerdas dengan `vercel.blob`. Karena Vercel Serverless beroperasi dalam sistem file *read-only* (hanya-baca), fitur *fallback* otomatis ke Vercel Blob ini memastikan fitur unggah dokumen Anda tidak akan rusak *(crash)* saat produksi.

---

## 2. Kendala dan Perhatian Utama (Points of Concern)

Meskipun sangat layak, ada beberapa hal teknis di sisi Vercel yang perlu diwaspadai:

> [!WARNING]
> **Batas Ukuran Bundle (Serverless Function Size Limit)**
> Vercel Hobby (Gratis) memiliki batas ukuran paket tak terkompresi (*unzipped*) maksimal **250MB** per fungsi.
> Mengingat `requirements.txt` Anda berisi dependensi seperti `fastapi`, `pypdf`, `networkx`, dan ekstensi `langchain-*`, ada kemungkinan ukuran total mendekati batas ini. Sangat disarankan untuk memastikan bahwa paket-paket lama (seperti `langchain-ollama` jika tidak dipakai) dibersihkan untuk menghemat kapasitas.

> [!CAUTION]
> **Timeout Execution**
> Batas maksimum eksekusi untuk Vercel Hobby adalah **10 detik** per request (atau 60 detik jika Anda berlangganan paket Pro).
> Karena layanan AI Anda memanggil API eksternal (Groq & Cohere), pastikan latensi atau respons API eksternal tersebut konsisten di bawah 10 detik. Jika ada proses ekstraksi PDF yang sangat besar dan memakan waktu, ada risiko *Serverless Timeout*.

> [!IMPORTANT]
> **Pengaturan CORS (Cross-Origin Resource Sharing)**
> Pada file `app/core/config.py`, Anda mengunci *allowed origins* ke `localhost` dan `127.0.0.1`.
> Saat Frontend di-deploy, ia akan mendapat URL seperti `https://spbebot-frontend.vercel.app`. API Backend tidak akan bisa menerima permintaan kecuali URL tersebut ditambahkan ke daftar `allowed_origins` atau Anda menggunakan *wildcard* `*`.

---

## 3. Strategi Deployment Terbaik (Rekomendasi)

Terdapat struktur folder `Frontend` dan `API` di repositori Anda. Alih-alih memaksakan *Monorepo* yang kompleks di Vercel, strategi yang paling minim gesekan *(frictionless)* adalah men-deploynya sebagai **dua project terpisah**:

### Tahap 1: Deploy Backend (API)
1. Buat Project baru di Vercel, pilih repositori SPBEBOT.
2. Atur **Root Directory** ke folder `API`.
3. Vercel akan membaca `vercel.json` untuk mengeksekusi FastAPI.
4. Masukkan semua Environment Variables dari `.env` (seperti `GROQ_API_KEY`, `COHERE_API_KEY`, `PINECONE_API_KEY`, dan `BLOB_READ_WRITE_TOKEN`).
5. Catat URL Vercel yang dihasilkan (misal: `https://spbebot-api.vercel.app`).

### Tahap 2: Update CORS Backend
1. Kembali ke kodingan `app/core/config.py` dan perbarui `allowed_origins` untuk menerima origin dari Frontend yang akan Anda buat, atau gunakan `*` sementara untuk mempermudah.

### Tahap 3: Deploy Frontend
1. Buat Project Vercel baru lagi dari repositori yang sama.
2. Atur **Root Directory** ke folder `Frontend`.
3. Framework akan otomatis terdeteksi sebagai Vite.
4. Tambahkan Environment Variable, misal `VITE_API_URL` dengan nilai URL Backend Anda (`https://spbebot-api.vercel.app/api/v1`).
5. Selesai!

---

## Kesimpulan

Rencana Anda untuk menggunakan Vercel sudah sangat tepat dan dapat segera dieksekusi. Berkat migrasi RAG Anda baru-baru ini ke layanan cloud API (Cohere, Pinecone, Groq) serta kesiapan kode fallback Vercel Blob yang sudah tertanam di sistem Anda, transisi ini seharusnya berjalan mulus asal memperhatikan batas *Timeout* dan *Bundle Size*.
