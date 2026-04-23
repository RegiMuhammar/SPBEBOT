import os
import time
import chromadb
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_pinecone import PineconeVectorStore

def main():
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "spbe-cohere")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    
    if not pinecone_api_key or not cohere_api_key:
        print("Error: PINECONE_API_KEY atau COHERE_API_KEY tidak ditemukan di .env")
        return
        
    print(f"Menghubungkan ke Pinecone...")
    pc = Pinecone(api_key=pinecone_api_key)
    
    # Buat index jika belum ada
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Index '{index_name}' belum ada. Membuat index baru dengan dimensi 1024...")
        pc.create_index(
            name=index_name,
            dimension=1024, # Dimensi untuk Cohere embed-multilingual-v3.0
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"Menunggu index '{index_name}' siap...")
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        print("Index siap!")
    else:
        print(f"Index '{index_name}' ditemukan.")
        
    print("Inisialisasi Cohere Embeddings...")
    embeddings = CohereEmbeddings(
        model="embed-multilingual-v3.0",
        cohere_api_key=cohere_api_key
    )
    
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    
    # Path ke ChromaDB lama
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "SPBEBOT-Eksperiment", "db"))
    print(f"Membaca ChromaDB dari: {db_path}")
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        
        if not collections:
            print("Tidak ada collection ditemukan di ChromaDB tersebut.")
            return
            
        for col in collections:
            print(f"\nMemproses Collection: '{col.name}' (Total: {col.count()} dokumen)")
            
            data = col.get(include=["documents", "metadatas"])
            ids = data.get("ids", [])
            documents = data.get("documents", [])
            metadatas = data.get("metadatas", [])
            
            if len(ids) == 0:
                print(f"Collection '{col.name}' kosong.")
                continue
                
            # Batch upsert ke Pinecone via Langchain (akan melakukan API call ke Cohere)
            batch_size = 96 # Dibatasi agar tidak melebihi rate-limit (max 96 per call recommended untuk Cohere)
            total_upserted = 0
            
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_docs = documents[i:i+batch_size]
                
                # Pembersihan metadata (Cohere/Pinecone kadang rewel jika ada None)
                cleaned_meta = []
                for j in range(len(batch_meta)):
                    meta = batch_meta[j] if batch_meta[j] is not None else {}
                    meta["text"] = batch_docs[j]
                    cleaned_meta.append(meta)
                
                print(f"Meng-embed dan mengunggah batch ke-{i//batch_size + 1} ({len(batch_ids)} dokumen)...")
                # Ini akan memanggil API Cohere untuk melakukan embedding, lalu mengirim ke Pinecone
                vectorstore.add_texts(texts=batch_docs, metadatas=cleaned_meta, ids=batch_ids)
                
                total_upserted += len(batch_ids)
                print(f"-> Berhasil {total_upserted} / {len(ids)} vektor...")
                time.sleep(1) # Hindari rate limit
                
            print(f"Selesai memigrasikan {total_upserted} vektor dari collection '{col.name}' ke Pinecone!")
            
    except Exception as e:
        print(f"Terjadi kesalahan saat memigrasikan data: {e}")

if __name__ == "__main__":
    main()
