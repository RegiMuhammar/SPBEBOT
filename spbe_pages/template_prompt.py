import streamlit as st

# Content for Template Prompt
def show_prompt_template():
    st.markdown('<h1 class="main-header">Template Prompt</h1>', unsafe_allow_html=True)
    
    st.markdown('<p class="paragraph">Template prompt adalah kumpulan instruksi terstruktur yang telah dikonfigurasi untuk SPBEBOT. Template-template ini membantu chatbot memberikan jawaban yang lebih relevan dan terstruktur sesuai dengan kebutuhan informasi SPBE.</p>', unsafe_allow_html=True)
    
    templates = [
        {
            "title": "Penjelasan Umum SPBE",
            "prompt": "Berikan penjelasan umum tentang Sistem Pemerintahan Berbasis Elektronik (SPBE), termasuk definisi, tujuan, dan manfaatnya."
        },
        {
            "title": "Komponen SPBE",
            "prompt": "Jelaskan komponen-komponen utama dalam Sistem Pemerintahan Berbasis Elektronik (SPBE) dan bagaimana keterkaitan antar komponen tersebut."
        },
        {
            "title": "Kebijakan SPBE",
            "prompt": "Berikan informasi tentang kebijakan dan regulasi terkait Sistem Pemerintahan Berbasis Elektronik (SPBE), termasuk peraturan perundang-undangan yang mengaturnya."
        },
        {
            "title": "Indikator Penilaian SPBE",
            "prompt": "Jelaskan indikator-indikator yang digunakan dalam penilaian Sistem Pemerintahan Berbasis Elektronik (SPBE) dan bagaimana cara mengukurnya."
        },
        {
            "title": "Implementasi SPBE",
            "prompt": "Berikan panduan langkah-langkah implementasi Sistem Pemerintahan Berbasis Elektronik (SPBE) di instansi pemerintah."
        }
    ]
    
    for i, template in enumerate(templates):
        with st.expander(f"{i+1}. {template['title']}"):
            text_area_key = f"prompt_{i}"
            prompt_text = st.text_area("Edit prompt:", template["prompt"], key=text_area_key, height=100)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Simpan", key=f"save_{i}"):
                    st.success("Template prompt berhasil disimpan!")
            with col2:
                if st.button("Gunakan di Chatbot", key=f"use_{i}"):
                    st.info("Template prompt telah diterapkan di chatbot.")