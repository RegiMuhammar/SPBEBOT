# SPBE GraphRAG RAGAS Evaluation
# Evaluasi RAGAS untuk GraphRAG SPBE

import os
import time
import pickle
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from ragas import evaluate, EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import (
    faithfulness, 
    answer_relevancy, 
    context_recall, 
    context_precision
)

# Load environment variables
load_dotenv()

# Import GraphRAG components
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.vectorstores.neo4j_vector import remove_lucene_chars
from pydantic import BaseModel, Field
from typing import Optional

# Initialize Azure OpenAI
llm_openai_azure = AzureChatOpenAI(
    openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
)

# Initialize Neo4J connection
NEO4J_URI = os.environ.get('NEO4J_URI_regguy')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME_regguy')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD_regguy')
NEO4J_DATABASE = os.environ.get('NEO4J_DATABASE_regguy') 

graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
    refresh_schema=False
)

# Initialize Embedding
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:latest",
)

# Create Neo4J Vector Index
from langchain_neo4j import Neo4jVector
vector_index = Neo4jVector.from_existing_graph(
    embedding=embeddings,
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding",
    url=os.environ.get('NEO4J_URI_regguy'),
    username=os.environ.get('NEO4J_USERNAME_regguy'),
    password=os.environ.get('NEO4J_PASSWORD_regguy'),
)

# Entity extraction for GraphRAG
class Entities(BaseModel):
    """Identifying information about entities."""
    names: Optional[list[str]] = Field(default_factory=list, description="Nama orang, organisasi, atau entitas bisnis")
    kata_kunci_spbe: Optional[list[str]] = Field(default_factory=list, description="Istilah atau frasa penting yang berkaitan dengan SPBE, misalnya arsitektur SPBE, layanan digital, transformasi pemerintahan digital, domain, aspek, indikator, level, kematangan, kriteria dll, tahun indeks, untuk kata kunci tahun, ekstrak format seperti '2021', '2022', '2023'.")

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Kamu adalah asisten yang mengekstrak entitas dari dokumen kebijakan SPBE (Sistem Pemerintahan Berbasis Elektronik). "
        "Ekstrak dan kategorikan semua nama organisasi, domain SPBE, aspek SPBE, indikator evaluasi, dan istilah atau kata kunci penting dari teks berikut."
    ),
    (
        "human",
        "Gunakan format berikut untuk mengekstrak informasi dari input:\n{question}"
    )
])

entity_chain = prompt | llm_openai_azure.with_structured_output(Entities)

def generate_full_text_query(input: str) -> str:
    """
    Generate a full-text search query for a given input string.
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()

def graph_retriever(question: str, max_entities: int = 5) -> str:
    """
    Graph retriever for GraphRAG
    """
    result = ""
    entities = entity_chain.invoke({"question": question})

    all_entities = []
    for field in ["names", "kata_kunci_spbe"]:
        values = getattr(entities, field, [])
        if values:
            all_entities.extend(values)

    selected_entities = all_entities[:max_entities]

    for entity in selected_entities:
        response = graph.query(
            """
            CALL db.index.fulltext.queryNodes('fulltext_entity_id', $query, {limit:2})
            YIELD node, score
            OPTIONAL MATCH (node)-[r]->(neighbor)
            RETURN
              node.id AS node_id,
              properties(node) AS props,
              labels(node) AS labels,
              COLLECT([type(r), neighbor.id]) AS relationships,
              score
            LIMIT 50
            """,
            {"query": generate_full_text_query(entity)},
        )
        for el in response:
            result += f"🔹 Node: {el['node_id']}\n"
            result += f"   Labels: {', '.join(el['labels'])}\n"
            result += f"   Score: {round(el['score'], 3)}\n"

            for key, value in el['props'].items():
                result += f"     {key}: {value}\n"

            relationships = el.get("relationships", [])
            if relationships:
                result += f"   Relationships:\n"
                for rel in relationships:
                    if rel and len(rel) == 2:
                        rel_type, neighbor = rel
                        result += f"     ➡️ -[{rel_type}]-> {neighbor}\n"

            result += "\n"

    return result or "[INFO] Tidak ada hasil graph yang ditemukan."

def full_retriever(question: str):
    """
    Full retriever combining graph and vector data
    """
    print(f"Search query: {question}")
    graph_data = graph_retriever(question)
    vector_data = [el.page_content for el in vector_index.similarity_search(question, k=2)]
    final_data = f"""Graph data:
{graph_data}
vector data:
{"#Document ".join(vector_data)}
    """
    return final_data

# GraphRAG Chain
template = """Answer the question based only on the following context:
{context}

