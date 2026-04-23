from __future__ import annotations

import re
import json
from pathlib import Path
from collections import Counter
from functools import cached_property, lru_cache

import networkx as nx
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.services.vector_service import VectorService


# Batas maksimum node yang dikirim saat full=True.
# Node diprioritaskan berdasarkan degree (koneksi terbanyak) agar
# subgraph yang paling informatif tetap tersedia tanpa membebani browser.
MAX_FULL_GRAPH_NODES = 700

DOMAIN_CONFIG = [
    ("D1", "Kebijakan", ["A1", "A2"]),
    ("D2", "Tata Kelola", ["A3", "A4"]),
    ("D3", "Manajemen", ["A5", "A6"]),
    ("D4", "Layanan", ["A7", "A8"]),
]

ASPECT_CONFIG = [
    ("A1", "Kebijakan Internal Tata Kelola SPBE", 10),
    ("A2", "Perencanaan Strategis SPBE", 4),
    ("A3", "Teknologi Informasi dan Komunikasi", 4),
    ("A4", "Penyelenggara SPBE", 2),
    ("A5", "Penerapan Manajemen SPBE", 8),
    ("A6", "Pelaksanaan Audit TIK", 3),
    ("A7", "Layanan Administrasi Pemerintahan Berbasis Elektronik", 9),
    ("A8", "Layanan Publik Berbasis Elektronik", 7),
]

NODE_COLORS = {
    "root": "#0f172a",
    "domain": "#b42318",
    "aspect": "#0f766e",
    "indicator": "#1d4ed8",
    "document": "#7c3aed",
    "question": "#475569",
    "spbe": "#0f172a",
    "bab_pedoman": "#9a3412",
    "poin_pedoman": "#a16207",
    "indeks": "#7c2d12",
    "kuesioner": "#334155",
    "deskripsi_indikator": "#0369a1",
    "contoh_bukti_dukung": "#6d28d9",
    "level": "#047857",
    "kriteria_level": "#0f766e",
    "kriteria_pemenuhan_level": "#0e7490",
    "kriteria_bukti_dukung": "#4338ca",
    "ketentuan_penilaian": "#be123c",
    "contoh_kaidah": "#9333ea",
    "kriteria_kaidah": "#4f46e5",
    "entity": "#475569",
}

QUERY_CODE_PATTERN = re.compile(r"\b(?:D\d+|A\d+|ID-\d+)\b", re.IGNORECASE)
CATEGORY_BOOSTS = {
    "root": 6.0,
    "spbe": 6.0,
    "domain": 5.0,
    "aspek": 4.0,
    "aspect": 4.0,
    "indikator": 3.0,
    "indicator": 3.0,
    "level": 2.0,
    "document": 1.0,
    "question": 1.0,
}

@lru_cache(maxsize=1)
def _load_exported_graph_cached(path_str: str) -> nx.MultiDiGraph | None:
    path = Path(path_str)
    if not path.exists():
        return None

    payload = json.loads(path.read_text(encoding="utf-8"))
    graph = nx.MultiDiGraph()

    for node in payload.get("nodes", []):
        graph.add_node(
            node["id"],
            label=node.get("label") or node["id"],
            category=node.get("category", "entity"),
            description=node.get("description", ""),
            size=float(node.get("size", 1.0)),
            color=node.get("color") or NODE_COLORS["entity"],
        )

    for edge in payload.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target or source not in graph or target not in graph:
            continue
        graph.add_edge(
            source,
            target,
            key=edge.get("id"),
            label=edge.get("label", "RELATED_TO"),
        )

    return graph



