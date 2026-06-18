# ==========================================
# Nama File: ingestion.py
# Deskripsi: Pembaca materi kuliah
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   18-06-2026
# Catatan:
#   - Membaca teks dari file .pdf dan .md
#   - Memotong teks dengan Fixed-Size Chunking dengan Overlap
#   - Menampilkan hasilnya di terminal/command prompt
#   - Jalankan command: "ollama pull nomic-embed-text" di terminal
#   - Pastikan Ollama menyala
# ==========================================

import os
from pypdf import PdfReader
import sqlite3
import requests
import sqlite_vec

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

# Konfigurasi Ollama
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_EMBEDDING = "nomic-embed-text" # Atau model embedding lain yang Anda unduh di Ollama

def get_embedding(teks):
    """Mengambil vektor embedding dari Ollama lokal."""
    payload = {
        "model": MODEL_EMBEDDING,
        "prompt": teks
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response_data = response.json()
        return response_data.get("embedding")
    except Exception as e:
        print(f"Gagal mengambil embedding dari Ollama: {e}")
        return None

def proses_dan_simpan_dokumen():
    folder_target = "data_kuliah"
    
    # Koneksi ke Database
    conn = sqlite3.connect("kuliah_rag.db")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    cursor = conn.cursor()
    
    # Ambil semua file di folder data_kuliah
    files = os.listdir(folder_target)
    if not files:
        print("⚠️ Folder 'data_kuliah' kosong. Masukkan file PDF atau .md dulu!")
        return

    print(f"Mengonversi model embedding menggunakan: {MODEL_EMBEDDING}")
    
    for file_name in files:
        path_lengkap = os.path.join(folder_target, file_name)
        ext = os.path.splitext(file_name)[1].lower()
        
        teks_dokumen = ""
        if ext == ".pdf":
            print(f"📄 Membaca PDF: {file_name}...")
            teks_dokumen = baca_pdf(path_lengkap)
        elif ext == ".md":
            print(f"📝 Membaca Markdown: {file_name}...")
            teks_dokumen = baca_markdown(path_lengkap)
        else:
            continue # Abaikan file dengan format lain
            
        if not teks_dokumen.strip():
            print(f"⚠️ File {file_name} tidak menghasilkan teks.")
            continue
            
        # Potong teks menjadi chunks
        chunks = potong_teks(teks_dokumen, ukuran_chunk=600, overlap=100)
        print(f"✂️ Berhasil memotong menjadi {len(chunks)} bagian.")
        
        for idx, chunk in enumerate(chunks):
            # 1. Simpan teks asli ke tabel standar
            cursor.execute(
                "INSERT INTO dokumen_chunks (nama_file, tipe_file, konten_teks) VALUES (?, ?, ?)",
                (file_name, ext, chunk)
            )
            # Ambil ID baris yang baru saja dimasukkan
            last_id = cursor.lastrowid
            
            # 2. Dapatkan Vektor dari Ollama
            vector = get_embedding(chunk)
            
            if vector:
                # sqlite-vec menerima data vektor dalam bentuk binary (BLOB) f32
                # Kita gunakan serialize_float_vector bawaan sqlite_vec jika ada, 
                # atau serialize manual menggunakan json/struct. Paling aman untuk sqlite-vec lewat python adalah melempar bertipe bytes atau json array tergantung setup.
                # Namun untuk sqlite-vec resmi, kita bisa gunakan json_array atau cast jika didukung, atau serialize menggunakan struct.
                # Agar vanilla dan aman tanpa library ekstra, kita convert array float ke byte string (BLOB)
                import struct
                vector_blob = struct.pack(f"{len(vector)}f", *vector)
                
                # 3. Simpan ke tabel virtual vektor
                cursor.execute(
                    "INSERT INTO vektor_chunks (chunk_id, embedding) VALUES (?, ?)",
                    (last_id, vector_blob)
                )
                print(f"  -> Chunk {idx+1}/{len(chunks)} berhasil di-embed & disimpan.", end="\r")
        print(f"\n✅ Selesai memproses {file_name}\n")
        
    conn.commit()
    conn.close()
    print("🎉 Semua dokumen kuliah berhasil dimasukkan ke Database Vektor lokal!")

if __name__ == "__main__":
    # Sebelum menjalankan, pastikan Anda sudah melakukan `ollama pull nomic-embed-text` di terminal Anda
    proses_dan_simpan_dokumen()