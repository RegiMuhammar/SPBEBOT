from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContentRepository:
    def get_overview(self) -> dict:
        return {
            "hero": {
                "eyebrow": "Tentang SPBEBOT",
                "title": "Ruang bantu untuk membaca, menelusuri, dan merangkum informasi SPBE.",
                "description": (
                    "SPBEBOT dirancang untuk membantu pengguna memahami pedoman SPBE, menelusuri "
                    "dokumen, melihat keterkaitan antar unsur, dan mengambil ringkasan yang relevan "
                    "dengan cepat."
                ),
                "highlights": [
                    "Cari informasi SPBE dari dokumen dan pertanyaan yang lebih spesifik.",
                    "Lihat hubungan antara domain, aspek, indikator, dan penilaian.",
                    "Baca ringkasan temuan untuk mempercepat pemahaman konteks.",
                ],
            },
            "sections": [
                {
                    "title": "Tentang SPBE",
                    "body": (
                        "SPBE adalah penyelenggaraan pemerintahan berbasis elektronik untuk "
                        "mewujudkan layanan yang lebih efektif, transparan, akuntabel, dan terhubung."
                    ),
                },
                {
                    "title": "Apa yang dibantu",
                    "body": (
                        "Aplikasi ini membantu membaca dokumen, menelusuri hubungan konsep, "
                        "menyusun jawaban singkat, dan memudahkan eksplorasi hasil evaluasi."
                    ),
                },
                {
                    "title": "Kenapa penting",
                    "body": (
                        "Semua informasi yang sering dicari ditempatkan dalam satu ruang agar "
                        "proses memahami SPBE jadi lebih cepat dan tidak berpindah-pindah."
                    ),
                },
            ],
            "quick_facts": [
                {"label": "Domain", "value": "4"},
                {"label": "Aspek", "value": "8"},
                {"label": "Indikator", "value": "47"},
                {"label": "Sumber utama", "value": "Pedoman Menteri PANRB No. 3/2024"},
            ],
        }

    def get_prompt_templates(self) -> list[dict]:
        return [
            {
                "id": "general",
                "title": "Penjelasan Umum SPBE",
                "prompt": (
                    "Berikan penjelasan umum tentang Sistem Pemerintahan Berbasis Elektronik "
                    "(SPBE), termasuk definisi, tujuan, dan manfaatnya."
                ),
            },
            {
                "id": "components",
                "title": "Komponen SPBE",
                "prompt": (
                    "Jelaskan komponen-komponen utama dalam SPBE dan bagaimana keterkaitan antar "
                    "komponen tersebut."
                ),
            },
            {
                "id": "policy",
                "title": "Kebijakan SPBE",
                "prompt": (
                    "Berikan informasi tentang kebijakan dan regulasi terkait SPBE, termasuk "
                    "peraturan perundang-undangan yang mengaturnya."
                ),
            },
            {
                "id": "indicator",
                "title": "Indikator Penilaian SPBE",
                "prompt": (
                    "Jelaskan indikator-indikator yang digunakan dalam penilaian SPBE dan "
                    "bagaimana cara mengukurnya."
                ),
            },
            {
                "id": "implementation",
                "title": "Implementasi SPBE",
                "prompt": (
                    "Berikan panduan langkah-langkah implementasi SPBE di instansi pemerintah."
                ),
            },
        ]

    def get_dashboard(self) -> dict:
        return {
            "total_index": 3.47,
            "domains": [
                {"code": "D1", "name": "Kebijakan", "value": 3.52},
                {"code": "D2", "name": "Tata Kelola", "value": 3.65},
                {"code": "D3", "name": "Manajemen", "value": 3.40},
                {"code": "D4", "name": "Layanan", "value": 3.31},
            ],
            "aspects": [
                {"code": "A1", "name": "Kebijakan Internal Tata Kelola SPBE", "indicator_count": 10},
                {"code": "A2", "name": "Perencanaan Strategis SPBE", "indicator_count": 4},
                {"code": "A3", "name": "Teknologi Informasi dan Komunikasi", "indicator_count": 4},
                {"code": "A4", "name": "Penyelenggara SPBE", "indicator_count": 2},
                {"code": "A5", "name": "Penerapan Manajemen SPBE", "indicator_count": 8},
                {"code": "A6", "name": "Pelaksanaan Audit TIK", "indicator_count": 3},
                {"code": "A7", "name": "Layanan Administrasi Pemerintahan Berbasis Elektronik", "indicator_count": 9},
                {"code": "A8", "name": "Layanan Publik Berbasis Elektronik", "indicator_count": 7},
            ],
        }

    def get_research_results(self) -> dict:
        return {
            "summary": (
                "Evaluasi membandingkan dua pendekatan RAG untuk menjawab pertanyaan SPBE. "
                "Nilai di bawah merepresentasikan dataset riset yang dipakai untuk mendukung "
                "evaluasi dan pengembangan aplikasi."
            ),
            "metrics": [
                {"metric": "Context Recall", "system_1": 0.85, "system_2": 0.79},
                {"metric": "Context Precision", "system_1": 0.78, "system_2": 0.82},
                {"metric": "Faithfulness", "system_1": 0.92, "system_2": 0.88},
                {"metric": "Answer Relevance", "system_1": 0.87, "system_2": 0.85},
                {"metric": "Answer Correctness", "system_1": 0.83, "system_2": 0.86},
            ],
            "categories": [
                {
                    "name": "Umum",
                    "questions": [
                        {"label": "Pertanyaan 1", "context_recall": 0.91, "context_precision": 0.88, "faithfulness": 0.93},
                        {"label": "Pertanyaan 2", "context_recall": 0.83, "context_precision": 0.80, "faithfulness": 0.90},
                    ],
                },
                {
                    "name": "Kebijakan",
                    "questions": [
                        {"label": "Pertanyaan 1", "context_recall": 0.89, "context_precision": 0.84, "faithfulness": 0.91},
                        {"label": "Pertanyaan 2", "context_recall": 0.81, "context_precision": 0.79, "faithfulness": 0.88},
                    ],
                },
            ],
        }
