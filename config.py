import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Ganti SECRET_KEY ini dengan string acak yang aman saat deploy ke production
    SECRET_KEY = os.environ.get("SECRET_KEY", "ganti-dengan-secret-key-yang-aman")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'pos_kesehatan.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Nama pesantren, tampil di halaman publik & judul aplikasi
    NAMA_PESANTREN = os.environ.get("NAMA_PESANTREN", "Pondok Pesantren Al-Hikmah")
