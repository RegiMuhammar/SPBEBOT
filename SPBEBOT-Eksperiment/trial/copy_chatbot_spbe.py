# import streamlit as st
# from dotenv import load_dotenv
# import os
# import tempfile

# from langchain_community.document_loaders import PyPDFLoader
# from langchain.vectorstores import Chroma # type: ignore
# from langchain_ollama import OllamaEmbeddings # type: ignore

# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory

# from langchain_groq import ChatGroq # type: ignore


# # # Load .env
# # load_dotenv()

# # # Temp dir for vector store
# # VECTOR_DIR = "./chroma_spbe_parent_db"

# # # Initialize Chat Model
# # llm = ChatGroq(model_name="llama-3.3-70b-versatile", 
# #                temperature=0, 
# #                groq_api_key=os.getenv("GROQ_API_KEY")
# #                )

# # # Memory
# # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# # # File loader
# # def process_documents(files):
# #     all_text = ""
# #     all_pages = []
# #     for pdf in files:
# #         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
# #             tmp.write(pdf.read())
# #             tmp_path = tmp.name
# #         loader = PyPDFLoader(tmp_path)
# #         pages = loader.load_and_split()
# #         all_pages.extend(pages)
# #         os.unlink(tmp_path)
# #     return all_pages

# # # Vectorstore
# # def build_vectorstore(documents):
# #     embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
# #     vectordb = Chroma.from_documents(documents, embedding=embeddings, persist_directory=VECTOR_DIR)
# #     vectordb.persist()
# #     return vectordb

# # # Chatbot
# # def setup_qa_chain(vectordb):
# #     retriever = vectordb.as_retriever(search_kwargs={"k": 3})
# #     qa_chain = ConversationalRetrievalChain.from_llm(
# #         llm=llm,
# #         retriever=retriever,
# #         memory=memory,
# #         return_source_documents=True
# #     )   
# #     return qa_chain

# # # --- Streamlit UI ---
# # st.markdown('<h1>SPBEBOT Chatbot</h1>', unsafe_allow_html=True)

# # # Chatbot area
# # with st.container():
# #     # Column layout like WhatsApp: input + upload + send
# #     col1, col2, col3 = st.columns([6, 1, 1])
# #     with col1:
# #         user_input = st.text_input("Type a message...", key="input", label_visibility="collapsed")
# #     with col2:
# #         uploaded_files = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
# #     with col3:
# #         send_button = st.button("➤", use_container_width=True)

# # # Session states
# # if "chat_history" not in st.session_state:
# #     st.session_state.chat_history = []
# # if "qa_chain" not in st.session_state:
# #     st.session_state.qa_chain = None

# # # Build chain if files uploaded
# # if uploaded_files and st.session_state.qa_chain is None:
# #     with st.spinner("Processing documents and building vectorstore..."):
# #         docs = process_documents(uploaded_files)
# #         vectordb = build_vectorstore(docs)
# #         qa_chain = setup_qa_chain(vectordb)
# #         st.session_state.qa_chain = qa_chain

# # # Chat interaction
# # if send_button and user_input:
# #     if st.session_state.qa_chain is not None:
# #         with st.spinner("Thinking..."):
# #             result = st.session_state.qa_chain({"question": user_input})
# #             st.session_state.chat_history.append(("You", user_input))
# #             st.session_state.chat_history.append(("SPBEBOT", result["answer"]))
# #     else:
# #         st.warning("Please upload PDF documents first.")

# # # Display chat
# # for sender, message in st.session_state.chat_history:
# #     st.markdown(f"**{sender}:** {message}")




# # import streamlit as st
# # from dotenv import load_dotenv
# # import tempfile
# # import os

# # from langchain_community.document_loaders import PyPDFLoader

# # def get_docs_text(spbe_docs):
# #     """Process PDF documents and return text"""
# #     text = ""
# #     for pdf_file in spbe_docs:
# #         # Create a temporary file
# #         with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
# #             # Write the uploaded file content to the temporary file
# #             tmp_file.write(pdf_file.getvalue())
# #             tmp_file_path = tmp_file.name
        
# #         try:
# #             # Load the PDF from the temporary file
# #             pdf_reader = PyPDFLoader(tmp_file_path)
# #             for page in pdf_reader.pages:
# #                 text += page.extract_text()
# #         finally:
# #             # Clean up the temporary file
# #             os.unlink(tmp_file_path)
    
# #     return text