class GraphService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.exported_graph_path = self._resolve_exported_graph_path()
        self.vector_service = VectorService() if self.settings.pinecone_api_key else None
        self.llm = None
        if self.settings.groq_api_key:
            self.llm = ChatGroq(
                model_name=self.settings.groq_model_name,
                temperature=0,
                groq_api_key=self.settings.groq_api_key,
            )

    def _resolve_exported_graph_path(self) -> Path:
        candidates = [
            self.settings.api_dir / "api" / "data" / "neo4j_graph.json",
            self.settings.api_dir / "app" / "data" / "neo4j_graph.json",
            self.settings.app_root / "app" / "data" / "neo4j_graph.json",
            self.settings.app_root / "data" / "neo4j_graph.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    def _load_exported_graph(self) -> nx.MultiDiGraph | None:
        return _load_exported_graph_cached(str(self.exported_graph_path.resolve()))

    @cached_property
    def indicator_details(self) -> dict[int, str]:
        pedoman_path = self.settings.data_dir / "pedoman_spbe.md"
        if not pedoman_path.exists():
            return {}

        text = pedoman_path.read_text(encoding="utf-8", errors="ignore")
        pattern = re.compile(r"(?ms)^### INDIKATOR (\d+)\s*(.*?)(?=^### INDIKATOR \d+|\Z)")
        details: dict[int, str] = {}

        for match in pattern.finditer(text):
            number = int(match.group(1))
            block = re.sub(r"\s+", " ", match.group(2)).strip()
            details[number] = block[:900]

        return details

    @cached_property
    def pretest_questions(self) -> list[dict]:
        question_path = self.settings.data_dir / "SOAL PRETEST SPBE.md"
        if not question_path.exists():
            return []

        text = question_path.read_text(encoding="utf-8", errors="ignore")
        pattern = re.compile(r"(?ms)^# Soal (\d+):\s*(.*?)\n\n(.*?)(?=^# Soal \d+|\Z)")
        questions: list[dict] = []
        for match in pattern.finditer(text):
            number = int(match.group(1))
            topic = match.group(2).strip()
            body = re.sub(r"\s+", " ", match.group(3)).strip()
            questions.append(
                {
                    "id": f"question-{number}",
                    "label": f"Soal {number}",
                    "topic": topic,
                    "description": body[:500],
                }
            )
        return questions

    @cached_property
    def graph(self) -> nx.MultiDiGraph:
        exported_graph = self._load_exported_graph()
        if exported_graph is not None:
            return exported_graph

        graph = nx.MultiDiGraph()
        graph.add_node(
            "spbe",
            label="SPBE",
            category="root",
            description="Sistem Pemerintahan Berbasis Elektronik",
            size=3.2,
            color=NODE_COLORS["root"],
        )

        aspect_lookup = {code: {"name": name, "count": count} for code, name, count in ASPECT_CONFIG}

        for code, name, aspects in DOMAIN_CONFIG:
            domain_id = f"domain-{code.lower()}"
            graph.add_node(
                domain_id,
                label=f"{code} {name}",
                category="domain",
                description=f"Domain {name} dalam pemantauan dan evaluasi SPBE.",
                size=2.4,
                color=NODE_COLORS["domain"],
            )
            graph.add_edge("spbe", domain_id, label="memiliki_domain")

            indicator_number = 1 + sum(
                aspect_lookup[aspect_code]["count"]
                for aspect_code, _, _ in ASPECT_CONFIG
                if aspect_code < aspects[0]
            )

            for aspect_code in aspects:
                aspect_info = aspect_lookup[aspect_code]
                aspect_id = f"aspect-{aspect_code.lower()}"
                graph.add_node(
                    aspect_id,
                    label=f"{aspect_code} {aspect_info['name']}",
                    category="aspect",
                    description=f"Aspek {aspect_info['name']} dengan {aspect_info['count']} indikator.",
                    size=1.8,
                    color=NODE_COLORS["aspect"],
                )
                graph.add_edge(domain_id, aspect_id, label="mencakup_aspek")

                for _ in range(aspect_info["count"]):
                    detail = self.indicator_details.get(indicator_number, "")
                    indicator_id = f"indicator-id-{indicator_number}"
                    graph.add_node(
                        indicator_id,
                        label=f"ID-{indicator_number}",
                        category="indicator",
                        description=detail or f"Indikator {indicator_number} pada {aspect_info['name']}.",
                        size=1.1,
                        color=NODE_COLORS["indicator"],
                    )
                    graph.add_edge(aspect_id, indicator_id, label="memiliki_indikator")
                    indicator_number += 1

        graph.add_node(
            "doc-pedoman",
            label="Pedoman SPBE 2024",
            category="document",
            description="Dokumen pedoman utama evaluasi SPBE tahun 2024.",
            size=1.8,
            color=NODE_COLORS["document"],
        )
        graph.add_edge("spbe", "doc-pedoman", label="dirujuk_oleh")

        for number in self.indicator_details:
            indicator_id = f"indicator-id-{number}"
            if graph.has_node(indicator_id):
                graph.add_edge(indicator_id, "doc-pedoman", label="terdokumentasi_di")

        for question in self.pretest_questions:
            graph.add_node(
                question["id"],
                label=f"{question['label']} · {question['topic']}",
                category="question",
                description=question["description"],
                size=1.0,
                color=NODE_COLORS["question"],
            )
            graph.add_edge("spbe", question["id"], label="diuji_dengan")

        return graph

    def export_graph(
        self,
        node_ids: set[str] | None = None,
        limit: int | None = MAX_FULL_GRAPH_NODES,
    ) -> dict:
        graph = self.graph
        if node_ids:
            subgraph = graph.subgraph(node_ids).copy()
        else:
            # Mode full: ambil node berdasarkan degree tertinggi agar
            # subgraph paling konektif yang muncul, bukan seluruh 1800+ node.
            if limit and graph.number_of_nodes() > limit:
                top_nodes = sorted(
                    graph.nodes(),
                    key=lambda n: graph.degree(n),
                    reverse=True,
                )[:limit]
                subgraph = graph.subgraph(top_nodes).copy()
            else:
                subgraph = graph

        nodes = []
        for node_id, data in subgraph.nodes(data=True):
            nodes.append(
                {
                    "id": node_id,
                    "label": data["label"],
                    "category": data["category"],
                    "description": (data.get("description") or "")[:220],
                    "size": data.get("size", 1.0),
                    "color": data["color"],
                }
            )

        edges = []
        for source, target, key, data in subgraph.edges(keys=True, data=True):
            edges.append(
                {
                    "id": str(key) if key is not None else f"{source}->{target}",
                    "source": source,
                    "target": target,
                    "label": data["label"],
                }
            )

        categories = Counter(node["category"] for node in nodes)
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "nodes": len(nodes),
                "edges": len(edges),
                "domains": categories.get("domain", 0),
                "aspects": categories.get("aspect", 0) + categories.get("aspek", 0),
                "indicators": categories.get("indicator", 0) + categories.get("indikator", 0),
                "total_nodes_in_graph": graph.number_of_nodes(),
            },
        }

    def get_stats(self) -> dict:
        """Endpoint ringan untuk mengambil statistik graph tanpa data node/edge."""
        graph = self.graph
        categories = Counter(
            data.get("category", "entity")
            for _, data in graph.nodes(data=True)
        )
        return {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "domains": categories.get("domain", 0),
            "aspects": categories.get("aspect", 0) + categories.get("aspek", 0),
            "indicators": categories.get("indicator", 0) + categories.get("indikator", 0),
            "max_full_graph_nodes": MAX_FULL_GRAPH_NODES,
        }

    def export_overview_graph(self, indicators_per_aspect: int = 3) -> dict:
        graph = self.graph
        node_ids: set[str] = set()

        root_candidates = [
            node_id
            for node_id, data in graph.nodes(data=True)
            if data.get("category") in {"root", "spbe"} or data.get("label") == "SPBE"
        ]
        root_id = root_candidates[0] if root_candidates else None
        if root_id:
            node_ids.add(root_id)

        max_domains = 16
        max_documents = 36

        domain_candidates = [
            node_id
            for node_id, data in graph.nodes(data=True)
            if data.get("category") == "domain"
        ]

        domain_ids: list[str] = []
        if root_id:
            connected_domains = [
                target
                for target in graph.successors(root_id)
                if graph.nodes[target].get("category") == "domain"
            ]
            domain_ids.extend(connected_domains)

        if len(domain_ids) < max_domains:
            remaining = [domain for domain in domain_candidates if domain not in domain_ids]
            remaining.sort(key=lambda nid: graph.degree(nid), reverse=True)
            domain_ids.extend(remaining[: max_domains - len(domain_ids)])

        domain_ids = domain_ids[:max_domains]
        node_ids.update(domain_ids)

        aspect_ids: set[str] = set()
        for domain_id in domain_ids:
            for target in graph.successors(domain_id):
                if graph.nodes[target].get("category") in {"aspect", "aspek"}:
                    aspect_ids.add(target)

        node_ids.update(aspect_ids)

        selected_indicators: set[str] = set()
        for aspect_id in aspect_ids:
            indicators = [
                target
                for _, target in graph.out_edges(aspect_id)
                if graph.nodes[target].get("category") in {"indicator", "indikator"}
            ]
            indicators.sort(key=lambda nid: graph.degree(nid), reverse=True)
            for indicator_id in indicators[:indicators_per_aspect]:
                selected_indicators.add(indicator_id)
                node_ids.add(indicator_id)

        linked_documents: list[str] = []
        for indicator_id in selected_indicators:
            for target in graph.successors(indicator_id):
                if graph.nodes[target].get("category") == "document":
                    linked_documents.append(target)

        seen_documents: set[str] = set()
        ordered_documents: list[str] = []
        for document_id in linked_documents:
            if document_id in seen_documents:
                continue
            seen_documents.add(document_id)
            ordered_documents.append(document_id)

        if len(ordered_documents) < max_documents:
            document_candidates = [
                node_id
                for node_id, data in graph.nodes(data=True)
                if data.get("category") == "document" and node_id not in seen_documents
            ]
            document_candidates.sort(key=lambda nid: graph.degree(nid), reverse=True)
            ordered_documents.extend(document_candidates[: max_documents - len(ordered_documents)])

        node_ids.update(ordered_documents[:max_documents])

        return self.export_graph(node_ids=node_ids)

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"[a-zA-Z0-9\-]+", text.lower()))

    @staticmethod
    def _extract_codes(text: str) -> set[str]:
        return {match.group(0).lower() for match in QUERY_CODE_PATTERN.finditer(text)}

    def rewrite_graph_query(self, question: str) -> str:
        """
        Ubah pertanyaan user menjadi query singkat yang lebih cocok untuk
        pencarian node graph, bukan teks mentah percakapan.
        """
        base_codes = sorted(self._extract_codes(question))
        question_lower = question.lower()

        # Heuristik fallback bila LLM tidak tersedia.
        keyword_map = [
            ("audit tik", "A6 audit tik"),
            ("teknologi informasi dan komunikasi", "A3 teknologi informasi dan komunikasi"),
            ("layanan publik", "A8 layanan publik"),
            ("layanan administrasi", "A7 layanan administrasi"),
            ("kebijakan internal", "A1 kebijakan internal"),
            ("perencanaan strategis", "A2 perencanaan strategis"),
            ("penerapan manajemen", "A5 penerapan manajemen"),
            ("penyelenggara", "A4 penyelenggara spbe"),
            ("domain layanan", "D4 layanan"),
            ("domain kebijakan", "D1 kebijakan"),
            ("domain tata kelola", "D2 tata kelola"),
            ("domain manajemen", "D3 manajemen"),
        ]

        heuristic_terms: list[str] = []
        for needle, replacement in keyword_map:
            if needle in question_lower:
                heuristic_terms.append(replacement)

        if base_codes:
            heuristic_terms.extend(base_codes)

        if heuristic_terms:
            return " ".join(dict.fromkeys(heuristic_terms))

        if self.llm is None:
            return question

        prompt = PromptTemplate.from_template(
            """Ubah pertanyaan pengguna menjadi query pendek untuk pencarian node knowledge graph SPBE.

Aturan:
- Output hanya query singkat, tanpa penjelasan tambahan.
- Maksimal 8 kata.
- Gunakan istilah node yang cocok seperti D1, D2, D3, D4, A1, A2, A3, A4, A5, A6, A7, A8, SPBE, domain, aspek, indikator, audit TIK, layanan, tata kelola, manajemen, kebijakan.
- Jika ada kode node yang relevan, prioritaskan kode itu.

Pertanyaan: {question}

Query:"""
        )

        chain = prompt | self.llm | StrOutputParser()
        try:
            rewritten = chain.invoke({"question": question}).strip()
        except Exception:
            return question

        rewritten = rewritten.splitlines()[0].strip().strip('"').strip("'")
        return rewritten or question

    @cached_property
    def searchable_nodes(self) -> list[tuple[str, set[str], dict]]:
        searchable: list[tuple[str, set[str], dict]] = []
        for node_id, data in self.graph.nodes(data=True):
            haystack = f"{data.get('label', '')} {data.get('description', '')}"
            searchable.append((node_id, self._tokenize(haystack), data))
        return searchable

    def search(self, query: str, limit: int = 18) -> dict:
        query_tokens = self._tokenize(query)
        query_codes = self._extract_codes(query)
        query_lower = query.strip().lower()
        matched: list[dict] = []

        for node_id, tokens, data in self.searchable_nodes:
            overlap = len(tokens & query_tokens)
            if overlap <= 0 and not query_codes and query_lower not in node_id.lower() and query_lower not in str(data.get("label", "")).lower():
                continue

            node_label = str(data.get("label", ""))
            node_label_lower = node_label.lower()
            node_id_lower = node_id.lower()
            node_codes = self._extract_codes(f"{node_id} {node_label}")

            score = float(overlap)
            score += CATEGORY_BOOSTS.get(str(data.get("category", "")).lower(), 0.0)

            if query_lower and query_lower == node_label_lower:
                score += 8.0

            if query_lower and (query_lower in node_label_lower or node_label_lower in query_lower):
                score += 3.0

            if query_lower and (query_lower == node_id_lower or query_lower in node_id_lower or node_id_lower in query_lower):
                score += 10.0

            if query_codes and node_codes & query_codes:
                score += 12.0

            if query_codes and str(data.get("category", "")).lower() == "document":
                score -= 3.0

            if score <= 0:
                continue

            matched.append(
                {
                    "id": node_id,
                    "label": data["label"],
                    "category": data["category"],
                    "description": (data.get("description") or "")[:220],
                    "score": score,
                }
            )

        matched.sort(key=lambda item: item["score"], reverse=True)
        matched = matched[:limit]

        node_ids: set[str] = {"spbe"}
        for item in matched[:8]:
            node_ids.add(item["id"])
            node_ids.update(self.graph.predecessors(item["id"]))
            node_ids.update(self.graph.successors(item["id"]))

        return {
            "query": query,
            "graph": self.export_graph(node_ids=node_ids),
            "related_items": matched,
        }

    @staticmethod
    def _format_graph_context(items: list[dict]) -> str:
        if not items:
            return "Tidak ada node graph yang cukup relevan."

        return "\n".join(
            f"- {item['label']} [{item['category']}]: {item['description']}"
            for item in items[:4]
        )

    @staticmethod
    def _format_vector_context(items: list[dict]) -> str:
        if not items:
            return "Tidak ada hasil Pinecone yang cukup relevan."

        return "\n".join(
            f"- {item['title']} [{item['source']}]: {item['excerpt']}"
            for item in items[:4]
        )

    def _build_hybrid_context(self, question: str) -> tuple[str, list[dict]]:
        graph_query = self.rewrite_graph_query(question)
        graph_result = self.search(graph_query)
        graph_items = graph_result["related_items"][:6]

        vector_items: list[dict] = []
        if self.vector_service is not None:
            vector_items = self.vector_service.search(question, top_k=4)

        combined_sources: list[dict] = []
        seen_keys: set[str] = set()

        for item in graph_items:
            key = f"graph:{item['id']}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            combined_sources.append(
                {
                    "id": item["id"],
                    "title": item["label"],
                    "source": "knowledge-graph",
                    "score": round(float(item["score"]), 3),
                    "excerpt": item["description"],
                }
            )

        for item in vector_items:
            key = f"pinecone:{item['id']}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            combined_sources.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "source": item["source"],
                    "score": round(float(item["score"]), 3),
                    "excerpt": item["excerpt"],
                }
            )

        context = (
            "Knowledge graph nodes:\n"
            f"{self._format_graph_context(graph_items)}\n\n"
            "Pinecone embeddings:\n"
            f"{self._format_vector_context(vector_items)}"
        )

        return context, combined_sources

    def answer(self, question: str) -> dict:
        context, combined_sources = self._build_hybrid_context(question)
        related = combined_sources[:5]

        if not related:
            answer = (
                "Knowledge graph lokal belum menemukan node yang cukup relevan untuk pertanyaan tersebut. "
                "Coba gunakan kode seperti D1, A5, atau ID-32."
            )
        else:
            if self.llm is not None:
                prompt = PromptTemplate.from_template(
                    """Anda adalah asisten SPBE yang menjawab berdasarkan knowledge graph dan Pinecone embeddings.

Gunakan prioritas berikut:
1. Knowledge graph untuk struktur domain, aspek, indikator, dan relasi.
2. Pinecone untuk detail dokumen, penjelasan, dan kutipan pendukung.

Konteks gabungan:
{context}

Tugas:
- Jawab pertanyaan pengguna secara langsung, ringkas, dan jelas.
- Jika graph dan Pinecone mendukung jawaban yang sama, rangkum menjadi satu jawaban final.
- Jika keduanya belum cukup, sebutkan apa yang belum ditemukan dan sarankan kata kunci yang lebih spesifik.
- Jangan hanya mengulang daftar sumber.

Pertanyaan: {question}

Jawaban:"""
                )
                chain = prompt | self.llm | StrOutputParser()
                try:
                    answer = chain.invoke({"context": context, "question": question})
                except Exception as exc:
                    answer = (
                        "Saya menemukan konteks graph, tetapi gagal memanggil LLM untuk menyusun jawaban akhir. "
                        f"Detail error: {exc}"
                    )
            else:
                answer = (
                    "Saya menemukan konteks dari knowledge graph dan Pinecone, tetapi LLM belum tersedia untuk menyusun jawaban akhir.\n\n"
                    f"{context}"
                )

        return {
            "mode": "hybrid",
            "question": question,
            "answer": answer,
            "sources": related,
            "follow_up_suggestions": [
                "Tampilkan subgraph untuk Domain Layanan.",
                "Apa indikator yang terkait audit TIK?",
                "Cari node terkait indeks SPBE nasional.",
            ],
        }
