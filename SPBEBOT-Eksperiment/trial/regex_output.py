import re
import ast

def extract_dictionary(text):
    # Pola regex untuk mencari dictionary di antara kurung kurawal
    pattern = r'\{[^}]*\}'
    
    # Cari semua kecocokan pola
    matches = re.findall(pattern, text)
    
    # Jika ada match, ambil yang pertama
    if matches:
        try:
            # Gunakan ast.literal_eval untuk mengonversi string dictionary menjadi dictionary aktual
            dictionary = ast.literal_eval(matches[0])
            return dictionary
        except (SyntaxError, ValueError):
            print("Gagal mengurai dictionary")
            return None
    else:
        print("Tidak ada dictionary yang ditemukan")
        return None

# Contoh penggunaan
text = """
Berdasarkan pedoman pemantauan dan evaluasi SPBE.....dengan diberikannya informasi tahapan dan bukti dukung maka indeks SPBEdiberikan: 

Penilaian = 
{"Level": 2,
"Indikator": 4,
"Aspek": 23,
"Domain": 2,

}alasan penilaian diatas karena.....level.....indikator....aspek....domain...sesuai standard dari pedoman evaluasi SPBE.
"""

# Ekstrak dictionary
result = extract_dictionary(text)

# Tampilkan hasilnya
if result:
    print("Dictionary yang diekstrak:")
    print(result)
    print("\nTipe data:", type(result))