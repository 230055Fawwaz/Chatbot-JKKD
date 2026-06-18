# ==========================================
# Nama File: __init__.py
# Deskripsi: Inisialisasi Flask dan Database SQLite
# Penulis:   Fawwaz Yaqzhan
# Tanggal:   18-06-2026
# Catatan:
#   - Pendaftaran rute blueprint
# ==========================================

from flask import Flask

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# ====================================================
# PROSES REGISTRASI BLUEPRINT BARU DI SINI
# ====================================================
# Jalankan import di paling bawah untuk menghindari circular import

# noqa: E402 # pylint: disable=wrong-import-position
from app.routes.main import main_bp

# Daftarkan ke aplikasi utama Anda
app.register_blueprint(main_bp, url_prefix="/")