Question: {question}
Use natural language and be concise.
Answer:"""
prompt = ChatPromptTemplate.from_template(template)

llm = ChatGroq(
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile", 
    temperature=0
)

graphrag_chain = (
    RunnableParallel(
        {
            "context": full_retriever,
            "question": RunnablePassthrough(),
        }
    )
    | prompt
    | llm
    | StrOutputParser()
)

def prepare_ragas_data_graphrag(question, reference=None):
    """
    Menyiapkan data untuk evaluasi RAGAS dari GraphRAG chain
    """
    try:
        # Get context from full_retriever
        context = full_retriever(question)
        
        # Get response from GraphRAG chain
        response = graphrag_chain.invoke(question)
        
        return {
            "user_input": question,
            "retrieved_contexts": [context],  # RAGAS expects list of contexts
            "response": response,
            "reference": reference
        }
    except Exception as e:
        print(f"Error in prepare_ragas_data_graphrag: {str(e)}")
        return None

def evaluate_graphrag_with_ragas(questions, references=None):
    """
    Evaluasi GraphRAG menggunakan RAGAS
    """
    ragas_dataset = []
    
    for i, question in enumerate(questions):
        print(f"Processing question {i+1}/{len(questions)}: {question[:50]}...")
        
        # Get reference if available
        reference = references[i] if references and i < len(references) else None
        
        # Prepare RAGAS data
        ragas_data = prepare_ragas_data_graphrag(question, reference)
        
        if ragas_data:
            ragas_dataset.append(ragas_data)
            print(f"✅ Question {i+1} processed successfully")
        else:
            print(f"❌ Failed to prepare RAGAS data for question {i+1}")

        # Jeda untuk menghindari rate limiting
        print("⏳ Menunggu 30 detik...")
        time.sleep(30)
    
    return ragas_dataset

# Test questions untuk evaluasi GraphRAG
questions_for_evaluation = [
    """Dalam penerapan Manajemen Risiko SPBE, masing-masing IPPD (Instansi Pusat dan Pemerintah Daerah) dapat mengacu pada Pedoman Manajemen Risiko SPBE yang ditetapkan dalam kebijakan:""",
    """Jika "Rencana dan Anggaran SPBE Instansi Pusat Pemerintah Daerah telah terpadu dan dapat dikendalikan oleh unit kerja/perangkat daerah yang menjalankan fungsi perencanaan dan penganggaran dan telah direviu serta dievaluasi secara periodik:" Maka dapat diberikan level...""",
    "Berapa nilai indeks domain yang masih dibawah target pada tahun 2021-2023?",
    """Sebuah IPPD melampirkan Peta Rencana SPBE yang telah didokumentasikan secara formal, dan mengklaim memiliki dokumen Peta Rencana SPBE yang telah mengatur seluruh muatan Peta Rencana SPBE Instansi Pusat Pemerintah Daerah. Dokumen Peta Rencana yang diunggah berisikan muatan Peta Rencana secara lengkap antara lain Tata Kelola SPBE, Manajemen SPBE, Layanan SPBE, Arsitektur SPBE, Aplikasi SPBE, Keamanan SPBE dan Audit TIK. Maka level yang pantas diberikan adalah...""",
    """Dibawah ini merupakan domain-domain dari Arsitektur SPBE berdasarkan Perpres SPBE, kecuali (pilih salah satu):

- domain arsitektur Proses Bisnis
- domain arsitektur Manajemen SPBE 
- domain arsitektur Infrastruktur SPBE
- domain arsitektur Aplikasi SPBE
- domain arsitektur Keamanan SPBE
- domain arsitektur Layanan SPBE"""
]

references = [
    """PermenPANRB No. 5 Tahun 2020 memberikan pedoman umum bagi Instansi Pusat dan Pemerintah Daerah dalam melaksanakan SPBE, termasuk penerapan Manajemen Risiko SPBE""",
    """Berdasarkan pedoman pemantauan dan evaluasi SPBE, dengan diberikannya informasi kriteria-kriteria, maka indeks SPBE yang diberikan: 
 
Penilaian: 
Level: 4,
Indikator: 13,
Aspek: 2,
Domain: 2

Alasan penilaian diatas karena Rencana dan Anggaran SPBE Instansi Pusat/Pemerintah Daerah telah terpadu dan dapat dikendalikan oleh unit kerja/perangkat daerah yang menjalankan fungsi perencanaan dan penganggaran dan telah direviu serta dievaluasi secara periodik, sehingga sesuai dengan kriteria Level 4 pada Domain Tata Kelola, Aspek Perencanaan Strategis SPBE, dan Indikator 13 tentang tingkat kematangan keterpaduan rencana dan anggaran SPBE.""",
    """Nilai indeks domain yang masih di bawah target (<2,60) pada tahun 2021-2023 adalah:

