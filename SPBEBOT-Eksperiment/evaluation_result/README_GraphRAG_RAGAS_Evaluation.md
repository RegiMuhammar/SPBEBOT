# SPBE GraphRAG RAGAS Evaluation

## Overview
Kode ini dibuat untuk melakukan evaluasi RAGAS (Retrieval-Augmented Generation Assessment) pada sistem GraphRAG SPBE. Evaluasi ini membandingkan performa GraphRAG dengan VectorRAG menggunakan metrik RAGAS.

## Files Created

### 1. `SPBE_GraphRAG_RAGAS_Evaluation.py`
File Python standalone untuk evaluasi RAGAS GraphRAG.

### 2. `SPBE_GraphRAG_RAGAS_Evaluation.ipynb`
Notebook Jupyter untuk evaluasi RAGAS GraphRAG yang lebih interaktif.

## Prerequisites

### Environment Variables
Pastikan file `.env` berisi variabel berikut:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT=your_azure_openai_deployment
AZURE_OPENAI_API_VERSION=your_azure_openai_api_version

# Groq
GROQ_API_KEY=your_groq_api_key

# Neo4J
NEO4J_URI_regguy=your_neo4j_uri
NEO4J_USERNAME_regguy=your_neo4j_username
NEO4J_PASSWORD_regguy=your_neo4j_password
NEO4J_DATABASE_regguy=your_neo4j_database
```

### Dependencies
Install dependencies yang diperlukan:

```bash
pip install ragas langchain-groq langchain-openai langchain-ollama langchain-neo4j pandas python-dotenv
```

## Usage

### Method 1: Using Python Script
```bash
python SPBE_GraphRAG_RAGAS_Evaluation.py
```

### Method 2: Using Jupyter Notebook
1. Buka `SPBE_GraphRAG_RAGAS_Evaluation.ipynb`
2. Jalankan semua cell secara berurutan
3. Hasil evaluasi akan disimpan dalam file CSV dan pickle

## Features

### 1. GraphRAG Components
- **Entity Extraction**: Mengekstrak entitas dari pertanyaan menggunakan Azure OpenAI
- **Graph Retriever**: Mencari informasi di Neo4J knowledge graph
- **Vector Retriever**: Mencari informasi menggunakan vector similarity
- **Hybrid Retrieval**: Menggabungkan hasil graph dan vector retrieval

### 2. RAGAS Metrics
Evaluasi menggunakan 4 metrik RAGAS:

1. **Faithfulness**: Mengukur sejauh mana jawaban sesuai dengan konteks yang diberikan
2. **Answer Relevancy**: Mengukur relevansi jawaban terhadap pertanyaan
3. **Context Recall**: Mengukur sejauh mana konteks yang relevan ditemukan
4. **Context Precision**: Mengukur presisi konteks yang ditemukan

### 3. Test Questions
Sistem menggunakan 5 pertanyaan test yang mencakup:
- Pertanyaan umum SPBE
- Pertanyaan audit SPBE
- Pertanyaan tentang indeks SPBE
- Pertanyaan tentang level kematangan
- Pertanyaan tentang domain arsitektur

## Output Files

### 1. Dataset Files
- `spbe_graphrag_ragas.csv`: Dataset RAGAS dalam format CSV
- `graphrag_ragas_dataset.pkl`: Dataset RAGAS dalam format pickle

### 2. Evaluation Results
- `evaluation_spbe_graphrag.csv`: Hasil evaluasi RAGAS GraphRAG

## Comparison with VectorRAG

Kode ini memungkinkan perbandingan dengan hasil VectorRAG:

```python
# Load results
graphrag_results = pd.read_csv("evaluation_spbe_graphrag.csv")
vector_results = pd.read_csv("evaluation2_spbe_vector.csv")

# Compare metrics
print(f"GraphRAG Faithfulness: {graphrag_results['faithfulness'].mean():.3f}")
print(f"VectorRAG Faithfulness: {vector_results['faithfulness'].mean():.3f}")
```

## Key Differences from VectorRAG

### 1. Retrieval Method
- **VectorRAG**: Menggunakan Parent Document Retriever dengan ChromaDB
- **GraphRAG**: Menggunakan hybrid retrieval (Graph + Vector) dengan Neo4J

### 2. Context Structure
- **VectorRAG**: Context berupa dokumen teks
- **GraphRAG**: Context berupa graph nodes dan relationships

### 3. Entity Extraction
- **VectorRAG**: Tidak ada entity extraction
- **GraphRAG**: Menggunakan entity extraction untuk query graph

## Troubleshooting

### Common Issues

1. **Neo4J Connection Error**
   - Pastikan Neo4J server berjalan
   - Periksa kredensial di file `.env`

2. **Azure OpenAI Error**
   - Periksa API key dan endpoint
   - Pastikan deployment name benar

3. **Ollama Error**
   - Pastikan Ollama berjalan
   - Install model `nomic-embed-text:latest`

4. **Rate Limiting**
   - Sistem memiliki delay 30 detik antar pertanyaan
   - Sesuaikan delay jika diperlukan

### Error Handling
Kode memiliki error handling untuk:
- Connection errors
- API rate limiting
- Data processing errors
- File I/O errors

## Performance Considerations

### 1. Processing Time
- Setiap pertanyaan memerlukan ~30-60 detik
- Total evaluasi: ~5-10 menit untuk 5 pertanyaan

### 2. Resource Usage
- Memory: ~2-4 GB RAM
- CPU: Moderate usage
- Network: Moderate untuk API calls

### 3. Cost Considerations
- Azure OpenAI API calls
- Groq API calls
- Neo4J database queries

## Customization

### 1. Adding New Questions
```python
questions_for_evaluation.append("Pertanyaan baru Anda")
references.append("Reference untuk pertanyaan baru")
```

### 2. Modifying Retrieval
```python
# Modify graph retriever parameters
def graph_retriever(question: str, max_entities: int = 10):  # Increase max_entities
    # Your custom logic
```

### 3. Adding New Metrics
```python
from ragas.metrics import your_custom_metric

results = evaluate(
    dataset=eval_dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
        your_custom_metric  # Add new metric
    ],
    # ...
)
```

## Contributing

Untuk menambahkan fitur atau perbaikan:

1. Fork repository
2. Buat branch baru
3. Implementasi perubahan
4. Test dengan dataset yang ada
5. Submit pull request

## License

Kode ini dibuat untuk evaluasi akademis SPBE GraphRAG system. 