from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document

class SPBETextSplitter:
    def __init__(self, parent_chunk_size: int = 2000, child_chunk_size: int = 400):
        self.parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size)
        self.child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size)
    
    @property
    def get_parent_splitter(self):
        return self.parent_splitter
    
    @property
    def get_child_splitter(self):
        return self.child_splitter 