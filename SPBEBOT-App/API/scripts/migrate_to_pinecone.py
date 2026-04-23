import os
import time
import chromadb
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "spbe-index")
    
    if not pinecone_api_key:
        print("Error: PINECONE_API_KEY tidak ditemukan di .env")
        return
        
    print(f"Menghubungkan ke Pinecone...")
    pc = Pinecone(api_key=pinecone_api_key)
    
    # Buat index jika belum ada
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Index '{index_name}' belum ada. Membuat index baru...")
        pc.create_index(
            name=index_name,
            dimension=768, # Dimensi untuk nomic-embed-text
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1" # Region gratis untuk Pinecone Serverless
            )
        )
        print(f"Menunggu index '{index_name}' siap...")
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        print("Index siap!")
    else:
        print(f"Index '{index_name}' ditemukan.")
        
    index = pc.Index(index_name)
    
    # Path ke ChromaDB lama (naik 3 tingkat: scripts -> API -> SPBEBOT-App -> SPBEBOT)
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
            
            data = col.get(include=["embeddings", "documents", "metadatas"])
            ids = data.get("ids", [])
            embeddings = data.get("embeddings", [])
            documents = data.get("documents", [])
            metadatas = data.get("metadatas", [])
            
            if len(ids) == 0 or len(embeddings) == 0:
                print(f"Collection '{col.name}' kosong atau tidak memiliki embedding.")
                continue
                
            # Batch upsert ke Pinecone
            batch_size = 100
            total_upserted = 0
            
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_emb = embeddings[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_docs = documents[i:i+batch_size]
                
                vectors_to_upsert = []
                for j in range(len(batch_ids)):
                    meta = batch_meta[j] if batch_meta[j] is not None else {}
                    # Pinecone mengharuskan nilai metadata berupa string, number, boolean, atau list of string
                    # Kita masukkan text document sebagai `text` ke dalam metadata agar bisa di retrieve
                    meta["text"] = batch_docs[j]
                    
                    # Konversi numpy array ke list murni jika diperlukan
                    val = batch_emb[j]
                    if hasattr(val, "tolist"):
                        val = val.tolist()
                    elif not isinstance(val, list):
                        val = list(val)
                    val = [float(x) for x in val]
                        
                    vectors_to_upsert.append({
                        "id": str(batch_ids[j]),
                        "values": val,
                        "metadata": meta
                    })
                    
                index.upsert(vectors=vectors_to_upsert)
                total_upserted += len(vectors_to_upsert)
                print(f"Berhasil mengunggah {total_upserted} / {len(ids)} vektor...")
                
            print(f"Selesai memigrasikan {total_upserted} vektor dari collection '{col.name}' ke Pinecone!")
            
    except Exception as e:
        print(f"Terjadi kesalahan saat memigrasikan data: {e}")

if __name__ == "__main__":
    main()