1. Indeks Domain Tata Kelola: 
   - Tahun 2021: 1,89
   - Tahun 2022: 1,85
   - Tahun 2023: 2,29

2. Indeks Domain Manajemen: 
   - Tahun 2021: 1,23
   - Tahun 2022: 1,32
   - Tahun 2023: 1,66""",
    """Berdasarkan pedoman pemantauan dan evaluasi SPBE, dengan diberikannya informasi kriteria-kriteria, maka indeks SPBE yang diberikan: 
 
Penilaian: 
Level: 3,
Indikator: 12,
Aspek: 2,
Domain: 2

Alasan penilaian diatas karena dokumen Peta Rencana SPBE telah mengatur seluruh muatan Peta Rencana SPBE Instansi Pusat/Pemerintah Daerah secara lengkap (Tata Kelola SPBE, Manajemen SPBE, Layanan SPBE, Infrastruktur SPBE, Aplikasi SPBE, Keamanan SPBE, Audit Teknologi SPBE dan Audit TIK) dan dokumen Peta Rencana SPBE telah didokumentasikan secara formal, sehingga sesuai dengan kriteria Level 3 pada Domain Tata Kelola, Aspek Perencanaan Strategis SPBE, dan Indikator 12 tentang Tingkat Kematangan Peta Rencana SPBE Instansi Pusat/Pemerintah Daerah. Namun, perlu diperhatikan bahwa untuk mencapai Level 4, IPPD harus memenuhi kriteria tambahan, yaitu dokumen Peta Rencana SPBE telah diterapkan secara konsisten melalui rencana kerja dan anggaran 3 (tiga) tahun terakhir, dan dokumen Peta Rencana SPBE telah dilakukan reviu dan evaluasi secara periodik.""",
    "Domain Arsitektur Manajemen SPBE tidak termasuk dalam daftar domain arsitektur SPBE yang ditetapkan dalam Perpres SPBE. Domain Manajemen SPBE sebenarnya merupakan salah satu aspek dalam Sistem Pemerintahan Berbasis Elektronik (SPBE), bukan domain arsitektur SPBE."
]

def run_graphrag_evaluation():
    """
    Menjalankan evaluasi GraphRAG dengan RAGAS
    """
    print("🚀 Memulai evaluasi GraphRAG dengan RAGAS...")
    
    # Menjalankan evaluasi
    ragas_dataset = evaluate_graphrag_with_ragas(questions_for_evaluation, references)
    
    # Menampilkan hasil
    print(f"\n📊 Dataset RAGAS berhasil disiapkan dengan {len(ragas_dataset)} sampel")
    for i, data in enumerate(ragas_dataset):
        print(f"\n--- Sampel {i+1} ---")
        print(f"Question: {data['user_input']}")
        print(f"Context Length: {len(str(data['retrieved_contexts']))} characters")
        print(f"Response: {data['response'][:100]}...")
        if data['reference']:
            print(f"Reference: {data['reference'][:100]}...")
    
    # Save dataset
    df_ragas = pd.DataFrame(ragas_dataset, columns=["user_input", "retrieved_contexts", "response", "reference"])
    df_ragas.to_csv("spbe_graphrag_ragas.csv", index=False)
    
    # Save as pickle
    with open("graphrag_ragas_dataset.pkl", "wb") as f:
        pickle.dump(ragas_dataset, f)
    
    return ragas_dataset

def run_ragas_metrics(ragas_dataset):
    """
    Menjalankan metrik RAGAS pada dataset GraphRAG
    """
    print("📊 Menjalankan metrik RAGAS...")
    
    # Create evaluation dataset
    eval_dataset = EvaluationDataset.from_list(ragas_dataset)
    
    # Initialize evaluators
    evaluator_embedding = LangchainEmbeddingsWrapper(embeddings)
    evaluator_llm = LangchainLLMWrapper(llm_openai_azure)
    
    # Evaluasi dengan RAGAS
    results = evaluate(
        dataset=eval_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embedding,
    )
    
    print("📊 Hasil Evaluasi RAGAS GraphRAG:")
    results_df = results.to_pandas()
    results_df.to_csv("evaluation_spbe_graphrag.csv", index=False)
    print(results_df)
    
    return results_df

if __name__ == "__main__":
    # Run GraphRAG evaluation
    ragas_dataset = run_graphrag_evaluation()
    
    # Run RAGAS metrics
    results_df = run_ragas_metrics(ragas_dataset)
    
    print("✅ Evaluasi GraphRAG dengan RAGAS selesai!") 