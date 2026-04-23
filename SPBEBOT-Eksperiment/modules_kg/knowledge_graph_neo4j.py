# This is the core of Langgraph using Neo4J
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List
import time
import asyncio
from langchain_core.documents import Document
from typing import Optional

from langchain_core.runnables import (RunnableParallel, RunnablePassthrough)
from langchain.text_splitter import TokenTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jVector
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser 
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship

class Entities(BaseModel):
    """Identifying information about entities."""

    names: Optional[list[str]] = Field(default_factory=list, description="Nama orang, organisasi, atau entitas bisnis")
    kata_kunci_spbe: Optional[list[str]] = Field(default_factory=list, description="Istilah atau frasa penting yang berkaitan dengan SPBE, misalnya arsitektur SPBE, layanan digital, transformasi pemerintahan digital, domain, aspek, indikator, level, kematangan, kriteria dll, tahun indeks, untuk kata kunci tahun, ekstrak format seperti '2021', '2022', '2023'. ")

class SPBE_GraphRAG_Neo4J:
    default_cypher = "MATCH (s)-[r:!MENTIONS]->(t) RETURN s,r,t LIMIT 100"

    def __init__(self):
        load_dotenv()
        self.NEO4J_URI = os.environ.get('NEO4J_URI_regguy')
        self.NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME_regguy')
        self.NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD_regguy')
        self.NEO4J_DATABASE = os.environ.get('NEO4J_DATABASE_regguy') 
        self.graph = Neo4jGraph(
            url=self.NEO4J_URI,
            username=self.NEO4J_USERNAME,
            password=self.NEO4J_PASSWORD,
            database=self.NEO4J_DATABASE
        )
        self.llm_graph = ChatGroq(
            groq_api_key=os.environ.get("GROQ_API_KEY"), 
            model_name="llama-3.3-70b-versatile", 
            temperature=0
        )
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        self.chat_history = []
        self.create_fulltext_index()
        self.prepare_cypher_chat_template()
        self.create_vector_index()
        
    def data_db_directories(self):
        """Initialize data directory and ensure it exists."""
        try:
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            data_path = parent_dir / "data"
            os.makedirs(data_path, exist_ok=True)
            return data_path
        except Exception as e:
            raise Exception(f"Error creating data directory: {str(e)}")
    
    def loading_and_splitting_data(self):
        """Loading directory data and splitting content"""
        try:
            data_path = self.data_db_directories()
            
            # Load documents from directory
            loader = DirectoryLoader(
                data_path, 
                glob='**/*.pdf', 
                show_progress=True, 
                use_multithreading=True, 
                loader_cls=PyPDFLoader
            )
            self.documents = loader.load()

            if not self.documents:
                raise Exception("No PDF documents found in the data directory")

            # Split documents into chunks
            text_splitter = TokenTextSplitter(
                chunk_size=2000, 
                chunk_overlap=100
            )
            texts = text_splitter.split_documents(self.documents)
            
            if not texts:
                raise Exception("No text chunks generated from documents")
                
            return texts
            
        except Exception as e:
            raise Exception(f"Error in loading and splitting data: {str(e)}")

    async def process_batch(self, batch: List[Document], llm_graph_transformer) -> List[GraphDocument]:
        """Process a batch of documents asynchronously"""
        try:
            return llm_graph_transformer.convert_to_graph_documents(batch)
        except Exception as e:
            print(f"Error processing batch: {str(e)}")
            return []

    async def create_graph_async(self):
        """Create knowledge graph from documents asynchronously"""
        try:
            # Define node and relationship
            spbe_nodes = [
                "SPBE",
                "Indeks",
                "Domain",
                "Aspek",
                "Indikator",
                "Kuesioner",
                "Deskripsi Indikator",
                "Ketentuan Penilaian",
                "Contoh Bukti Dukung",
                "Level",
                "Kriteria Level",
                "Kriteria Pemenuhan Level",
                "Kriteria Bukti Dukung",
                "Contoh Kaidah",
                "Bab Pedoman",
                "Poin Pedoman"
            ]

            spbe_relationships = [
                "Memiliki_Indeks",
                "Memiliki_Aspek",                     # Domain → Aspek
                "Memiliki_Indikator",                # Aspek → Indikator
                "Memiliki_Kuesioner",                # Indikator → Kuesioner
                "Memiliki_Deskripsi",                # Indikator → Deskripsi Indikator
                "Memiliki_Ketentuan_Penilaian",      # Indikator → Ketentuan Penilaian
                "Memiliki_Contoh_Bukti_Dukung",      # Indikator → Contoh Bukti Dukung
                "Memiliki_Level",                    # Indikator → Level (1–5)
                "Memiliki_Kriteria_Level",           # Level → Kriteria Level
                "Memiliki_Kriteria_Pemenuhan",       # Level → Kriteria Pemenuhan Level
                "Memiliki_Kriteria_Bukti_Dukung",    # Level → Kriteria Bukti Dukung
                "Contoh_Kaidah_Memiliki_Kriteria",
                "Memiliki_Penjelasan",
                "Memiliki_Kriteria_TINGKAT_KEMATANGAN",
                "Memiliki_SubBab",
                "Memiliki_SubPoin",
            ]
            # Initialize transformer
            llm_graph_transformer = LLMGraphTransformer(
                llm=self.llm_graph,
                allowed_nodes=spbe_nodes,
                allowed_relationships=spbe_relationships,
                strict_mode=False,
                node_properties=True,
                relationship_properties=True
            )
            
            # Load and split data
            spbe_texts = self.loading_and_splitting_data()
            
            # Process in batches
            batch_size = 5  # Adjust based on your needs
            all_graph_documents = []
            
            for i in range(0, len(spbe_texts), batch_size):
                batch = spbe_texts[i:i + batch_size]
                graph_documents = await self.process_batch(batch, llm_graph_transformer)
                all_graph_documents.extend(graph_documents)
                
                # Add delay between batches to avoid rate limits
                await asyncio.sleep(30)
            
            # Store all documents to Neo4J
            self.graph.add_graph_documents(
                all_graph_documents,
                baseEntityLabel=True,
                include_source=True
            )
            
        except Exception as e:
            raise Exception(f"Error in async graph creation: {str(e)}")

    def create_graph(self):
        """Synchronous wrapper for async graph creation"""
        asyncio.run(self.create_graph_async())

    # Create vector store
    def create_vector_index(self):
        self.vector_index = Neo4jVector.from_existing_graph(
            embedding=self.embeddings,
            search_type="hybrid",
            node_label="Document",
            text_node_properties=["text"],
            embedding_node_property="embedding",
            url = os.environ.get('NEO4J_URI_regguy'),
            username = os.environ.get('NEO4J_USERNAME_regguy'),
            password = os.environ.get('NEO4J_PASSWORD_regguy'),
        )

    def create_fulltext_index(self):
        """Create fulltext index for entity search."""
        try:
            # First check if index exists
            check_index = self.graph.query("""
            SHOW INDEXES
            """)
            print("Existing indexes:", check_index)
            
            # Create the index
            self.graph.query('''
                CREATE FULLTEXT INDEX `fulltext_entity_id`
                IF NOT EXISTS
                FOR (n:__Entity__) 
                ON EACH [n.id];
                ''')
            
            # Verify index was created
            verify_index = self.graph.query("""
            SHOW INDEXES
            """)
            print("Indexes after creation:", verify_index)
            
            print("Fulltext index created successfully")
        except Exception as e:
            print(f"Error creating fulltext index: {str(e)}")
            # If index already exists, we can ignore the error
            pass

    def prepare_cypher_chat_template(self):
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Kamu adalah asisten yang mengekstrak entitas dari dokumen kebijakan SPBE (Sistem Pemerintahan Berbasis Elektronik). "
                "Ekstrak dan kategorikan semua nama organisasi, domain SPBE, aspek SPBE, indikator evaluasi, dan istilah atau kata kunci penting dari teks berikut."
            ),
            (
                "human",
                "Gunakan format berikut untuk mengekstrak informasi dari input:\n{question}"
            )
        ])
        self.entity_chain = prompt | self.llm_graph.with_structured_output(Entities)

    @staticmethod
    def generate_full_text_query(input: str) -> str:
        """
        Generate a full-text search query for a given input string.

        This function constructs a query string suitable for a full-text
        search. It processes the input string by splitting it into words and 
        appending a similarity threshold (~2 changed characters) to each
        word, then combines them using the AND operator. Useful for mapping
        entities from user questions to database values, and allows for some 
        misspelings.
        """
        full_text_query = ""
        words = [el for el in remove_lucene_chars(input).split() if el]
        for word in words[:-1]:
            full_text_query += f" {word}~2 AND"
        full_text_query += f" {words[-1]}~2"
        return full_text_query.strip()

    def structured_retriever(self, question: str, max_entities: int = 5) -> str:
        """
        Mengumpulkan keterkaitan entitas yang disebutkan dalam pertanyaan
        """
        try:
            result = ""
            entities = self.entity_chain.invoke({"question": question})

            all_entities = []
            for field in ["names", "kata_kunci_spbe"]:
                values = getattr(entities, field, [])
                if values:
                    all_entities.extend(values)

            selected_entities = all_entities[:max_entities]

            for entity in selected_entities:
                response = self.graph.query(
                    """
                    CALL db.index.fulltext.queryNodes('fulltext_entity_id', $query, {limit:2})
                    YIELD node, score
                    OPTIONAL MATCH (node)-[r]->(neighbor)
                    RETURN
                      node.id AS node_id,
                      properties(node) AS props,
                      labels(node) AS labels,
                      COLLECT([type(r), neighbor.id]) AS relationships,
                      score
                    LIMIT 50
                    """,
                    {"query": self.generate_full_text_query(entity)},
                )
                for el in response:
                    result += f"🔹 Node: {el['node_id']}\n"
                    result += f"   Labels: {', '.join(el['labels'])}\n"
                    result += f"   Score: {round(el['score'], 3)}\n"

                    for key, value in el['props'].items():
                        result += f"     {key}: {value}\n"

                    relationships = el.get("relationships", [])
                    if relationships:
                        result += f"   Relationships:\n"
                        for rel in relationships:
                            if rel and len(rel) == 2:
                                rel_type, neighbor = rel
                                result += f"     ➡️ -[{rel_type}]-> {neighbor}\n"

                    result += "\n"

            return result or "[INFO] Tidak ada hasil graph yang ditemukan."
        except Exception as e:
            print(f"Error in structured_retriever: {str(e)}")
            print(f"Full error details: {type(e).__name__}: {str(e)}")
            return ""
    
    def retriever(self, question: str):
        print(f"Search query: {question}")
        structured_data = self.structured_retriever(question)
        unstructured_data = [el.page_content for el in self.vector_index.similarity_search(question)]
        final_data = f"""
        Structured data:
        {structured_data}
        Unstructured data:
        {"#Document ". join(unstructured_data)}
        """
        return final_data
    
    def load_prompt_template(self):
        """Load prompt template from text file"""
        try:
            current_dir = Path(__file__).parent
            prompt_path = current_dir / "prompt_template.txt"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error loading prompt template: {str(e)}")

    def ask_question_chain(self, query):
        # Load prompt template from file
        prompt_template = self.load_prompt_template()
        
        # Create prompt template
        prompt_spbe = PromptTemplate(
            template=prompt_template,
            input_variables=["chat_history", "context", "question"]
        )
        chain = (
            RunnableParallel(
                {
                    "context" : self.retriever,
                    "question": RunnablePassthrough(),
                }
            )
            | prompt_spbe
            | self.llm_graph
            | StrOutputParser()
        )
        result = chain.invoke(query)
        return result


    