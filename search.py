# ==========================================
# Nama File: search.py
# Deskripsi: Penerima percakapn user
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   18-06-2026
# Catatan:
#   - Menerima pertanyaan user (menerima prompt)
#   - Mengubah pertanyaan (prompt) menjadi vektor
#   - Mencari potongan teks materi kuliah yang sesuai
# ==========================================

import sqlite3
import struct
import requests
import sqlite_vec

# Konfigurasi yang sama dengan ingestion
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_EMBEDDING = "nomic-embed-text"

def get_embedding(teks):
    """Mengubah pertanyaan user menjadi vektor."""
    payload = {"model": MODEL_EMBEDDING, "prompt": teks}
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get("embedding")
    except Exception as e:
        print(f"Gagal mengambil embedding: {e}")
        return None

def cari_materi_kuliah(pertanyaan, jumlah_hasil=3):
    """Mencari potongan teks kuliah yang paling relevan dengan pertanyaan."""
    query_vector = get_embedding(pertanyaan)
    if not query_vector:
        return []

    # Koneksi ke database
    conn = sqlite3.connect("kuliah_rag.db")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    cursor = conn.cursor()

    # Convert query_vector ke format binary BLOB f32 agar bisa dibaca sqlite-vec
    query_blob = struct.pack(f"{len(query_vector)}f", *query_vector)

    # PERBAIKAN QUERY: Menggunakan operator MATCH untuk pencarian K-NN standar sqlite-vec
    cursor.execute("""
        SELECT 
            d.nama_file,
            d.konten_teks,
            v.distance
        FROM vektor_chunks v
        JOIN dokumen_chunks d ON v.chunk_id = d.id
        WHERE v.embedding MATCH ? AND k = ?
        ORDER BY v.distance ASC;
    """, (query_blob, jumlah_hasil))

    hasil = cursor.fetchall()
    conn.close()
    return hasil

# --- AREA UNTUK UJI COBA PENCARIAN ---
if __name__ == "__main__":
    print("🔍 Sistem Pencarian Dokumen Kuliah Siap.")
    while True:
        tanya = input("\nTanya materi kuliah (atau ketik 'exit' untuk keluar): ")
        if tanya.lower() == 'exit':
            break
            
        print("Sedang mencari di database...")
        hasil_pencarian = cari_materi_kuliah(tanya)
        
        if not hasil_pencarian:
            print("Tidak ditemukan materi yang cocok.")
            continue
            
        print(f"\n📚 Ditemukan {len(hasil_pencarian)} potongan materi yang relevan:")
        for idx, (file, teks, skor) in enumerate(hasil_pencarian):
            print(f"\n--- [Hasil {idx+1}] dari File: {file} (Jarak Vektor: {skor:.4f}) ---")
            print(teks)