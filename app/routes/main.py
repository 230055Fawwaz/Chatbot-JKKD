# ==========================================
# Nama File: main.py
# Deskripsi: Rute halaman web awal
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   20-05-2026
# Catatan:
#   - Rute hanya menampilkan halaman saja beserta data di dalamnya
# ==========================================

from flask import render_template, Blueprint

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@main_bp.route("/chat")
def chat():
    return render_template("chat.html")
