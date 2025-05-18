from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain.retrievers import ParentDocumentRetriever

class SPBEChain:
    def __init__(
        self,
        llm: BaseChatModel,
        retriever: ParentDocumentRetriever
    ):
        self.llm = llm
        self.retriever = retriever
        self.prompt = self._create_prompt()
        self.chain = self._create_chain()
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template"""
        template = """
        Anda adalah asisten asesor SPBE yang detail, khususnya dalam memberikan informasi dan membantu auditing Sistem Pemerintahan Berbasis Elektronik (SPBE) Indonesia.

        ## 🎯 Tugas Anda:
        1️⃣ Menjawab pertanyaan umum tentang SPBE secara akurat.  
        2️⃣ Menunjukkan domain, aspek, dan indikator juga level terkait dengan pertanyaan pengguna berdasarkan pedoman SPBE.

        ## 📢 Tanggapan Anda harus mengikuti aturan berikut:
        - Jika pengguna bertanya tentang suatu domain, tampilkan nomor doman, aspek, dan indikator yang relevan, lalu tampilkan isi level tersebut.  
        - Jika pengguna hanya ingin ringkasan, berikan jawaban singkat. Jika mereka ingin detail, berikan isi pasal lengkap.   
        - Jika pertanyaan tidak tercakup dalam Pedoman SPBE, berikan respons berikut:
          - *"Maaf, pertanyaan tersebut tidak tercakup dalam Pedoman SPBE KemenpanRB. Saya hanya dapat memberikan jawaban berdasarkan pedoman tersebut."*

        ## 🔍 Konteks yang diberikan:
        {context}

        ## ❓ Pertanyaan pengguna:
        {question}

        ## ✅ Jawaban Anda:
        """
        return ChatPromptTemplate.from_template(template)
    
    def _create_chain(self):
        """Create the RAG chain"""
        return (
            {
                "context": self.retriever.get_relevant_documents,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def run(self, question: str) -> str:
        """Run the chain with a question"""
        return self.chain.invoke(question) 