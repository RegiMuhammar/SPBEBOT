from langchain.retrievers import ParentDocumentRetriever
from langchain_core.documents import Document
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryStore

class SPBERetriever:
    def __init__(
        self,
        vectorstore: Chroma,
        docstore: InMemoryStore,
        child_splitter: RecursiveCharacterTextSplitter,
        parent_splitter: RecursiveCharacterTextSplitter,
        search_type: str = "mmr",
        k: int = 2,
        score_threshold: float = 0.8
    ):
        self.retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=docstore,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
            search_type=search_type,
            search_kwargs={"k": k, "score_threshold": score_threshold}
        )
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the retriever"""
        self.retriever.add_documents(documents)
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents for a query"""
        return self.retriever.get_relevant_documents(query) 