import os
import logging
from llama_cloud_services import LlamaParse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize parser
parser = LlamaParse(
    result_type="markdown",
    parse_mode="parse_page_with_agent", 
    preserve_layout_alignment_across_pages=True,
    system_prompt="ini adalah dokumen pedoman Sistem Pemerintahan Berbasis Elektronik (SPBE). Didalamnya ada 4 Domain yang disingkat D (contoh: D1,D2,D3,D4), lalu ada 8 Aspek yang disingkat A (contoh: A2, A5) dan 47 Indikator yang disingkat ID (contoh: ID-3, ID-23). jadi struktur dari SPBE ada 3 unsur tadi domain, aspek, dan indikator, dan penilaian indikator ada kriteria level nya yaitu level 1-5,  dengan level 5 paling tinggi nya.\n\nakan ada perlakuan khusus saat kamu extract table pedoman SPBE ini:\n1. pada table tingkat pertama yaitu penjelasan kuesioner Domain, Aspek, dan Indikator keberapa nya, dari penjelasan, deskripsi indikator, ketentuan penilaian, dan contoh bukti dukung. ini harus dalam 1 tingkatan markdown\n2. pada table tingkat kedua yaitu penjelasan kriteria level dari suatu indikator, kriteria pemenuhan Level, kriteria bukti dukung, tolong bagi seperti itu pada tingkatan table ini",
    language="id",
    adaptive_long_table=True,
    compact_markdown_table=True,
    model="gemini-2.0-flash-001"
)

# Parse PDF and get markdown content
markdown_content = parser.load_data("data/5. Pedoman Menteri PANRB NO 3 Tahun 2024 Pedoman Tata Cara Pemantauan dan Evaluasi SPBE.pdf")

# Save markdown content to file
output_path = "data/output.md"
with open(output_path, "w", encoding="utf-8") as f:
    for doc in markdown_content:
        f.write(doc.text + "\n")

logger.info(f"Markdown content saved to {output_path}")