# # Content for Chatbot
# def show_chatbot():
#     st.markdown('<h1 class="main-header">Chatbot Sistem Pemerintahan Berbasis Elektronik</h1>', unsafe_allow_html=True)
    
#     st.markdown('<p class="paragraph">SPBEBOT adalah chatbot yang dirancang untuk memberikan informasi dan panduan tentang Sistem Pemerintahan Berbasis Elektronik (SPBE). Chatbot ini menggunakan teknologi Retrieval Augmented Generation (RAG) untuk mengakses informasi dari dokumen pedoman SPBE dan memberikan jawaban yang akurat.</p>', unsafe_allow_html=True)
    
#     tabs = st.tabs(["SPBE Documents","SPBEBOT", "Dashboard Indeks SPBE"])
    
#     # SPBEBOT Tab
#     with tabs[0]:
#         # step 1: upload pdf and submit

#         # step 2: process pdf to vector store
#         st.subheader("SPBE Documents")
#         spbe_docs = st.file_uploader(
#             "Upload the PDF here and click 'Process'",
#             type="pdf",
#             accept_multiple_files=True)
#         if st.button("Process"):
#             if spbe_docs:
#                 with st.spinner("Processing"):
#                     # get docs text
#                     raw_text = get_docs_text(spbe_docs)
#                     st.write(raw_text)
#             else:
#                 st.warning("Please upload PDF files first!")

#     # SPBEBOT Tab
#     with tabs[1]:
#         chat_history=[]
#         vector_store=[]
           
#     # Dashboard Indeks SPBE Tab
#     with tabs[2]:
#         st.markdown('<h2 class="sub-header">Dashboard Indeks SPBE</h2>', unsafe_allow_html=True)
        
#         # Total Index Value
#         st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
#         st.markdown('<h3>Nilai Indeks Total</h3>', unsafe_allow_html=True)
#         st.markdown('<div class="metric-value">3.47</div>', unsafe_allow_html=True)
#         st.markdown('<div class="progress-container"><div class="progress-bar" style="width: 69.4%;"></div></div>', unsafe_allow_html=True)
#         st.markdown('</div>', unsafe_allow_html=True)
        
#         # Domain Values
#         st.markdown('<h3>Domain</h3>', unsafe_allow_html=True)
        
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
#             st.markdown('<div class="metric-label">Domain 1</div>', unsafe_allow_html=True)
#             st.markdown('<div class="metric-value">3.52</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)
            
#         with col2:
#             st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
#             st.markdown('<div class="metric-label">Domain 2</div>', unsafe_allow_html=True)
#             st.markdown('<div class="metric-value">3.65</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)
            
#         with col3:
#             st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
#             st.markdown('<div class="metric-label">Domain 3</div>', unsafe_allow_html=True)
#             st.markdown('<div class="metric-value">3.40</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)
            
#         with col4:
#             st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
#             st.markdown('<div class="metric-label">Domain 4</div>', unsafe_allow_html=True)
#             st.markdown('<div class="metric-value">3.31</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)
        
#         # Aspects and Indicators
#         st.markdown('<h3>Aspek</h3>', unsafe_allow_html=True)
        
#         aspects = [
#             {"name": "Aspek 1", "value": 3.58, "indicators": [3.7, 3.6, 3.5, 3.4, 3.7]},
#             {"name": "Aspek 2", "value": 3.42, "indicators": [3.5, 3.3, 3.4, 3.5, 3.4]},
#             {"name": "Aspek 3", "value": 3.61, "indicators": [3.8, 3.5, 3.6, 3.7, 3.5]},
#             {"name": "Aspek 4", "value": 3.35, "indicators": [3.3, 3.4, 3.3, 3.4, 3.4]},
#             {"name": "Aspek 5", "value": 3.52, "indicators": [3.6, 3.5, 3.5, 3.4, 3.6]},
#             {"name": "Aspek 6", "value": 3.44, "indicators": [3.5, 3.4, 3.3, 3.5, 3.5]},
#             {"name": "Aspek 7", "value": 3.38, "indicators": [3.4, 3.3, 3.4, 3.3, 3.5]},
#             {"name": "Aspek 8", "value": 3.48, "indicators": [3.5, 3.5, 3.4, 3.6, 3.4]}
#         ]
        
#         for aspect in aspects:
#             with st.expander(f"{aspect['name']} - {aspect['value']}"):
#                 st.markdown('<table class="indikator-table" width="100%">', unsafe_allow_html=True)
#                 st.markdown('<tr><th>Indikator 1</th><th>Indikator 2</th><th>Indikator 3</th><th>Indikator 4</th><th>Indikator 5</th></tr>', unsafe_allow_html=True)
                
