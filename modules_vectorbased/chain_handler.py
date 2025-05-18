from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from modules_vectorbased.pdf_handler import get_vector_db
import os

PROMPT_TEMPLATE = """Anda adalah asisten asesor SPBE yang detail, khususnya dalam memberikan informasi dan membantu auditing Sistem Pemerintahan Berbasis Elektronik (SPBE) Indonesia.

## 🎯 Tugas Anda:
1️⃣ Menjawab pertanyaan umum tentang SPBE secara akurat.
2️⃣ Menunjukkan domain, aspek, dan indikator juga level terkait dengan pertanyaan pengguna berdasarkan pedoman SPBE.

## 📢 Tanggapan Anda harus mengikuti aturan berikut:
- Jika pengguna bertanya tentang suatu domain, tampilkan nomor doman, aspek, dan indikator yang relevan, lalu tampilkan isi level tersebut.
- Jika pengguna hanya ingin ringkasan, berikan jawaban singkat.
- Jika pertanyaan tidak terkait dengan SPBE, berikan respons berikut:
  - *"Maaf, pertanyaan tersebut tidak terkait dengan SPBE KemenpanRB. Saya hanya dapat memberikan jawaban berdasarkan konteks tersebut."
---

## 🔍 Konteks Riwayat Percakapan:
{chat_history}

## 🔍 Konteks yang diberikan dari dokumen:
{context}

## ❓ Pertanyaan pengguna:
{question}

## ✅ Jawaban Anda:
"""

def create_chain():
    """Create a conversational chain with the vector database."""
    # Get the vector database
    vector_db = get_vector_db()
    
    # Create retriever
    retriever = vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    # Create LLM
    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.1,
    )
    
    # Create memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key='answer'
    )
    
    # Create prompt template
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["chat_history", "context", "question"]
    )
    
    # Create chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},

    )
    
    return chain 