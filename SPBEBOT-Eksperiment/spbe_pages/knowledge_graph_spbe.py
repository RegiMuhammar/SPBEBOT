# Import necessary modules
import streamlit as st
from modules_kg.generate_knowledge_graph import generate_spbe_knowledge_graph, show_spbe_graph
from modules_kg.knowledge_graph_neo4j import SPBE_GraphRAG_Neo4J
from modules_kg.listdata_kg import show_data_list

def check_neo4j_connection():
    """Check Neo4j database connection"""
    try:
        # Try to initialize GraphRAG
        graphrag = SPBE_GraphRAG_Neo4J()
        return True, "Koneksi ke Neo4j berhasil!"
    except Exception as e:
        return False, f"❌ Koneksi ke Neo4j gagal: {str(e)}"

def show_knowledge_graph():
    st.title("Knowledge Graph SPBE") 
    st.markdown("""
    This page allows you to generate and visualize the SPBE Knowledge Graph with hybrid search capabilities.
    The process includes:
    1. Creating the Knowledge Graph
    2. Creating Vector Index for hybrid search
    3. Visualizing the graph
    """)

    show_data_list()

    # Connection check button
    if st.button("🔌 Cek Koneksi Neo4j", type="secondary"):
        is_connected, message = check_neo4j_connection()
        if is_connected:
            st.success(message)
        else:
            st.error(message)

    if st.button("Process Knowledge Graph", type="primary"):
        try:
            generate_spbe_knowledge_graph()
        except Exception as e:
            st.error(f"Error in Knowledge Graph Generation: {str(e)}")
            st.stop()

            # Show the graph
    show_spbe_graph()

    st.session_state.messages1 = []
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages1 =[]
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages1:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Test Graph Query
    input_query = st.chat_input("Ask question to graph query result...")
    
    if input_query:  # Only process if there is input
        #Display user message in chat message container
        st.chat_message("user").markdown(input_query)
        #Add user message to chat history
        st.session_state.messages1.append({"role":"user","context":input_query})

        # Get response from retriever
        graph_retriever = SPBE_GraphRAG_Neo4J()
        graph_retriever.prepare_cypher_chat_template()
        response_query = graph_retriever.retriever(input_query)

        #Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response_query)

        st.session_state.messages1.append({'role':"assistant", "content": response_query})