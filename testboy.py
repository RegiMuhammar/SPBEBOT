# import os
# import streamlit as st
# import tempfile
# import shutil
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_groq import ChatGroq
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import PromptTemplate
# import glob

# # Constants
# DATA_DIR = "./data"
# DB_DIR = "./db"

# # Create directories if they don't exist
# os.makedirs(DATA_DIR, exist_ok=True)
# os.makedirs(DB_DIR, exist_ok=True)

# # Initialize Streamlit app
# st.set_page_config(page_title="SPBEBOT", layout="wide")
# st.title("SPBEBOT")
# st.markdown("### RAG-based Chatbot with PDF Knowledge Base")

# # Set environment variables from secrets if available
# if "GROQ_API_KEY" not in os.environ and hasattr(st.secrets, "GROQ_API_KEY"):
#     os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# # Initialize session state variables
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "processed_files" not in st.session_state:
#     st.session_state.processed_files = set()  # Store filenames instead of hashes
# if "db" not in st.session_state:
#     st.session_state.db = None
# if "memory" not in st.session_state:
#     st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# # Define the prompts
# PROMPT_TEMPLATES = {
#     "default": """You are a helpful AI assistant. Use the following context to answer the question.
    
#     Context: {context}
    
#     Chat History: {chat_history}
    
#     Question: {question}
    
#     Answer:""",
    
#     "math": """You are a specialized math tutor. Use the following context to answer the mathematical question.
    
#     Context: {context}
    
#     Chat History: {chat_history}
    
#     Question: {question}
    
#     Please solve the problem step by step, explaining the mathematical concepts and formulas used:""",
    
#     "biology": """You are a biology expert. Use the following context to answer the biology question.
    
#     Context: {context}
    
#     Chat History: {chat_history}
    
#     Question: {question}
    
#     Provide a comprehensive biological explanation, mentioning relevant processes, structures, and mechanisms:"""
# }

# # Function to check if file exists in database
# def file_exists_in_db(filename):
#     """Check if filename exists in the processed files."""
#     return filename in st.session_state.processed_files

# # Function to process PDF file
# def process_pdf(file_path):
#     """Load, chunk, and embed PDF content into the vector database."""
#     try:
#         # Load PDF
#         loader = PyPDFLoader(file_path)
#         documents = loader.load()
        
#         # Chunk documents
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         chunks = text_splitter.split_documents(documents)
        
#         # Create or update vector database
#         embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
        
#         if st.session_state.db is None:
#             st.session_state.db = Chroma.from_documents(
#                 documents=chunks,
#                 embedding=embeddings,
#                 persist_directory=DB_DIR
#             )
#         else:
#             # Add documents to existing DB
#             st.session_state.db.add_documents(chunks)
            
#         return True
#     except Exception as e:
#         st.error(f"Error processing PDF: {str(e)}")
#         return False

# # Function to create RAG chain
# def create_chain(prompt_type="default"):
#     """Create a conversational chain with the selected prompt template."""
#     if st.session_state.db is None:
#         return None
    
#     # Get prompt template
#     prompt = PromptTemplate(
#         input_variables=["context", "chat_history", "question"],
#         template=PROMPT_TEMPLATES[prompt_type]
#     )
    
#     # Initialize LLM
#     llm = ChatGroq(
#         model_name="llama-3.3-70b-versatile", 
#         temperature=0,
#         groq_api_key=os.environ.get("GROQ_API_KEY")
#     )
    
#     # Create chain
#     chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=st.session_state.db.as_retriever(search_kwargs={"k": 3}),
#         memory=st.session_state.memory,
#         combine_docs_chain_kwargs={"prompt": prompt},
#         return_source_documents=True
#     )
    
#     return chain

# # This section was removed as it's now replaced by the file_exists_in_db function above

# # Sidebar - File Upload and Settings
# with st.sidebar:
#     st.header("Settings")
    
#     # Prompt template selection
#     prompt_type = st.selectbox(
#         "Select Prompt Template",
#         options=["default", "math", "biology"],
#         index=0
#     )
    
#     st.header("Upload PDFs")
#     uploaded_files = st.file_uploader(
#         "Upload PDF files", 
#         type="pdf", 
#         accept_multiple_files=True
#     )
    
#     if uploaded_files:
#         for uploaded_file in uploaded_files:
#             # Check if file already exists in database by filename
#             if file_exists_in_db(uploaded_file.name):
#                 st.info(f"File '{uploaded_file.name}' has already been processed.")
#             else:
#                 # Save the uploaded file temporarily
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#                     tmp_file.write(uploaded_file.getvalue())
#                     temp_path = tmp_file.name
                
#                 # Save file to data directory
#                 destination_path = os.path.join(DATA_DIR, uploaded_file.name)
#                 shutil.copy(temp_path, destination_path)
                
#                 with st.spinner(f"Processing {uploaded_file.name}..."):
#                     success = process_pdf(destination_path)
#                     if success:
#                         st.session_state.processed_files.add(uploaded_file.name)
#                         st.success(f"Successfully processed {uploaded_file.name}")
#                     else:
#                         st.error(f"Failed to process {uploaded_file.name}")
                
#                 # Remove temporary file
#                 os.unlink(temp_path)
    
#     # Process existing files in data directory
#     if st.button("Load Existing PDF Files"):
#         existing_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
#         if existing_files:
#             for file_path in existing_files:
#                 filename = os.path.basename(file_path)
                
#                 if file_exists_in_db(filename):
#                     st.info(f"File '{filename}' has already been processed.")
#                 else:
#                     with st.spinner(f"Processing {filename}..."):
#                         success = process_pdf(file_path)
#                         if success:
#                             st.session_state.processed_files.add(filename)
#                             st.success(f"Successfully processed {filename}")
#                         else:
#                             st.error(f"Failed to process {filename}")
#         else:
#             st.info("No PDF files found in the data directory.")
    
#     # Load database if available
#     if not st.session_state.db and os.path.exists(DB_DIR) and os.listdir(DB_DIR):
#         with st.spinner("Loading existing database..."):
#             try:
#                 embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
#                 st.session_state.db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
#                 st.success("Loaded existing database!")
#             except Exception as e:
#                 st.error(f"Error loading database: {str(e)}")

# # Display chat messages
# st.header("Chat")
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

# # Get user input
# user_query = st.chat_input("Ask me anything...")

# # Process user input
# if user_query:
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": user_query})
    
#     # Display user message
#     with st.chat_message("user"):
#         st.write(user_query)
    
#     # Check if database exists
#     if st.session_state.db is None:
#         with st.chat_message("assistant"):
#             st.write("Please upload PDF files first to build the knowledge base.")
#         st.session_state.messages.append({"role": "assistant", "content": "Please upload PDF files first to build the knowledge base."})
#     else:
#         # Create chain with selected prompt template
#         chain = create_chain(prompt_type)
        
#         # Generate response
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 try:
#                     response = chain.invoke({"question": user_query})
#                     st.write(response["answer"])
#                     st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
#                 except Exception as e:
#                     error_msg = f"Error generating response: {str(e)}"
#                     st.error(error_msg)
#                     st.session_state.messages.append({"role": "assistant", "content": error_msg})