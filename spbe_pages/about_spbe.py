import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import io


# Function to create a placeholder image
def get_placeholder_image(width, height, text="SPBE Image"):
    fig, ax = plt.subplots(figsize=(width/100, height/100))
    ax.set_facecolor('#f0f0f0')
    ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=12)
    ax.axis('off')
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    
    return buf
# Content for Tentang SPBE
def show_about_spbe():
    st.markdown('<h1 class="main-header">Tentang SPBE</h1>', unsafe_allow_html=True)
    
    st.markdown('<p class="paragraph">Sistem Pemerintahan Berbasis Elektronik (SPBE) merupakan penyelenggaraan pemerintahan yang memanfaatkan teknologi informasi dan komunikasi untuk memberikan layanan kepada pengguna SPBE. SPBE diatur melalui Peraturan Presiden Nomor 95 Tahun 2018 tentang Sistem Pemerintahan Berbasis Elektronik.</p>', unsafe_allow_html=True)
    
    # Display SPBE image
    # img_buf = get_placeholder_image(600, 400, "Ilustrasi SPBE")
    st.image("./assets/SPBEimage.jpg", caption="Ilustrasi Sistem Pemerintahan Berbasis Elektronik", use_container_width=True)
    
    st.markdown('<h2 class="sub-header">Tujuan SPBE</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <p class="paragraph">SPBE bertujuan untuk mewujudkan tata kelola pemerintahan yang bersih, efektif, transparan, dan akuntabel serta pelayanan publik yang berkualitas dan terpercaya. Implementasi SPBE diarahkan untuk:</p>
    <ul>
        <li>Meningkatkan efisiensi, efektivitas, transparansi, dan akuntabilitas penyelenggaraan pemerintahan</li>
        <li>Meningkatkan kualitas pelayanan publik</li>
        <li>Mewujudkan tata kelola pemerintahan yang bersih, efektif, dan terpercaya</li>
        <li>Mendukung terwujudnya Indonesia sebagai pusat inovasi digital</li>
    </ul>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">Komponen Utama SPBE</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <p class="paragraph">SPBE terdiri dari beberapa komponen utama, yaitu:</p>
    <ol>
        <li><strong>Tata Kelola SPBE</strong> - Kebijakan, standar, dan prosedur yang diterapkan dalam pemanfaatan TIK untuk pemerintahan</li>
        <li><strong>Manajemen SPBE</strong> - Koordinasi, perencanaan, penganggaran, dan pengukuran kinerja implementasi SPBE</li>
        <li><strong>Layanan SPBE</strong> - Dikelompokkan menjadi layanan administrasi pemerintahan berbasis elektronik dan layanan publik berbasis elektronik</li>
        <li><strong>Infrastruktur SPBE</strong> - Semua perangkat keras, perangkat lunak, dan fasilitas yang menjadi pondasi utama sistem digital pemerintahan</li>
        <li><strong>Aplikasi SPBE</strong> - Sistem-sistem informasi yang digunakan untuk mendukung proses pemerintahan</li>
        <li><strong>Keamanan SPBE</strong> - Penerapan perlindungan terhadap infrastruktur, data, dan aplikasi SPBE</li>
    </ol>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">Evaluasi SPBE</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <p class="paragraph">Evaluasi SPBE dilakukan untuk mengukur kemajuan implementasi SPBE di setiap Instansi Pusat dan Pemerintah Daerah. Evaluasi SPBE dilakukan terhadap:</p>
    <ul>
        <li>Kebijakan internal SPBE</li>
        <li>Tata Kelola SPBE</li>
        <li>Manajemen SPBE</li>
        <li>Layanan SPBE</li>
        <li>Infrastruktur SPBE</li>
        <li>Aplikasi SPBE</li>
        <li>Keamanan SPBE</li>
        <li>Audit TIK</li>
    </ul>
    <p class="paragraph">Hasil evaluasi SPBE digunakan sebagai bahan pertimbangan dalam perencanaan dan pelaksanaan SPBE serta peningkatan kualitas penyelenggaraan pemerintahan dan pelayanan publik.</p>
    """, unsafe_allow_html=True)