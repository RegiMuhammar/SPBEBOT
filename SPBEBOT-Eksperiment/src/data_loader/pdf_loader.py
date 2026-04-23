from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from typing import List
from langchain_core.documents import Document

class SPBEPDFLoader:
    def __init__(self, directory_path: str = "data"):
        self.directory_path = directory_path
        self.loader = DirectoryLoader(
            directory_path,     
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        )
    
    def load_documents(self) -> List[Document]:
        """Load all PDF documents from the directory"""
        try:
            documents = self.loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Error loading PDF files from directory: {str(e)}") 