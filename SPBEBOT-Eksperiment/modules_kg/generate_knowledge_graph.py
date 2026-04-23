from pyvis.network import Network
import networkx as nx
from py2neo import Graph
from modules_kg.knowledge_graph_neo4j import SPBE_GraphRAG_Neo4J
import streamlit as st
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components
import sys

def generate_spbe_knowledge_graph():
    try:
        spbe_graph = SPBE_GraphRAG_Neo4J()
        
        # Create knowledge graph with progress bar
        with st.spinner("Creating Knowledge Graph..."):
            progress_bar = st.progress(0)
            spbe_graph.create_graph()  # This will use the async implementation
            progress_bar.progress(100)
            st.success("Knowledge Graph Created Successfully!")
        
        # Create vector index
        with st.spinner("Creating Vector Index..."):
            spbe_graph.create_vector_index()
            st.success("Vector Index Created Successfully!")
        
        
    except Exception as e:
        st.error(f"Error in graph generation process: {str(e)}")
        raise e

def show_spbe_graph():
    # Load env
    load_dotenv()
    
    # Get Neo4J credentials
    uri = os.environ.get('NEO4J_URI_regguy')
    user = os.environ.get('NEO4J_USERNAME_regguy')
    password = os.environ.get('NEO4J_PASSWORD_regguy')

    # Load Graph Button
    if st.button("Show SPBE Graph"):
        try:
            data = get_spbe_graph_data(uri, user, password)
            G = create_networkx_graph(data)
            visualize_graph(G)

            HtmlFile = open("spbe_graph.html", "r", encoding="utf-8")
            source_code = HtmlFile.read()
            components.html(source_code, height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error loading graph: {e}")

def get_spbe_graph_data(uri, user, password):
    # Initialize Neo4j connection properly
    graph = Graph(uri, auth=(user,password))
    query = """
            MATCH (n)-[r]->(m)
            RETURN n, r, m
            LIMIT 100
            """
    # Execute Cypher query to get graph data from Neo4J
    data = graph.query(query)
    return data

def create_networkx_graph(data):
    G = nx.DiGraph()
    for record in data:
        n = record['n']
        m = record['m']
        r = record['r']        
        # Add nodes with their labels
        G.add_node(n['id'], label=n['name'])
        G.add_node(m['id'], label=m['name'])
        # Add edge with relationship type
        G.add_edge(n['id'], m['id'], label=r['type'])
    return G

def visualize_graph(G):
    net = Network(notebook=True, directed=True)
    # Tambahkan node
    for node, data in G.nodes(data=True):
        net.add_node(node, label=data.get('label', str(node)))
    # Tambahkan edge dengan label
    for source, target, data in G.edges(data=True):
        net.add_edge(source, target, label=data.get('label', ''))
    net.show("spbe_graph.html")