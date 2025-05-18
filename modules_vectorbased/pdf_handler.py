import streamlit as st
import tempfile
import glob
import shutil
import os
from pathlib import Path
import base64

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize session state variables
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()  # Store filenames
if "db" not in st.session_state:
    st.session_state.db = None


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

    # Create Directory if not exist
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(db_path, exist_ok=True)

    return data_path, db_path

data_path, db_path = data_db_directories()

@st.cache_data
def file_exists_in_db(filename):
    """Check if filename exists in the processed files."""
    return filename in st.session_state.processed_files

def process_single_pdf(file_path):
    """Process a single PDF file and add it to the vector database."""
    try:
        # Load single PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        # Embed and store in vector database
        embeddings = my_embeddings
        if st.session_state.db is None:
            st.session_state.db = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=str(db_path)  # Convert Path to string
            )
        else:
            # Add documents to existing DB
            st.session_state.db.add_documents(chunks)

        # Update session state
        st.session_state.processed_files.add(os.path.basename(file_path))
        
        return True, st.session_state.db
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return False, None

def get_vector_db():
    """Get the vector database from session state or create a new one if it doesn't exist."""
    if st.session_state.db is None:
        embeddings = my_embeddings
        st.session_state.db = Chroma(
            persist_directory=str(db_path),  # Convert Path to string
            embedding_function=embeddings
        )
    return st.session_state.db

if "pdf_cache" not in st.session_state:
    st.session_state.pdf_cache = {}  # Cache untuk menyimpan hasil loading PDF

@st.cache_data
def load_pdf_metadata(file_path):
    """Load PDF metadata with caching."""
    try:
        loader = PyPDFLoader(file_path)
        doc = loader.load()[0]
        return {
            'metadata': doc.metadata,
            'preview': doc.page_content[:500]  # Ambil 500 karakter pertama untuk preview
        }
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")
        return None

def display_existing_files():
    """Display existing files in data directory with expander."""
    if "show_documents" not in st.session_state:
        st.session_state.show_documents = False  # Store display state
    # Toggle display state when button is clicked
    if st.button("Load Existing Documents"):
        st.session_state.show_documents = not st.session_state.show_documents
    
    # Only display if show_documents is True
    if st.session_state.show_documents:
        existing_files = glob.glob(os.path.join(data_path, "*.pdf"))
        if existing_files:
            for file_path in existing_files:
                filename = os.path.basename(file_path)
                is_processed = file_exists_in_db(filename)
                
                with st.expander(f"{filename} {'✅' if is_processed else '⏳'}"):
                    # Load PDF data with caching
                    pdf_data = load_pdf_metadata(file_path)
                    if pdf_data:
                        # Display metadata
                        st.markdown("#### Metadata")
                        for key, value in pdf_data['metadata'].items():
                            if key == 'source':
                                continue
                            st.text(f"{key}: {value}")
                        
                        # Display processing status
                        if is_processed:
                            st.badge("Processed", icon="✅", color="green")
                        else:
                            st.badge("Not Processed", icon="⏳", color="orange")
                        
                        # Display PDF preview
                        st.markdown("#### Preview")
                        preview_text = ' '.join(pdf_data['preview'].split()[:100])
                        
                        # Display in a nice box
                        st.markdown(f"""
                        <div style="
                            padding: 1rem;
                            border: 1px solid #ddd;
                            border-radius: 5px;
                            margin: 1rem 0;
                        ">
                            {preview_text}...
                        </div>
                        """, unsafe_allow_html=True)
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
            # Save file to data directory
            destination_path = os.path.join(data_path, uploaded_file.name)
            with open(destination_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            st.success(f"File {uploaded_file.name} uploaded successfully!")

def process_documents():
    """Process unprocessed documents."""
    st.markdown("### Process Documents")
    if st.button("Load and Process Documents"):
        # Get all unprocessed files (files not yet in database)
        existing_files = glob.glob(os.path.join(data_path, "*.pdf"))
        unprocessed_files = [f for f in existing_files if not file_exists_in_db(os.path.basename(f))]
        
        if not unprocessed_files:
            st.info("No new files to process!")
            return
            
        st.markdown("#### Processing Status")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process files one by one for better progress tracking
        for idx, file_path in enumerate(unprocessed_files):
            filename = os.path.basename(file_path)
            status_text.text(f"Processing {filename}... Please wait...")
            
            with st.spinner(f"Processing {filename}..."):
                try:
                    success, db = process_single_pdf(file_path)
                    if success:
                        st.success(f"Successfully processed {filename}")
                    else:
                        st.error(f"Failed to process {filename}")
                except Exception as e:
                    st.error(f"Error processing {filename}: {str(e)}")
            
            # Update progress
            progress = (idx + 1) / len(unprocessed_files)
            progress_bar.progress(progress)
        
        status_text.text("Processing completed!") 