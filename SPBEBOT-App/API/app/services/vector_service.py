from __future__ import annotations

import os
from functools import cached_property
from typing import Any, Dict, List

from langchain_cohere import CohereEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import get_settings


class VectorService:
    def __init__(self) -> None:
        self.settings = get_settings()

        # Inisialisasi model Embeddings Cohere
        self.embeddings = CohereEmbeddings(
            model="embed-multilingual-v3.0",
            cohere_api_key=self.settings.cohere_api_key,
        )
        
        # Inisialisasi model LLM Groq
        self.llm = ChatGroq(
            model_name=self.settings.groq_model_name,
            temperature=0,
            groq_api_key=self.settings.groq_api_key,
        )

    @cached_property
    def vector_store(self) -> PineconeVectorStore | None:
        if not self.settings.pinecone_api_key:
            return None
            
        # Menggunakan PineconeVectorStore dari langchain_pinecone
        import os
        os.environ["PINECONE_API_KEY"] = self.settings.pinecone_api_key
        
        return PineconeVectorStore(
            index_name=self.settings.pinecone_index_name,
            embedding=self.embeddings
        )

    def search(self, question: str, top_k: int = 4) -> List[Dict[str, Any]]:
        if not self.vector_store:
            return []
            
        try:
            # Lakukan similarity search ke Pinecone
            docs_and_scores = self.vector_store.similarity_search_with_score(question, k=top_k)
            
            scored: List[Dict[str, Any]] = []
            for i, (doc, score) in enumerate(docs_and_scores):
                # Menyiapkan data hasil pencarian yang sesuai schema lama
                excerpt = doc.page_content[:320].replace("\n", " ")
                
                # Pinecone terkadang mengembalikan metadata unik berdasarkan data asal
                title = doc.metadata.get("title") or doc.metadata.get("source") or f"Dokumen {i+1}"
                source = doc.metadata.get("source", "Korpus SPBE")
                doc_id = doc.metadata.get("id") or str(i)
                
                scored.append(
                    {
                        "id": doc_id,
                        "title": title,
                        "source": source,
                        "score": round(float(score), 3),
                        "excerpt": excerpt,
                        "content": doc.page_content,
                    }
                )
            return scored
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error dalam Vector Search: {e}")
            return []

    def answer(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        results = self.search(question, top_k=top_k)

        if not results:
            return {
                "mode": "vector",
                "question": question,
                "answer": (
                    "Saya belum menemukan potongan dokumen yang cukup relevan dari sistem Pinecone RAG. "
                    "Pastikan Pinecone sudah dikonfigurasi dan diisi dengan vektor dokumen."
                ),
                "sources": [],
                "follow_up_suggestions": [
                    "Apa indikator untuk domain layanan?",
                    "Jelaskan indeks SPBE nasional 2021-2023.",
                    "Apa tujuan evaluasi SPBE?",
                ],
            }

        # Menggabungkan konten untuk dijadikan konteks bagi LLM
        context_parts = []
        source_names = set()
        
        for item in results:
            source_names.add(item["source"])
            context_parts.append(f"[Sumber: {item['title']}]\n{item['content']}")
            
        context_str = "\n\n".join(context_parts)
        
        # Menyusun template prompt untuk LLM (RAG Prompts)
        template = """Anda adalah asisten asesor SPBE yang detail dan komprehensif, khususnya dalam memberikan informasi Sistem Pemerintahan Berbasis Elektronik (SPBE) Indonesia.

Konteks dari pedoman SPBE yang ditemukan di sistem:
{context}

Berdasarkan konteks di atas, tolong jawab pertanyaan pengguna berikut. 
Jika jawaban tidak ada di konteks, katakan bahwa informasi tersebut tidak ditemukan dalam pedoman. Jawab dengan konkrit dan jelas.

Pertanyaan: {question}

Jawaban Anda:"""

        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            # Memanggil LLM GroqCloud untuk merangkum jawaban
            llm_answer = chain.invoke({"context": context_str, "question": question})
        except Exception as e:
            llm_answer = f"Maaf, terjadi kesalahan saat menghubungi LLM (Groq): {e}"

        return {
            "mode": "vector",
            "question": question,
            "answer": llm_answer,
            "sources": results,
            "follow_up_suggestions": [
                "Tampilkan domain, aspek, dan indikator yang terkait.",
                "Apa bukti dukung untuk indikator tersebut?",
                "Buat ringkasan singkat untuk asesor internal.",
            ],
        }
