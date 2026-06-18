# ==========================================
# Nama File: init_db.py
# Deskripsi: Inisialisasi Database SQLite
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   18-06-2026
# Catatan:
#   - Membuat file database SQLite
#   - Menyiapkan tabel penampung materi kuliah
#   - Menyiapkan tabel penampung vektor tabel materi kuliah
# ==========================================

import sqlite3
import sqlite_vec

def init_database():
    # 1. Buat atau hubungkan ke file database lokal bernama 'kuliah_rag.db'
    conn = sqlite3.connect("kuliah_rag.db")
    
    # 2. Aktifkan dan muat ekstensi sqlite-vec ke dalam koneksi
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    
    cursor = conn.cursor()
    
    # 3. Buat tabel standar untuk menyimpan teks asli dokumen kuliah
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dokumen_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_file TEXT,
            tipe_file TEXT,
            konten_teks TEXT
        );
    """)
    
    # 4. Buat tabel virtual sqlite-vec untuk menyimpan vektor embedding.
    # Qwen 2.5 atau model embedding lokal umumnya menghasilkan 768 atau 1536 dimensi.
    # Kita gunakan 768 sebagai standar awal (sesuaikan dengan model embedding Ollama Anda nanti).
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vektor_chunks USING vec0(
            chunk_id INTEGER PRIMARY KEY,
            embedding FLOAT[768]
        );
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database 'kuliah_rag.db' dan tabel vektor berhasil dibuat!")

if __name__ == "__main__":
    init_database()
    