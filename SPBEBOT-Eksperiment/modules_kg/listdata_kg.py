import os
from pathlib import Path
import streamlit as st
import pandas as pd
from langchain.document_loaders import DirectoryLoader, PyPDFLoader

def get_file_metadata(file_path):
    """Get metadata from PDF file using Langchain's PyPDFLoader"""
    try:
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        return {
            'file_name': os.path.basename(file_path),
            'num_pages': len(pages),
            'file_type': 'PDF'
        }
    except Exception as e:
        st.error(f"Error reading file {file_path}: {str(e)}")
        return None

@st.cache_data # Cache for 1 hour
def load_documents(data_path):
    """Load documents with caching"""
    loader = DirectoryLoader(
        str(data_path),
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
        use_multithreading=True
    )
    return loader.load()

def list_data_files():
    """List all data files in the data directory using optimized loading"""
    try:
        # Initialize session state for file data if not exists
        if 'file_data' not in st.session_state:
            # Get the data directory path
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            data_path = parent_dir / "data"

            # Check if directory exists
            if not data_path.exists():
                st.error("Data directory not found!")
                return

            # Get all documents using cached loader
            documents = load_documents(data_path)
            
            if not documents:
                st.warning("No PDF files found in the data directory!")
                return

            # Get unique file paths from documents
            file_paths = list(set(doc.metadata.get('source') for doc in documents))
            
            # Get metadata for each file
            file_data = []
            for idx, file_path in enumerate(file_paths, 1):
                metadata = get_file_metadata(file_path)
                if metadata:
                    file_data.append({
                        'No': idx,
                        'Nama File': metadata['file_name'],
                        'Jumlah Halaman': metadata['num_pages'],
                        'Tipe File': metadata['file_type']
                    })
            
            # Store in session state
            st.session_state.file_data = file_data

        # Display the table using data from session state
        df = pd.DataFrame(st.session_state.file_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Display summary
        st.info(f"Total files found: {len(st.session_state.file_data)}")
        
    except Exception as e:
        st.error(f"Error listing data files: {str(e)}")

def show_data_list():
    """Main function to display the data list page"""    
    with st.spinner("Memuat data..."):
        list_data_files()