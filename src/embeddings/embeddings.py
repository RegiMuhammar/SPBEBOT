from langchain_ollama import OllamaEmbeddings

class SPBEEmbeddings:
    def __init__(self, model_name: str = "nomic-embed-text:latest"):
        self.embeddings = OllamaEmbeddings(
            model=model_name
        )
    
    @property
    def get_embeddings(self):
        return self.embeddings 