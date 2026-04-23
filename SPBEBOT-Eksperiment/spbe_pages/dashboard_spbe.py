import streamlit as st
from statistics import mean

# Struktur aspek dan indikator sesuai gambar
aspek_list = [
    {"name": "Aspek 01 (Kebijakan Internal Tata Kelola SPBE)", "jumlah": 10},
    {"name": "Aspek 02 (Perencanaan Strategis SPBE)", "jumlah": 4},
    {"name": "Aspek 03 (Teknologi Informasi dan Komunikasi)", "jumlah": 4},
    {"name": "Aspek 04 (Penyelenggara SPBE)", "jumlah": 2},
    {"name": "Aspek 05 (Penerapan Manajemen SPBE)", "jumlah": 8},
    {"name": "Aspek 06 (Pelaksanaan Audit TIK)", "jumlah": 3},
    {"name": "Aspek 07 (Layanan Administrasi Pemerintahan Berbasis Elektronik)", "jumlah": 10},
    {"name": "Aspek 08 (Layanan Publik Berbasis Elektronik)", "jumlah": 7},
]

# Buat struktur data indikator per aspek
indikator_values = []
for aspek in aspek_list:
    indikator_values.append([None for _ in range(aspek["jumlah"])])

# Fungsi untuk mengisi nilai indikator dari dictionary
# Contoh: {'Level': 2, 'Indikator': 4, 'Aspek': 8, 'Domain': 2}
def set_indikator_value(aspek_ke, indikator_ke, value):
    # aspek_ke dan indikator_ke mulai dari 1
    indikator_values[aspek_ke-1][indikator_ke-1] = value

# Contoh pengisian dari dictionary
input_dict = {'Level': 2, 'Indikator': 4, 'Aspek': 8, 'Domain': 2}
set_indikator_value(input_dict['Aspek'], input_dict['Indikator'], input_dict['Level'])

def show_dashboard():
    st.markdown('<h1 class="sub-header">Dashboard Indeks SPBE</h1>', unsafe_allow_html=True)
    
    # Total Index Value
    st.markdown('''
        <div style="border: 2px solid #4a4a4a; border-radius: 10px; padding: 10px; margin: 10px 0;">
            <h3 style="text-align: center; margin: 0;">Nilai Indeks Total</h3>
            <h1 style="text-align: center; font-weight: bold; margin: 10px 0;">3.47</h1>
        </div>
    ''', unsafe_allow_html=True)
    
    # Domain Values
    st.markdown('''
        <div style="border: 2px solid #4a4a4a; border-radius: 10px; padding: 20px; margin: 10px 0;">
            <h3 style="text-align: center;">Domain SPBE</h3>
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 1; margin: 0 10px;">
                    <div style="border: 2px solid #4a4a4a; border-radius: 10px; padding: 10px; margin: 10px 0;">
                        <div class="metric-label">Domain 1</div>
                        <div class="metric-value">3.52</div>
                    </div>
                </div>
                <div style="flex: 1; margin: 0 10px;">
                    <div style="border: 2px solid #4a4a4a; border-radius: 10px; padding: 10px; margin: 10px 0;">
                        <div class="metric-label">Domain 2</div>
                        <div class="metric-value">3.65</div>
                    </div>
                </div>
                <div style="flex: 1; margin: 0 10px;">
                    <div style="border: 2px solid #4a4a4a; border-radius: 10px; padding: 10px; margin: 10px 0;">
                        <div class="metric-label">Domain 3</div>
                        <div class="metric-value">3.40</div>
                    </div>
                </div>
                <div style="flex: 1; margin: 0 10px;">
                    <div style="border: 2px solid #4a4a4a; border-radius: 10px; padding: 10px; margin: 10px 0;">
                        <div class="metric-label">Domain 4</div>
                        <div class="metric-value">3.31</div>
                    </div>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center;">Aspek SPBE</h3>', unsafe_allow_html=True)

    for idx, aspek in enumerate(aspek_list):
        values = indikator_values[idx]
        aspek_avg = mean([v for v in values if v is not None]) if any(v is not None for v in values) else '-'
        with st.expander(f"{aspek['name']} - {aspek_avg if aspek_avg == '-' else f'{aspek_avg:.2f}'}"):
            st.markdown('<div style="border: 2px solid #4a4a4a; border-radius: 10px; padding: 10px; margin: 10px 0;">', unsafe_allow_html=True)
            # Header indikator
            header = '<tr>' + ''.join([f'<th style="border: 1px solid #4a4a4a; padding: 8px;">Indikator {i+1}</th>' for i in range(aspek['jumlah'])]) + '</tr>'
            # Nilai indikator
            row = '<tr>' + ''.join([f'<td style="border: 1px solid #4a4a4a; text-align:center;">{v if v is not None else "-"}</td>' for v in values]) + '</tr>'
            st.markdown(f'<table width="100%" style="border-collapse: collapse;">{header}{row}</table>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)