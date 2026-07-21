"""
Script untuk mengisi data awal (seed) ke database.
Jalankan sekali di awal dengan perintah: python seed.py
"""
from datetime import date, timedelta

from app import create_app
from extensions import db
from models import Admin, Santri, Obat, Kunjungan

app = create_app()

with app.app_context():
    db.create_all()

    # 1. Buat akun admin default jika belum ada
    if not Admin.query.filter_by(username="admin").first():
        admin = Admin(username="admin", nama_lengkap="Petugas Pos Kesehatan")
        admin.set_password("admin123")
        db.session.add(admin)
        print("Admin default dibuat -> username: admin | password: admin123")
    else:
        print("Akun admin sudah ada, dilewati.")

    # 2. Contoh data santri
    if Santri.query.count() == 0:
        contoh_santri = [
            Santri(nis="S001", nama="Ahmad Fauzi", jenis_kelamin="L", asrama="Asrama Al-Fatih",
                   tanggal_lahir=date(2009, 3, 12), kontak_wali="081234560001"),
            Santri(nis="S002", nama="Siti Nurhaliza", jenis_kelamin="P", asrama="Asrama Khadijah",
                   tanggal_lahir=date(2010, 7, 25), kontak_wali="081234560002"),
            Santri(nis="S003", nama="Muhammad Rizki", jenis_kelamin="L", asrama="Asrama Al-Fatih",
                   tanggal_lahir=date(2009, 11, 2), kontak_wali="081234560003"),
        ]
        db.session.add_all(contoh_santri)
        print("Contoh data santri ditambahkan.")

    # 3. Contoh data obat
    if Obat.query.count() == 0:
        contoh_obat = [
            Obat(nama_obat="Paracetamol 500mg", satuan="tablet", stok=50, stok_minimum=15,
                 keterangan="Obat penurun demam & pereda nyeri"),
            Obat(nama_obat="Oralit", satuan="sachet", stok=8, stok_minimum=10,
                 keterangan="Untuk penanganan dehidrasi/diare"),
            Obat(nama_obat="Minyak Kayu Putih", satuan="botol", stok=20, stok_minimum=5,
                 keterangan="Untuk masuk angin"),
            Obat(nama_obat="Betadine", satuan="botol", stok=5, stok_minimum=5,
                 keterangan="Antiseptik luka luar"),
        ]
        db.session.add_all(contoh_obat)
        print("Contoh data obat ditambahkan.")

    db.session.commit()

    # 4. Contoh data kunjungan (dibuat setelah santri & obat tersimpan agar id tersedia)
    if Kunjungan.query.count() == 0:
        santri1 = Santri.query.filter_by(nis="S001").first()
        santri2 = Santri.query.filter_by(nis="S002").first()
        santri3 = Santri.query.filter_by(nis="S003").first()
        obat_pct = Obat.query.filter_by(nama_obat="Paracetamol 500mg").first()
        obat_oralit = Obat.query.filter_by(nama_obat="Oralit").first()

        today = date.today()
        contoh_kunjungan = [
            Kunjungan(santri_id=santri1.id, tanggal=today - timedelta(days=2), keluhan="Demam",
                      diagnosa="Demam ringan", tindakan="Diberi obat penurun panas & istirahat",
                      petugas="Petugas Pos Kesehatan", status="Rawat Jalan",
                      obat_id=obat_pct.id if obat_pct else None, jumlah_obat=6),
            Kunjungan(santri_id=santri2.id, tanggal=today - timedelta(days=5), keluhan="Diare",
                      diagnosa="Gangguan pencernaan ringan", tindakan="Diberi oralit, edukasi pola makan",
                      petugas="Petugas Pos Kesehatan", status="Rawat Jalan",
                      obat_id=obat_oralit.id if obat_oralit else None, jumlah_obat=2),
            Kunjungan(santri_id=santri3.id, tanggal=today - timedelta(days=10), keluhan="Demam",
                      diagnosa="Demam disertai batuk", tindakan="Dirujuk untuk pemeriksaan lanjutan",
                      petugas="Petugas Pos Kesehatan", status="Dirujuk ke Puskesmas/RS"),
            Kunjungan(santri_id=santri1.id, tanggal=today - timedelta(days=20), keluhan="Sakit Kepala",
                      diagnosa="Kelelahan", tindakan="Istirahat & diberi obat pereda nyeri",
                      petugas="Petugas Pos Kesehatan", status="Rawat Jalan",
                      obat_id=obat_pct.id if obat_pct else None, jumlah_obat=4),
        ]
        db.session.add_all(contoh_kunjungan)
        print("Contoh data kunjungan ditambahkan.")

    db.session.commit()
    print("\nSeeding selesai. Database siap digunakan.")
