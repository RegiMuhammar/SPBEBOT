from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryStore
from langchain_core.embeddings import Embeddings

class SPBEVectorStore:
    def __init__(
        self,
        embedding_function: Embeddings,
        collection_name: str = "spbe_parent_chunk",
        persist_directory: str = "./chroma_spbe_parent_db"
    ):
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=persist_directory
        )
        self.docstore = InMemoryStore()
    
    @property
    def get_vectorstore(self):
        return self.vectorstore
    
    @property
    def get_docstore(self):
        return self.docstore 