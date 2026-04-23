import streamlit as st
from modules_kg.knowledge_graph_neo4j import SPBE_GraphRAG_Neo4J
from langchain.schema import HumanMessage, AIMessage
import time

def initialize_session_state():
    """Initialize session state variables"""
    if "messages_graphrag" not in st.session_state:
        st.session_state.messages_graphrag = []
    if "chat_history_graphrag" not in st.session_state:
        st.session_state.chat_history_graphrag = []
        
    # Add welcome message if messages is empty
    if not st.session_state.messages_graphrag:
        welcome_message_graphrag = "Halo, silahkan tanyakan terkait evaluasi SPBE"
        st.session_state.messages_graphrag.append({"role": "assistant", "content": welcome_message_graphrag})

def reset_chat_history():
    """Reset chat history if requested"""
    try:
        # Reset messages and chat history
        st.session_state.messages_graphrag = []
        st.session_state.chat_history_graphrag = []
        
        # Add welcome message
        welcome_message_graphrag = "Halo, silahkan tanyakan terkait evaluasi SPBE"
        st.session_state.messages_graphrag.append({"role": "assistant", "content": welcome_message_graphrag})
    except Exception as e:
        st.error(f"Error resetting chat: {str(e)}")

def display_chat_history():
    """Display chat history in a scrollable area"""
    for msg in st.session_state.messages_graphrag:
        st.chat_message(msg["role"]).markdown(msg["content"])
        if "source_documents" in msg and msg["source_documents"]:
            with st.expander("View Sources"):
                for i, doc in enumerate(msg["source_documents"]):
                    st.markdown(f"**Source {i+1}: {doc.metadata.get('source', 'N/A')}**")
                    st.caption(doc.page_content)
                    st.markdown("---")

def handle_user_input(user_input_graphrag):
    """Process user input and generate response with streaming effect"""
    if not user_input_graphrag:
        return
    
    # Add user message to history first
    st.chat_message("user").markdown(user_input_graphrag)
    st.session_state.messages_graphrag.append({"role": "user", "content": user_input_graphrag})
    
    # Create a placeholder for the AI response
    with st.chat_message("assistant"):
        # Show typing indicator
        message_placeholder_graphrag = st.empty()
        message_placeholder_graphrag.markdown("*SPBEBOT merespons...*")
        
        try:
            # Initialize GraphRAG only when needed
            graphrag = SPBE_GraphRAG_Neo4J()
            
            # Get response from GraphRAG
            response_graphrag = graphrag.ask_question_chain(user_input_graphrag)
            context = graphrag.retriever(user_input_graphrag)
            
            # Simulate streaming effect
            displayed_response_graphrag = ""
            full_response = response_graphrag
            
            for i in range(len(full_response)):
                displayed_response_graphrag += full_response[i]
                message_placeholder_graphrag.markdown(displayed_response_graphrag + "▌")
                time.sleep(0.002)  # Adjust speed for natural feeling
                
            # Show final response without cursor
            message_placeholder_graphrag.markdown(full_response)
            
            # Add AI response to history
            ai_message = {"role": "assistant", "content": response_graphrag}
            st.session_state.messages_graphrag.append(ai_message)
            
            # Update langchain chat history
            st.session_state.chat_history_graphrag.extend([
                HumanMessage(content=user_input_graphrag),
                AIMessage(content=response_graphrag)
            ])
            
            # Tampilkan context hasil retrieval
            with st.expander("View Sources"):
                st.markdown(context)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

def download_chat_history():
    """Create download button for chat history"""
    if st.session_state.get("messages_graphrag"):
        chat_export_content_graphrag = []
        for m in st.session_state.messages_graphrag:
            entry = f"{m['role'].upper()}: {m['content']}"
            if "source_documents" in m and m["source_documents"]:
                entry += "\n\n[SOURCES]:"
                for i, doc in enumerate(m["source_documents"]):
                    source_name = doc.metadata.get('source', 'N/A')
                    entry += f"\n  Source {i+1}: {source_name}\n"
                    entry += f"  Content: {doc.page_content[:100]}...\n"
            chat_export_content_graphrag.append(entry)
        
        content = "\n\n---\n\n".join(chat_export_content_graphrag)
        st.download_button("💾 Download Chat History", content, file_name="chat_history_graphrag.txt", mime="text/plain")

def show_graphrag_chatbot():
    """Main function to display the knowledge graph chatbot interface"""
    try:
        # Initialize session state variables first
        initialize_session_state()
        
        st.markdown('<h1 class="main-header">GraphRAG SPBEBOT</h1>', unsafe_allow_html=True)
        st.markdown('<p class="paragraph">GraphRAG SPBEBOT adalah Chatbot untuk membantu asesor dalam mengevaluasi Sistem Pemerintahan Berbasis Elektronik (SPBE) dengan menggunakan teknik Retrieval Augmented Generation (RAG) dan Knowledge Graph untuk memperkaya konteks jawaban.</p>', unsafe_allow_html=True)
        
        # Display chat history
        display_chat_history()
            
        # The chat input will be at the bottom
        user_input_graphrag = st.chat_input("Tanya terkait evaluasi SPBE")
        if user_input_graphrag:
            handle_user_input(user_input_graphrag)
        
        # Show chat control buttons in a row, aligned to the right
        if st.session_state.get("messages_graphrag"):
            col1, col2, col3 = st.columns([5,3,2], gap="small")  # Adjust ratio to push buttons to the right
            with col1:
                st.write("")  # Empty space to push buttons right
            with col2:
                download_chat_history()
            with col3:
                if st.button("🗑️ Clear Chat"):
                    reset_chat_history()
                    
    except Exception as e:
        st.error(f"Error in show_graphrag_chatbot: {str(e)}") 