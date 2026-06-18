# ==========================================
# Nama File: ingestion.py
# Deskripsi: Pembaca materi kuliah
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   18-06-2026
# Catatan:
#   - Membaca teks dari file .pdf dan .md
#   - Memotong teks dengan Fixed-Size Chunking dengan Overlap
#   - Menampilkan hasilnya di terminal/command prompt
# ==========================================

import os
from pypdf import PdfReader

def baca_pdf(path_file):
    """Membaca seluruh teks dari file PDF halaman demi halaman."""
    teks_total = ""
    try:
        reader = PdfReader(path_file)
        for halaman in reader.pages:
            teks_halaman = halaman.extract_text()
            if teks_halaman:
                teks_total += teks_halaman + "\n"
    except Exception as e:
        print(f"Gagal membaca PDF {path_file}: {e}")
    return teks_total

def baca_markdown(path_file):
    """Membaca teks dari file Markdown."""
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Gagal membaca Markdown {path_file}: {e}")
        return ""

def potong_teks(teks, ukuran_chunk=600, overlap=100):
    """
    Memotong teks panjang menjadi potongan kecil (chunks).
    overlap memastikan tidak ada informasi yang terputus di ujung potongan.
    """
    chunks = []
    start = 0
    while start < len(teks):
        end = start + ukuran_chunk
        chunk = teks[start:end]
        chunks.append(chunk.strip())
        # Geser start maju sebesar (ukuran_chunk - overlap)
        start += (ukuran_chunk - overlap)
    return chunks

# --- AREA UNTUK TEST RUN ---
if __name__ == "__main__":
    # Buat folder tiruan untuk testing jika belum ada
    os.makedirs("data_kuliah", exist_ok=True)
    
    print("📁 Folder 'data_kuliah' siap. Silakan masukkan file PDF/.md kuliah Anda ke sana.")
    print("Mencoba simulasi chunking dengan teks buatan...")
    
    teks_contoh = "Materi Kuliah Pemrograman Web. Bab 1: Pengenalan HTML. HTML adalah bahasa standar untuk membuat halaman web. Bab 2: CSS untuk Desain. CSS digunakan untuk mengatur gaya dan tata letak halaman web agar terlihat menarik."
    
    hasil_potongan = potong_teks(teks_contoh, ukuran_chunk=100, overlap=20)
    
    for i, chunk in enumerate(hasil_potongan):
        print(f"\n[Chunk {i+1}]: {chunk}")