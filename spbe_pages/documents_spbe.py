import streamlit as st
from modules_vectorbased.pdf_handler import display_existing_files, handle_file_upload, process_documents

def show_documents():
    st.title("Documents SPBE")
    st.markdown("#### Existing Documents")
    display_existing_files()
    handle_file_upload()
    process_documents()