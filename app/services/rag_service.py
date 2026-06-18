# ==========================================
# Nama File: rag_service.py
# Deskripsi: Layanan RAG
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   18-06-2026
# Catatan:
#   - Memberikan layanan RAG bagi chatbot AI
# ==========================================

# app/services/rag_service.py
import sqlite3
import struct
import requests
import sqlite_vec
import os

class RAGService:
    def __init__(self):
        self.embed_url = "http://localhost:11434/api/embeddings"
        self.chat_url = "http://localhost:11434/api/chat"
        self.model_embed = "nomic-embed-text"
        self.model_llm = "qwen2.5:1.5b"
        # Arahkan ke file db di root folder proyek
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../kuliah_rag.db'))

    def _get_embedding(self, teks):
        payload = {"model": self.model_embed, "prompt": teks}
        try:
            response = requests.post(self.embed_url, json=payload)
            return response.json().get("embedding")
        except:
            return None

    def _cari_konteks(self, pertanyaan, jumlah_hasil=3):
        query_vector = self._get_embedding(pertanyaan)
        if not query_vector: 
            return ""
        
        conn = sqlite3.connect(self.db_path)
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
        
        return "\n\n".join([row[0] for row in rows])

    def tanya(self, pertanyaan):
        konteks = self._cari_konteks(pertanyaan)
        
        prompt_sistem = (
            "Anda adalah asisten dosen yang pintar. Jawablah pertanyaan mahasiswa "
            "HANYA berdasarkan konteks materi kuliah yang diberikan di bawah ini. "
            "Jika jawabannya tidak ada di dalam konteks, katakan bahwa materi tersebut "
            "tidak ditemukan di dokumen kuliah."
        )
        prompt_user = f"Konteks Materi Kuliah:\n{konteks}\n\nPertanyaan: {pertanyaan}\nJawaban:"
        
        payload = {
            "model": self.model_llm,
            "messages": [
                {"role": "system", "content": prompt_sistem},
                {"role": "user", "content": prompt_user}
            ],
            "stream": False
        }
        
        try:
            response = requests.post(self.chat_url, json=payload)
            return response.json()['message']['content']
        except Exception as e:
            return f"Gagal terhubung ke Qwen lokal: {e}"