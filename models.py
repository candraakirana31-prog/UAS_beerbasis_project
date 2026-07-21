from datetime import datetime, date
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model):
    """Akun petugas / admin Pos Kesehatan Pesantren."""

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Santri(db.Model):
    """Data santri yang terdaftar di Pos Kesehatan Pesantren."""

    __tablename__ = "santri"

    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(30), unique=True, nullable=False)  # Nomor Induk Santri
    nama = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.String(1), nullable=False)  # 'L' atau 'P'
    asrama = db.Column(db.String(50), nullable=False)
    tanggal_lahir = db.Column(db.Date, nullable=True)
    kontak_wali = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    kunjungans = db.relationship(
        "Kunjungan", backref="santri", cascade="all, delete-orphan", lazy=True
    )

    @property
    def umur(self):
        if not self.tanggal_lahir:
            return None
        today = date.today()
        return today.year - self.tanggal_lahir.year - (
            (today.month, today.day) < (self.tanggal_lahir.month, self.tanggal_lahir.day)
        )

    @property
    def total_kunjungan(self):
        return len(self.kunjungans)


class Obat(db.Model):
    """Data stok obat / logistik kesehatan pesantren."""

    __tablename__ = "obat"

    id = db.Column(db.Integer, primary_key=True)
    nama_obat = db.Column(db.String(100), nullable=False)
    satuan = db.Column(db.String(20), nullable=False)  # tablet, botol, strip, dll
    stok = db.Column(db.Integer, nullable=False, default=0)
    stok_minimum = db.Column(db.Integer, nullable=False, default=10)
    keterangan = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    kunjungans = db.relationship("Kunjungan", backref="obat", lazy=True)

    @property
    def stok_menipis(self):
        return self.stok <= self.stok_minimum


STATUS_KUNJUNGAN = ["Rawat Jalan", "Dirujuk ke Puskesmas/RS", "Rawat Inap di Pos Kesehatan"]


class Kunjungan(db.Model):
    """Catatan kunjungan / pemeriksaan kesehatan santri (menghubungkan Santri & Obat)."""

    __tablename__ = "kunjungan"

    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey("santri.id"), nullable=False)
    tanggal = db.Column(db.Date, nullable=False, default=date.today)
    keluhan = db.Column(db.String(150), nullable=False)
    diagnosa = db.Column(db.String(150), nullable=True)
    tindakan = db.Column(db.Text, nullable=True)
    petugas = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default=STATUS_KUNJUNGAN[0])

    obat_id = db.Column(db.Integer, db.ForeignKey("obat.id"), nullable=True)
    jumlah_obat = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