#                 indicator_values = '</td><td>'.join([str(ind) for ind in aspect["indicators"]])
#                 st.markdown(f'<tr><td>{indicator_values}</td></tr>', unsafe_allow_html=True)
                
#                 st.markdown('</table>', unsafe_allow_html=True)

# # -------------------------------------------

# import streamlit as st
# import tempfile
# import glob
# import shutil
# import os
# from pathlib import Path

# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# # Initialize session state variables
# if "processed_files" not in st.session_state:
#     st.session_state.processed_files = set()  # Store filenames
# if "db" not in st.session_state:
#     st.session_state.db = None

# def data_db_directories():
#     """Initialize data and database directories."""
#     # Current Directory
#     current_dir = Path(__file__).parent

#     # Up to parent directory 
#     parent_dir = current_dir.parent

#     # Get Data Folder
#     data_path = parent_dir / "data"

#     # Get DB Folder
#     db_path = parent_dir / "db"

#     # Create Directory if not exist
#     os.makedirs(data_path, exist_ok=True)
#     os.makedirs(db_path, exist_ok=True)

#     return data_path, db_path

# data_path, db_path = data_db_directories()


# def file_exists_in_db(filename):
#     """Check if filename exists in the processed files."""
#     return filename in st.session_state.processed_files

# def process_pdf(file_path):
#     """Load, chunk, and embed PDF content into the vector database."""
#     try:
#         # Use DirectoryLoader to load PDF
#         loader = DirectoryLoader(
#             str(data_path),
#             glob="**/*.pdf",
#             loader_cls=PyPDFLoader,
#             loader_kwargs={
#                 "extract_images": True,
#                 "extract_metadata": True
#             }
#         )
#         documents = loader.load()

#         # Split into chunks
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len,
#             separators=["\n\n", "\n", " ", ""]
#         )
#         chunks = text_splitter.split_documents(documents)

#         # Embed and store in vector database
#         embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
#         if st.session_state.db is None:
#             st.session_state.db = Chroma.from_documents(
#                 documents=chunks,
#                 embedding=embeddings,
#                 persist_directory=db_path
#             )
#         else:
#             # Add documents to existing DB
#             st.session_state.db.add_documents(chunks)

#         # Update session state
#         st.session_state.processed_files.append(file_path)
        
#         return True
#     except Exception as e:
#         st.error(f"Error processing PDF: {str(e)}")
#         return False


# def upload_files():
#     """Handle PDF file uploads and processing."""
#     st.subheader("SPBE Documents")
#     uploaded_files = st.file_uploader(
#         "Upload the PDF here and click 'Process'",
#         type="pdf",
#         accept_multiple_files=True
#     )
    
#     if uploaded_files:
#         for uploaded_file in uploaded_files:
#             # check if file already exists in database by filename
#             if file_exists_in_db(uploaded_file.name):
#                 st.info(f"File '{uploaded_file.name}' has already been processed.")
#             else:
#                 # save the uploaded file temporarily
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#                     tmp_file.write(uploaded_file.getvalue())
#                     temp_path = tmp_file.name

#                 # Save file to data directory
#                 destination_path = os.path.join(data_path, uploaded_file.name)
#                 shutil.copy(temp_path, destination_path)

#                 with st.spinner(f"Processing {uploaded_file.name}..."):
#                     file_processed = process_pdf(destination_path)
#                     if file_processed:
#                         st.session_state.processed_files.add(uploaded_file.name)
#                         st.success(f"Successfully processed {uploaded_file.name}")
#                     else:
#                         st.error(f"Failed to process {uploaded_file.name}")

#                 # Remove temporary file
#                 os.unlink(temp_path)

#     # Process existing files in data directory
#     st.markdown('<p class="paragraph">Or load existing PDF files from the data directory.</p>', unsafe_allow_html=True)
#     if st.button("Load Existing PDF Files"):
#         existing_files = glob.glob(os.path.join(data_path, "*.pdf"))
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
#     if not st.session_state.db and os.path.exists(db_path) and os.listdir(db_path):
#         with st.spinner("Loading existing database..."):
#             try:
#                 embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
#                 st.session_state.db = Chroma(persist_directory=db_path, embedding_function=embeddings)
#                 st.success("Loaded existing database!")
#             except Exception as e:
#                 st.error(f"Error loading database: {str(e)}")