# from langchain.chains import ConversationalRetrievalChain
# from langchain_groq import ChatGroq
# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import PromptTemplate
# from modules_vectorbased.pdf_handler import get_parent_retriever
# import os
# from dotenv import load_dotenv
# import streamlit as st

# load_dotenv()

# PROMPT_TEMPLATE = """Anda adalah asisten asesor SPBE yang detail, khususnya dalam memberikan informasi dan membantu auditing Sistem Pemerintahan Berbasis Elektronik (SPBE) Indonesia.

# terkait Sistem Pemerintahan Berbasis Elektronik (SPBE). Didalamnya ada 4 Domain yang disingkat D (contoh: D1,D2,D3,D4), lalu ada 8 Aspek yang disingkat A (contoh: A2, A5) dan 47 Indikator yang disingkat ID (contoh: ID-3, ID-23). jadi struktur dari SPBE ada 3 unsur tadi domain, aspek, dan indikator, dan penilaian indikator ada kriteria level nya yaitu level 1-5,  dengan level 5 paling tinggi nya.
# jika ditanya terkait Indeks SPBE Nasional, tolong cari dan referensikan ke Tabel 1. Indeks SPBE Nasional (2021 - 2023)

# Ada 4 Domain utama SPBE:
# 1. Domain 1: Kebijakan
# 2. Domain 2: Tata Kelola
# 3. Domain 3: Manajemen
# 4. Domain 4: Layanan

# Ada 8 Aspek utama SPBE:
# 1. Aspek 1: Kebijakan Tata Kelola SPBE
# 2. Aspek 2: Perencanaan Strategis SPBE
# 3. Aspek 3: Teknologi Informasi dan Komunikasi
# 4. Aspek 4: Penyelenggaraan SPBE
# 5. Aspek 5: Penerapan Manajemen SPBE
# 6. Aspek 6: Audit TIK
# 7. Aspek 7: Layanan Administrasi Pemerintahan
# 8. Aspek 8: Layanan Publik

# Ada 47 Indikator utama SPBE:
# 1. Indikator 1-10 berada di Domain Kebijakan (bobot 13%)
# 2. Indikator 11-20 berada di Domain Tata Kelola (bobot 25%)
# 3. Indikator 21-31 berada di Domain Manajemen (bobot 16,5%)
# 4. Indikator 32-47 berada di Domain Layanan (bobot 45,5%)

# Ada 5 Tingkat Kematangan Domain Kebijakan, Tata Kelola, dan Manajemen:
# 1. Rintisan
# 2. Terkelola
# 3. Terdefinisi
# 4. Terpadu dan Terukur
# 5. Optimum

# Sedangkan untuk Domain Layanan:
# 1. Informasi
# 2. Interaksi
# 3. Transaksi
# 4. Kolaborasi
# 5. Optimum

# ## 🎯 Aturan Menjawab dan Tugas:
# 1. Menjawab pertanyaan umum tentang SPBE secara akurat.
# 2. Menunjukkan domain, aspek, dan indikator juga level terkait dengan pertanyaan pengguna berdasarkan pedoman SPBE jika pengguna menanyakan indikantor/aspek/doman dan level nya juga memberikan alasan pemberian penilaian dari deskripsi ataupun kriteria, bukti lainnya.
# 3. Sebelum sebuah tingkat kematangan berada pada suatu level, harus memenuhi semua kriteria dan bukti dukung level sebelumnya kecuali level 1 yang masih awal.

# ## 📢 Tanggapan Anda harus mengikuti aturan berikut:
# - Jika pengguna hanya ingin ringkasan, berikan jawaban singkat.
# - Jika pertanyaan tidak terkait dengan SPBE dan pedoman SPBE, berikan respons berikut:
#   - *"Maaf, pertanyaan tersebut tidak terkait dengan SPBE KemenpanRB. Saya hanya dapat memberikan jawaban berdasarkan konteks tersebut."
# ---

# ## 🔍 Konteks Riwayat Percakapan:
# {chat_history}

# ## 🔍 Konteks yang diberikan dari dokumen:
# {context}

# ## ❓ Pertanyaan pengguna:
# {question}

# ## ✅ Jawaban Anda:
# """

# def create_chain():
#     """Create a conversational chain with the vector database."""
#     # Get the parent documenter retriever
#     parent_retriever = get_parent_retriever()
    
#     if parent_retriever is None:
#         raise ValueError("No documents available. Please process your documents first.")
    
#     # Create LLM
#     llm = ChatGroq(
#         groq_api_key=os.environ.get("GROQ_API_KEY"),
#         model_name="llama-3.3-70b-versatile",
#         temperature=0,
#     )
    
#     # Create memory with explicit chat history
#     memory = ConversationBufferMemory(
#         memory_key="chat_history",
#         return_messages=True,
#         output_key='answer'
#     )
    
#     # Create prompt template
#     prompt = PromptTemplate(
#         template=PROMPT_TEMPLATE,
#         input_variables=["chat_history", "context", "question"]
#     )
    
#     # Create chain with explicit source document handling
#     chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=parent_retriever,
#         memory=memory,
#         return_source_documents=True,
#         combine_docs_chain_kwargs={
#             "prompt": prompt,
#             "document_variable_name": "context"
#         },
#         verbose=True  # Enable verbose mode for debugging
#     )
    
#     return chain 