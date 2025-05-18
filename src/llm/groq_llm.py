from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

class SPBELLM:
    def __init__(
        self,
        model_name: str = "llama3-70b-8192",
        temperature: float = 0
    ):
        load_dotenv()
        
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY not found in .env file")
            
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    
    @property
    def get_llm(self):
        return self.llm 