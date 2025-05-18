import streamlit as st
from langchain.schema import HumanMessage, AIMessage
import time

from modules_vectorbased.chain_handler import create_chain

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chain" not in st.session_state:
        st.session_state.chain = create_chain()
    if "db" not in st.session_state:
        st.session_state.db = None

initialize_session_state()

def reset_chat_history():
    """Reset chat history if requested"""
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.session_state.chain = create_chain()  # Reset the chain for a fresh start

def display_chat_history():
    """Display chat history in a scrollable area"""
    # Loop through state and display messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])
        if "source_documents" in msg and msg["source_documents"]:
            with st.expander("View Sources"):
                for i, doc in enumerate(msg["source_documents"]):
                    st.markdown(f"**Source {i+1}: {doc.metadata.get('source', 'N/A')}**")
                    st.caption(doc.page_content)
                    st.markdown("---")

def handle_user_input(user_input):
    """Process user input and generate response with streaming effect"""
    if not user_input:
        return
    
    # Add user message to history first
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Create a placeholder for the AI response
    with st.chat_message("assistant"):
        # Show typing indicator
        message_placeholder = st.empty()
        message_placeholder.markdown("*SPBEBOT merespons...*")
        
        try:
            # Get response from the chain
            result = st.session_state.chain({"question": user_input, "chat_history": st.session_state.chat_history})
            response = result["answer"]
            source_documents = result.get("source_documents", [])
            
            # Simulate streaming effect
            displayed_response = ""
            full_response = response
            
            for i in range(len(full_response)):
                displayed_response += full_response[i]
                message_placeholder.markdown(displayed_response + "▌")
                time.sleep(0.002)  # Adjust speed for natural feeling
                
            # Show final response without cursor
            message_placeholder.markdown(full_response)
            
            # Add AI response to history
            ai_message = {"role": "assistant", "content": response, "source_documents": source_documents}
            st.session_state.messages.append(ai_message)
            
            # Update langchain chat history
            st.session_state.chat_history.extend([
                HumanMessage(content=user_input),
                AIMessage(content=response)
            ])
            
            # Show source documents if available
            if source_documents:
                with st.expander("View Sources"):
                    for i, doc in enumerate(source_documents):
                        st.markdown(f"**Source {i+1}: {doc.metadata.get('source', 'N/A')}**")
                        st.caption(doc.page_content)
                        st.markdown("---")
                        
        except Exception as e:
            st.error(f"Error: {str(e)}")

def download_chat_history():
    """Create download button for chat history"""
    if st.session_state.get("messages"):
        chat_export_content = []
        for m in st.session_state.messages:
            entry = f"{m['role'].upper()}: {m['content']}"
            if "source_documents" in m and m["source_documents"]:
                entry += "\n\n[SOURCES]:"
                for i, doc in enumerate(m["source_documents"]):
                    source_name = doc.metadata.get('source', 'N/A')
                    entry += f"\n  Source {i+1}: {source_name}\n"
                    entry += f"  Content: {doc.page_content[:200]}...\n"
            chat_export_content.append(entry)
        
        content = "\n\n---\n\n".join(chat_export_content)
        st.download_button("💾 Download Chat History", content, file_name="chat_history_with_sources.txt", mime="text/plain")

def show_chatbot():
    """Main function to display the chatbot interface"""
    # Initialize session state variables first
    
    st.markdown('<h1 class="main-header">Chatbot Sistem Pemerintahan Berbasis Elektronik</h1>', unsafe_allow_html=True)
    
    st.markdown('<p class="paragraph">SPBEBOT adalah chatbot yang dirancang untuk memberikan informasi dan panduan tentang Sistem Pemerintahan Berbasis Elektronik (SPBE). Chatbot ini menggunakan teknologi Retrieval Augmented Generation (RAG) untuk mengakses informasi dari dokumen pedoman SPBE dan memberikan jawaban yang akurat.</p>', unsafe_allow_html=True)
        
    # Display chat history
    display_chat_history()
        
    # The chat input will be at the bottom
    user_input = st.chat_input("Pass your prompt here")
    if user_input:
        handle_user_input(user_input)
    
        # Show chat control buttons in a row, aligned to the right
    if st.session_state.get("messages"):
        col1, col2, col3 = st.columns([5,3,2], gap="small")  # Adjust ratio to push buttons to the right
        with col1:
            st.write("")  # Empty space to push buttons right
        with col2:
            download_chat_history()
        with col3:
            if st.button("🗑️ Clear Chat"):
                reset_chat_history()