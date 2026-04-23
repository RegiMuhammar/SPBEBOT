import streamlit as st
from modules_vectorbased.pdf_handler import display_existing_files, handle_file_upload, process_documents, clear_database

def show_documents():
    st.title("Documents SPBE")
    st.markdown("#### Existing Documents")
    display_existing_files()
    handle_file_upload()
    process_documents()
    
    # Add clear database button
    st.markdown("---")
    if st.button("🗑️ Clear Database", type="primary"):
        clear_database()
        # st.rerun()  # Refresh the page after clearing