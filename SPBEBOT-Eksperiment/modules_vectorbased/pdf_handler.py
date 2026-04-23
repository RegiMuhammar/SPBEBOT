import streamlit as st
import glob
import os
from pathlib import Path
import pandas as pd

from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.storage._lc_store import create_kv_docstore

# Initialize Embeddings model
my_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

@st.cache_data
def data_db_directories():
    """Initialize data and database directories."""
    # Current Directory
    current_dir = Path(__file__).parent
    # Up to parent directory 
    parent_dir = current_dir.parent
    # Get Data Folder
    data_path = parent_dir / "data"
    # Get DB Folder
    db_path = parent_dir / "db"
    # Get Docstore Folder
    docstore_path = parent_dir / "docstore"
    
    # Create Directory if not exist
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(db_path, exist_ok=True)
    os.makedirs(docstore_path, exist_ok=True)

    return data_path, db_path, docstore_path

data_path, db_path, docstore_path = data_db_directories()

def initialize_parent_retriever():
    """Initialize the parent document retriever."""
    # Create splitter for parent and child documents
    text_parent = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    text_child = RecursiveCharacterTextSplitter(
        chunk_size=400,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    # Create vector store for child documents
    db = Chroma(
        collection_name="spbe_parent_chunk_collection",
        embedding_function=my_embeddings,
        persist_directory=str(db_path)
    )
    
    # Create local file store for parent documents
    local_store = LocalFileStore(str(docstore_path))
    docstore = create_kv_docstore(local_store)
    
    # Create parent document retriever
    parent_retriever = ParentDocumentRetriever(
        vectorstore=db,
        docstore=docstore,
        child_splitter=text_child,
        parent_splitter=text_parent,
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    return parent_retriever, db, docstore

def get_parent_retriever():
    """Get the parent document retriever."""
    try:
        # Check if we already have a retriever in session state
        if "parent_retriever" in st.session_state and st.session_state.parent_retriever is not None:
            return st.session_state.parent_retriever
            
        # Initialize new retriever
        parent_retriever, db, docstore = initialize_parent_retriever()
        
        # Check if database has existing documents
        try:
            sample = db.get()
            if sample and sample.get('documents'):
                st.session_state.parent_retriever = parent_retriever
                st.session_state.db = db
                st.session_state.docstore = docstore
                st.session_state.documents_processed = True
                return parent_retriever
        except Exception:
            pass
            
        # If no existing documents, return None
        return None
        
    except Exception as e:
        st.error(f"Error getting parent retriever: {str(e)}")
        return None

@st.cache_data
def load_pdf_metadata(file_path):
    """Load PDF metadata with caching."""
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return {
            'total_page': len(pages),
            'preview': pages[0].page_content[:500] if pages else ''
        }
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")
        return None

def display_existing_files():
    """Display existing files in data directory in a table format."""
    if "show_documents" not in st.session_state:
        st.session_state.show_documents = False
    
    if st.button("Load Existing Documents"):
        st.session_state.show_documents = not st.session_state.show_documents
    
    if st.session_state.show_documents:
        existing_files = glob.glob(os.path.join(data_path, "*.pdf"))
        if existing_files:
            # Prepare data for table
            file_data = []
            for idx, file_path in enumerate(existing_files, 1):
                pdf_data = load_pdf_metadata(file_path)
                if pdf_data:
                    file_data.append({
                        'No': idx,
                        'Nama File': os.path.basename(file_path),
                        'Jumlah Halaman': pdf_data['total_page'],
                        'Preview': ' '.join(pdf_data['preview'].split()[:50]) + '...'
                    })
            
            # Create and display DataFrame
            df = pd.DataFrame(file_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            # Display summary
            st.info(f"Total files found: {len(file_data)}")
        else:
            st.info("No existing documents found.")

def handle_file_upload():
    """Handle new file uploads."""
    st.markdown("### Upload New Document")
    uploaded_files = st.file_uploader(
        "Upload PDF files here",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            destination_path = os.path.join(data_path, uploaded_file.name)
            with open(destination_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            st.success(f"File {uploaded_file.name} uploaded successfully!")

def process_documents():
    """Process all documents in the data directory."""
    st.markdown("### Process Documents")
    if st.button("Load and Process Documents"):
        # Initialize retriever
        parent_retriever, db, docstore = initialize_parent_retriever()
        st.session_state.parent_retriever = parent_retriever
        st.session_state.db = db
        st.session_state.docstore = docstore
        
        # Get all files in data directory
        existing_files = glob.glob(os.path.join(data_path, "*.pdf"))
        
        if not existing_files:
            st.info("No files found in data directory!")
            st.session_state.documents_processed = False
            return
            
        st.markdown("#### Processing Status")
        progress_bar = st.progress(0)
        
        # Process all files
        with st.spinner("Processing documents..."):
            for idx, file_path in enumerate(existing_files):
                filename = os.path.basename(file_path)
                try:
                    loader = PyPDFLoader(file_path)
                    documents = loader.load()
                    parent_retriever.add_documents(documents)
                    st.success(f"Successfully processed {filename}")
                except Exception as e:
                    st.error(f"Error processing {filename}: {str(e)}")
                
                progress = (idx + 1) / len(existing_files)
                progress_bar.progress(progress)
        
        # Verify final state
        try:
            sample = db.get()
            if sample and sample.get('documents'):
                st.success("Documents successfully processed and stored in the database.")
                st.session_state.documents_processed = True
            else:
                st.error("No documents found in the database after processing.")
                st.session_state.documents_processed = False
        except Exception as e:
            st.error(f"Error verifying final state: {str(e)}")
            st.session_state.documents_processed = False

def clear_database():
    """Clear the database and reset session state."""
    if "db" in st.session_state and st.session_state.db is not None:
        with st.spinner("Clearing database..."):
            try:
                st.session_state.db.delete_collection()
                st.session_state.db = None
                st.session_state.parent_retriever = None
                st.session_state.docstore = None
                # Clear docstore directory
                for file in os.listdir(docstore_path):
                    os.remove(os.path.join(docstore_path, file))
                st.success("Database cleared successfully.")
            except Exception as e:
                st.error(f"Error clearing database: {str(e)}")
    else:
        st.info("Database is already empty.")
