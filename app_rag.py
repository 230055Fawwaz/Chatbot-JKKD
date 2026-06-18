# ==========================================
# Nama File: app_rag.py
# Deskripsi: RAG
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   18-06-2026
# Catatan:
#   - Integrasi fungsi pencarian dengan model AI
# ==========================================

import sqlite3
import struct
import requests
import sqlite_vec

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_EMBEDDING = "nomic-embed-text"
MODEL_LLM = "qwen2.5:1.5b" # Sesuaikan dengan nama model Qwen Anda di Ollama

def get_embedding(teks):
    payload = {"model": MODEL_EMBEDDING, "prompt": teks}
    try:
        return requests.post(OLLAMA_EMBED_URL, json=payload).json().get("embedding")
    except: return None

def cari_konteks(pertanyaan, jumlah_hasil=3):
    query_vector = get_embedding(pertanyaan)
    if not query_vector: return ""
    
    conn = sqlite3.connect("kuliah_rag.db")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    cursor = conn.cursor()
    
    query_blob = struct.pack(f"{len(query_vector)}f", *query_vector)
    cursor.execute("""
        SELECT d.konten_teks FROM vektor_chunks v
        JOIN dokumen_chunks d ON v.chunk_id = d.id
        WHERE v.embedding MATCH ? AND k = ?
        ORDER BY v.distance ASC;
    """, (query_blob, jumlah_hasil))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Satukan potongan-potongan teks menjadi satu string besar
    konteks_utuh = "\n\n".join([row[0] for row in rows])
    return konteks_utuh

def tanya_chatbot(pertanyaan):
    # 1. Ambil potongan materi kuliah yang relevan
    konteks = cari_konteks(pertanyaan)
    
    # 2. Susun prompt untuk Qwen agar merangkum potongan teks tersebut
    prompt_sistem = (
        "Anda adalah asisten dosen yang pintar. Jawablah pertanyaan mahasiswa "
        "HANYA berdasarkan konteks materi kuliah yang diberikan di bawah ini. "
        "Jika jawabannya tidak ada di dalam konteks, katakan bahwa materi tersebut "
        "tidak ditemukan di dokumen kuliah."
    )
    
    prompt_user = f"Konteks Materi Kuliah:\n{konteks}\n\nPertanyaan: {pertanyaan}\nJawaban:"
    
    # 3. Kirim ke Qwen via Ollama
    payload = {
        "model": MODEL_LLM,
        "messages": [
            {"role": "system", "content": prompt_sistem},
            {"role": "user", "content": prompt_user}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_CHAT_URL, json=payload)
        return response.json()['message']['content']
    except Exception as e:
        return f"Gagal terhubung ke Qwen: {e}"

if __name__ == "__main__":
    print(f"🤖 Chatbot RAG ({MODEL_LLM}) Siap Diuji.")
    while True:
        tanya = input("\nMahasiswa: ")
        if tanya.lower() == 'exit': break
        
        print("Bot sedang membaca materi kuliah dan merangkum jawaban...")
        jawaban = tanya_chatbot(tanya)
        print(f"\nBot: {jawaban}")