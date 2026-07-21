<<<<<<< HEAD
body {
    background-color: #f4f7f6;
}

.card {
    border-radius: 0.9rem;
}

.navbar-brand {
    letter-spacing: 0.3px;
}

footer {
    border-top: 1px solid #e0e0e0;
}
=======
# Sistem Informasi Pos Kesehatan Pesantren

Aplikasi web sederhana berbasis **Python Flask** untuk membantu Pos Kesehatan Pesantren
mencatat data santri, kunjungan/pemeriksaan kesehatan, dan stok obat, lengkap dengan
Dashboard Admin berisi statistik dan grafik.

Project ini dibuat untuk memenuhi Tugas UAS Berbasis Project mata kuliah Pengantar Pemrograman.

## Fitur Utama

- **Halaman publik**: profil singkat pos kesehatan, layanan, dan jam operasional.
- **Autentikasi Admin**: login berbasis session, halaman dashboard/admin tidak bisa
  diakses tanpa login.
- **CRUD Data Santri**: tambah, lihat, ubah, hapus data santri (NIS, nama, jenis kelamin,
  asrama, tanggal lahir, kontak wali).
- **CRUD Data Obat**: kelola stok obat, termasuk stok minimum untuk deteksi stok menipis.
- **CRUD Data Kunjungan**: catat pemeriksaan kesehatan santri (keluhan, diagnosa, tindakan,
  status, obat yang diberikan) — entitas ini berelasi langsung dengan Santri dan Obat
  (stok obat otomatis berkurang saat obat diberikan pada kunjungan).
- **Dashboard Admin**: total santri, total kunjungan, kunjungan bulan berjalan, jumlah obat
  stok menipis, grafik tren kunjungan 6 bulan terakhir, dan grafik 5 keluhan terbanyak
  (semua dihitung langsung dari data di database, bukan data statis).
- **Validasi input** di sisi client (atribut HTML `required`, `type`) dan sisi server
  (pengecekan Python di setiap route sebelum data disimpan).
- **Flash message** untuk setiap aksi (berhasil/gagal).

## Teknologi

- Python 3 + Flask
- Flask-SQLAlchemy (ORM) + SQLite
- Bootstrap 5 & Bootstrap Icons (CDN)
- Chart.js (CDN) untuk grafik dashboard

## Struktur Proyek

```
pos_kesehatan_pesantren/
├── app.py                 # Entry point aplikasi (app factory)
├── config.py               # Konfigurasi aplikasi
├── extensions.py            # Inisialisasi SQLAlchemy
├── models.py                 # Model: Admin, Santri, Obat, Kunjungan
├── seed.py                    # Script pengisian data awal (admin default + contoh data)
├── requirements.txt
├── routes/
│   ├── auth.py             # Login/logout admin + decorator login_required
│   ├── admin.py             # Dashboard + CRUD Santri, Obat, Kunjungan
│   └── public.py            # Halaman publik
├── templates/
│   ├── base.html
│   ├── partials/navbar.html
│   ├── public/index.html
│   ├── auth/login.html
│   └── admin/               # dashboard, santri_*, obat_*, kunjungan_*
└── static/
    ├── css/style.css
    └── js/main.js
```

## Cara Instalasi & Menjalankan Aplikasi (Lokal)

1. **Clone / salin project ini**, lalu masuk ke folder project:
   ```bash
   cd pos_kesehatan_pesantren
   ```

2. **Buat virtual environment** (opsional tapi disarankan):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   ```

3. **Install dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Isi data awal** (membuat akun admin default & contoh data santri/obat/kunjungan):
   ```bash
   python seed.py
   ```
   Akun admin default yang dibuat:
   - **Username:** `admin`
   - **Password:** `admin123`

   > Ganti password ini setelah login pertama kali (fitur ganti password dapat
   > dikembangkan lebih lanjut sebagai saran pengembangan pada laporan).

5. **Jalankan aplikasi**:
   ```bash
   python app.py
   ```
   Aplikasi akan berjalan di `http://127.0.0.1:5000`.

6. **Akses halaman**:
   - Halaman publik: `http://127.0.0.1:5000/`
   - Login admin: `http://127.0.0.1:5000/login`
   - Dashboard admin: `http://127.0.0.1:5000/admin/dashboard` (setelah login)

## Catatan Deployment ke Domain `.my.id`

Untuk keperluan pengumpulan tugas (aplikasi wajib di-hosting dengan domain `.my.id`):

1. Gunakan layanan hosting/VPS yang mendukung Python (mis. PythonAnywhere, Railway, VPS
   dengan Nginx + Gunicorn, dsb).
2. Jalankan aplikasi menggunakan **gunicorn** (sudah termasuk di `requirements.txt`), contoh:
   ```bash
   gunicorn -w 2 -b 0.0.0.0:8000 app:app
   ```
3. Arahkan domain `.my.id` yang sudah didaftarkan ke server/hosting tersebut, lalu
   pastikan aplikasi dapat diakses secara publik selama masa penilaian.
4. Ubah `SECRET_KEY` di `config.py` (atau melalui environment variable) menjadi string
   acak yang aman sebelum digunakan secara publik, dan jangan gunakan `debug=True` pada
   mode production.

## Akun Demo

| Username | Password  |
|----------|-----------|
| admin    | admin123  |

## Pengembangan Lanjutan (Saran)

- Fitur ganti password & manajemen multi-admin (role petugas berbeda-beda).
- Notifikasi otomatis (email/WhatsApp) saat stok obat menipis.
- Ekspor laporan kunjungan & stok obat ke PDF/Excel.
- Riwayat kesehatan santri per individu ditampilkan dalam bentuk grafik.
>>>>>>> 2275be02df0d491abb263f9e6dec22816bdda1af
