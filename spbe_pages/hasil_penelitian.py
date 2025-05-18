import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Content for Hasil Penelitian
def show_research_results():
    st.markdown('<h1 class="main-header">Hasil Penelitian</h1>', unsafe_allow_html=True)
    
    st.markdown('<p class="paragraph">Halaman ini menampilkan hasil pengukuran evaluasi SPBEBOT dalam menjawab pertanyaan terkait SPBE. Evaluasi dilakukan terhadap dua sistem RAG (Retrieval Augmented Generation) yang berbeda untuk mengukur kualitas jawaban yang dihasilkan.</p>', unsafe_allow_html=True)
    
    # Create dummy data for evaluation results
    eval_data = {
        'Metrik': ['Context Recall', 'Context Precision', 'Faithfulness', 'Answer Relevance', 'Answer Correctness'],
        'RAG Sistem 1': [0.85, 0.78, 0.92, 0.87, 0.83],
        'RAG Sistem 2': [0.79, 0.82, 0.88, 0.85, 0.86]
    }
    
    df = pd.DataFrame(eval_data)
    
    # Display evaluation results table
    st.markdown('<h2 class="sub-header">Hasil Evaluasi Sistem RAG</h2>', unsafe_allow_html=True)
    st.table(df)
    
    # Create and display chart
    st.markdown('<h2 class="sub-header">Perbandingan Sistem RAG</h2>', unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(eval_data['Metrik']))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, eval_data['RAG Sistem 1'], width, label='RAG Sistem 1', color='#1a73e8')
    rects2 = ax.bar(x + width/2, eval_data['RAG Sistem 2'], width, label='RAG Sistem 2', color='#ea4335')
    
    ax.set_ylim(0, 1)
    ax.set_ylabel('Skor')
    ax.set_title('Perbandingan Performa Sistem RAG')
    ax.set_xticks(x)
    ax.set_xticklabels(eval_data['Metrik'])
    ax.legend()
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Additional detail tables
    st.markdown('<h2 class="sub-header">Detail Evaluasi per Kategori Pertanyaan</h2>', unsafe_allow_html=True)
    
    # Create dummy data for detailed evaluation
    categories = ['Umum', 'Kebijakan', 'Implementasi', 'Teknis', 'Evaluasi']
    metrics = ['Context Recall', 'Context Precision', 'Faithfulness']
    
    # Create tabs for each category
    tabs = st.tabs(categories)
    
    for i, tab in enumerate(tabs):
        with tab:
            # Generate random data for each category
            np.random.seed(i)  # For reproducibility
            data = {
                'Pertanyaan': [f'Pertanyaan {j+1}' for j in range(5)],
                'Context Recall': np.random.uniform(0.7, 0.95, 5).round(2),
                'Context Precision': np.random.uniform(0.7, 0.95, 5).round(2),
                'Faithfulness': np.random.uniform(0.7, 0.95, 5).round(2)
            }
            
            df_detail = pd.DataFrame(data)
            st.table(df_detail)