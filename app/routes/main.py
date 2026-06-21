# ==========================================
# Nama File: main.py
# Deskripsi: Rute halaman web awal
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   20-05-2026
# Catatan:
#   - Rute hanya menampilkan halaman saja beserta data di dalamnya
# ==========================================

from flask import Blueprint, render_template, request, jsonify, Response
from app.services.rag_service import RAGService

main_bp = Blueprint("main", __name__)
rag_service = RAGService()


@main_bp.route("/")
@main_bp.route("/")
def index():
    return render_template("chat.html")


@main_bp.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    pesan_user = data.get("message", "")

    if not pesan_user.strip():
        return jsonify({"status": "error", "reply": "Pesan tidak boleh kosong."}), 400

    # Mengembalikan Response berupa stream langsung dari generator RAG
    return Response(rag_service.tanya(pesan_user), mimetype="text/event-stream")
