from datetime import date, datetime, timedelta
from collections import OrderedDict

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func, extract

from extensions import db
from models import Santri, Kunjungan, Obat, STATUS_KUNJUNGAN
from routes.auth import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    today = date.today()

    total_santri = Santri.query.count()
    total_kunjungan = Kunjungan.query.count()
    total_kunjungan_bulan_ini = Kunjungan.query.filter(
        extract("month", Kunjungan.tanggal) == today.month,
        extract("year", Kunjungan.tanggal) == today.year,
    ).count()
    obat_menipis = Obat.query.filter(Obat.stok <= Obat.stok_minimum).count()

    # Grafik 1: 5 keluhan terbanyak (dari data riil di database)
    keluhan_terbanyak = (
        db.session.query(Kunjungan.keluhan, func.count(Kunjungan.id).label("jumlah"))
        .group_by(Kunjungan.keluhan)
        .order_by(func.count(Kunjungan.id).desc())
        .limit(5)
        .all()
    )
    chart_keluhan_labels = [k[0] for k in keluhan_terbanyak]
    chart_keluhan_data = [k[1] for k in keluhan_terbanyak]

    # Grafik 2: tren kunjungan 6 bulan terakhir (dari data riil di database)
    bulan_labels = []
    bulan_data = []
    for i in range(5, -1, -1):
        bulan_ref = today.replace(day=1) - timedelta(days=1)
        # hitung mundur bulan dengan aman
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        jumlah = Kunjungan.query.filter(
            extract("month", Kunjungan.tanggal) == month,
            extract("year", Kunjungan.tanggal) == year,
        ).count()
        bulan_labels.append(f"{month:02d}/{year}")
        bulan_data.append(jumlah)

    obat_stok_rendah = Obat.query.filter(Obat.stok <= Obat.stok_minimum).order_by(Obat.stok).all()
    kunjungan_terbaru = Kunjungan.query.order_by(Kunjungan.tanggal.desc(), Kunjungan.id.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_santri=total_santri,
        total_kunjungan=total_kunjungan,
        total_kunjungan_bulan_ini=total_kunjungan_bulan_ini,
        obat_menipis=obat_menipis,
        chart_keluhan_labels=chart_keluhan_labels,
        chart_keluhan_data=chart_keluhan_data,
        chart_bulan_labels=bulan_labels,
        chart_bulan_data=bulan_data,
        obat_stok_rendah=obat_stok_rendah,
        kunjungan_terbaru=kunjungan_terbaru,
    )


# ---------------------------------------------------------------------------
# CRUD SANTRI
# ---------------------------------------------------------------------------
@admin_bp.route("/santri")
@login_required
def santri_list():
    q = request.args.get("q", "").strip()
    query = Santri.query
    if q:
        query = query.filter(Santri.nama.ilike(f"%{q}%") | Santri.nis.ilike(f"%{q}%"))
    data_santri = query.order_by(Santri.nama).all()
    return render_template("admin/santri_list.html", data_santri=data_santri, q=q)


@admin_bp.route("/santri/tambah", methods=["GET", "POST"])
@login_required
def santri_tambah():
    if request.method == "POST":
        nis = request.form.get("nis", "").strip()
        nama = request.form.get("nama", "").strip()
        jenis_kelamin = request.form.get("jenis_kelamin", "")
        asrama = request.form.get("asrama", "").strip()
        tanggal_lahir = request.form.get("tanggal_lahir", "")
        kontak_wali = request.form.get("kontak_wali", "").strip()

        errors = []
        if not nis:
            errors.append("NIS wajib diisi.")
        elif Santri.query.filter_by(nis=nis).first():
            errors.append(f"NIS '{nis}' sudah terdaftar, gunakan NIS lain.")
        if not nama:
            errors.append("Nama santri wajib diisi.")
        if jenis_kelamin not in ("L", "P"):
            errors.append("Jenis kelamin wajib dipilih.")
        if not asrama:
            errors.append("Asrama wajib diisi.")

        tgl_lahir_obj = None
        if tanggal_lahir:
            try:
                tgl_lahir_obj = datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Format tanggal lahir tidak valid.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/santri_form.html", mode="tambah", santri=request.form)

        santri = Santri(
            nis=nis,
            nama=nama,
            jenis_kelamin=jenis_kelamin,
            asrama=asrama,
            tanggal_lahir=tgl_lahir_obj,
            kontak_wali=kontak_wali or None,
        )
        db.session.add(santri)
        db.session.commit()
        flash(f"Data santri '{nama}' berhasil ditambahkan.", "success")
        return redirect(url_for("admin.santri_list"))

    return render_template("admin/santri_form.html", mode="tambah", santri=None)


@admin_bp.route("/santri/<int:santri_id>/ubah", methods=["GET", "POST"])
@login_required
def santri_ubah(santri_id):
    santri = Santri.query.get_or_404(santri_id)

    if request.method == "POST":
        nis = request.form.get("nis", "").strip()
        nama = request.form.get("nama", "").strip()
        jenis_kelamin = request.form.get("jenis_kelamin", "")
        asrama = request.form.get("asrama", "").strip()
        tanggal_lahir = request.form.get("tanggal_lahir", "")
        kontak_wali = request.form.get("kontak_wali", "").strip()

        errors = []
        if not nis:
            errors.append("NIS wajib diisi.")
        elif Santri.query.filter(Santri.nis == nis, Santri.id != santri_id).first():
            errors.append(f"NIS '{nis}' sudah digunakan santri lain.")
        if not nama:
            errors.append("Nama santri wajib diisi.")
        if jenis_kelamin not in ("L", "P"):
            errors.append("Jenis kelamin wajib dipilih.")
        if not asrama:
            errors.append("Asrama wajib diisi.")

        tgl_lahir_obj = santri.tanggal_lahir
        if tanggal_lahir:
            try:
                tgl_lahir_obj = datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Format tanggal lahir tidak valid.")

        if errors:
            for e in errors:
                flash(e, "danger")
            form_data = {
                "nis": nis, "nama": nama, "jenis_kelamin": jenis_kelamin,
                "asrama": asrama, "tanggal_lahir": tanggal_lahir, "kontak_wali": kontak_wali,
            }
            return render_template("admin/santri_form.html", mode="ubah", santri=form_data, santri_id=santri_id)

        santri.nis = nis
        santri.nama = nama
        santri.jenis_kelamin = jenis_kelamin
        santri.asrama = asrama
        santri.tanggal_lahir = tgl_lahir_obj
        santri.kontak_wali = kontak_wali or None
        db.session.commit()
        flash(f"Data santri '{nama}' berhasil diperbarui.", "success")
        return redirect(url_for("admin.santri_list"))

    return render_template("admin/santri_form.html", mode="ubah", santri=santri, santri_id=santri_id)


@admin_bp.route("/santri/<int:santri_id>/hapus", methods=["POST"])
@login_required
def santri_hapus(santri_id):
    santri = Santri.query.get_or_404(santri_id)
    nama = santri.nama
    db.session.delete(santri)
    db.session.commit()
    flash(f"Data santri '{nama}' beserta riwayat kunjungannya berhasil dihapus.", "success")
    return redirect(url_for("admin.santri_list"))


# ---------------------------------------------------------------------------
# CRUD OBAT
# ---------------------------------------------------------------------------
@admin_bp.route("/obat")
@login_required
def obat_list():
    data_obat = Obat.query.order_by(Obat.nama_obat).all()
    return render_template("admin/obat_list.html", data_obat=data_obat)


@admin_bp.route("/obat/tambah", methods=["GET", "POST"])
@login_required
def obat_tambah():
    if request.method == "POST":
        nama_obat = request.form.get("nama_obat", "").strip()
        satuan = request.form.get("satuan", "").strip()
        stok = request.form.get("stok", "").strip()
        stok_minimum = request.form.get("stok_minimum", "").strip()
        keterangan = request.form.get("keterangan", "").strip()

        errors = []
        if not nama_obat:
            errors.append("Nama obat wajib diisi.")
        if not satuan:
            errors.append("Satuan obat wajib diisi.")
        if not stok.isdigit():
            errors.append("Stok wajib diisi dengan angka.")
        if stok_minimum and not stok_minimum.isdigit():
            errors.append("Stok minimum wajib berupa angka.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/obat_form.html", mode="tambah", obat=request.form)

        obat = Obat(
            nama_obat=nama_obat,
            satuan=satuan,
            stok=int(stok),
            stok_minimum=int(stok_minimum) if stok_minimum else 10,
            keterangan=keterangan or None,
        )
        db.session.add(obat)
        db.session.commit()
        flash(f"Obat '{nama_obat}' berhasil ditambahkan.", "success")
        return redirect(url_for("admin.obat_list"))

    return render_template("admin/obat_form.html", mode="tambah", obat=None)


@admin_bp.route("/obat/<int:obat_id>/ubah", methods=["GET", "POST"])
@login_required
def obat_ubah(obat_id):
    obat = Obat.query.get_or_404(obat_id)

    if request.method == "POST":
        nama_obat = request.form.get("nama_obat", "").strip()
        satuan = request.form.get("satuan", "").strip()
        stok = request.form.get("stok", "").strip()
        stok_minimum = request.form.get("stok_minimum", "").strip()
        keterangan = request.form.get("keterangan", "").strip()

        errors = []
        if not nama_obat:
            errors.append("Nama obat wajib diisi.")
        if not satuan:
            errors.append("Satuan obat wajib diisi.")
        if not stok.isdigit():
            errors.append("Stok wajib diisi dengan angka.")
        if stok_minimum and not stok_minimum.isdigit():
            errors.append("Stok minimum wajib berupa angka.")

        if errors:
            for e in errors:
                flash(e, "danger")
            form_data = {
                "nama_obat": nama_obat, "satuan": satuan, "stok": stok,
                "stok_minimum": stok_minimum, "keterangan": keterangan,
            }
            return render_template("admin/obat_form.html", mode="ubah", obat=form_data, obat_id=obat_id)

        obat.nama_obat = nama_obat
        obat.satuan = satuan
        obat.stok = int(stok)
        obat.stok_minimum = int(stok_minimum) if stok_minimum else 10
        obat.keterangan = keterangan or None
        db.session.commit()
        flash(f"Data obat '{nama_obat}' berhasil diperbarui.", "success")
        return redirect(url_for("admin.obat_list"))

    return render_template("admin/obat_form.html", mode="ubah", obat=obat, obat_id=obat_id)


@admin_bp.route("/obat/<int:obat_id>/hapus", methods=["POST"])
@login_required
def obat_hapus(obat_id):
    obat = Obat.query.get_or_404(obat_id)
    nama = obat.nama_obat
    db.session.delete(obat)
    db.session.commit()
    flash(f"Data obat '{nama}' berhasil dihapus.", "success")
    return redirect(url_for("admin.obat_list"))


# ---------------------------------------------------------------------------
# CRUD KUNJUNGAN (relasi ke Santri & Obat)
# ---------------------------------------------------------------------------
@admin_bp.route("/kunjungan")
@login_required
def kunjungan_list():
    data_kunjungan = Kunjungan.query.order_by(Kunjungan.tanggal.desc(), Kunjungan.id.desc()).all()
    return render_template("admin/kunjungan_list.html", data_kunjungan=data_kunjungan)


@admin_bp.route("/kunjungan/tambah", methods=["GET", "POST"])
@login_required
def kunjungan_tambah():
    daftar_santri = Santri.query.order_by(Santri.nama).all()
    daftar_obat = Obat.query.order_by(Obat.nama_obat).all()

    if request.method == "POST":
        santri_id = request.form.get("santri_id", "")
        tanggal = request.form.get("tanggal", "")
        keluhan = request.form.get("keluhan", "").strip()
        diagnosa = request.form.get("diagnosa", "").strip()
        tindakan = request.form.get("tindakan", "").strip()
        petugas = request.form.get("petugas", "").strip()
        status = request.form.get("status", "")
        obat_id = request.form.get("obat_id", "")
        jumlah_obat = request.form.get("jumlah_obat", "").strip()

        errors = []
        if not santri_id or not Santri.query.get(santri_id):
            errors.append("Santri wajib dipilih.")
        if not keluhan:
            errors.append("Keluhan wajib diisi.")
        if not petugas:
            errors.append("Nama petugas pemeriksa wajib diisi.")
        if status not in STATUS_KUNJUNGAN:
            errors.append("Status kunjungan wajib dipilih.")

        tanggal_obj = date.today()
        if tanggal:
            try:
                tanggal_obj = datetime.strptime(tanggal, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Format tanggal tidak valid.")
        else:
            errors.append("Tanggal kunjungan wajib diisi.")

        obat_obj = None
        jumlah_obat_val = None
        if obat_id:
            obat_obj = Obat.query.get(obat_id)
            if not obat_obj:
                errors.append("Obat yang dipilih tidak ditemukan.")
            elif not jumlah_obat.isdigit() or int(jumlah_obat) < 1:
                errors.append("Jumlah obat wajib diisi dengan angka lebih dari 0.")
            elif int(jumlah_obat) > obat_obj.stok:
                errors.append(f"Stok obat '{obat_obj.nama_obat}' tidak mencukupi (sisa stok: {obat_obj.stok}).")
            else:
                jumlah_obat_val = int(jumlah_obat)

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "admin/kunjungan_form.html", mode="tambah", kunjungan=request.form,
                daftar_santri=daftar_santri, daftar_obat=daftar_obat, status_list=STATUS_KUNJUNGAN,
            )

        kunjungan = Kunjungan(
            santri_id=int(santri_id),
            tanggal=tanggal_obj,
            keluhan=keluhan,
            diagnosa=diagnosa or None,
            tindakan=tindakan or None,
            petugas=petugas,
            status=status,
            obat_id=obat_obj.id if obat_obj else None,
            jumlah_obat=jumlah_obat_val,
        )
        db.session.add(kunjungan)

        if obat_obj and jumlah_obat_val:
            obat_obj.stok -= jumlah_obat_val

        db.session.commit()
        flash("Data kunjungan pemeriksaan berhasil disimpan.", "success")
        return redirect(url_for("admin.kunjungan_list"))

    return render_template(
        "admin/kunjungan_form.html", mode="tambah", kunjungan=None,
        daftar_santri=daftar_santri, daftar_obat=daftar_obat, status_list=STATUS_KUNJUNGAN,
    )


@admin_bp.route("/kunjungan/<int:kunjungan_id>/ubah", methods=["GET", "POST"])
@login_required
def kunjungan_ubah(kunjungan_id):
    kunjungan = Kunjungan.query.get_or_404(kunjungan_id)
    daftar_santri = Santri.query.order_by(Santri.nama).all()
    daftar_obat = Obat.query.order_by(Obat.nama_obat).all()

    if request.method == "POST":
        santri_id = request.form.get("santri_id", "")
        tanggal = request.form.get("tanggal", "")
        keluhan = request.form.get("keluhan", "").strip()
        diagnosa = request.form.get("diagnosa", "").strip()
        tindakan = request.form.get("tindakan", "").strip()
        petugas = request.form.get("petugas", "").strip()
        status = request.form.get("status", "")

        errors = []
        if not santri_id or not Santri.query.get(santri_id):
            errors.append("Santri wajib dipilih.")
        if not keluhan:
            errors.append("Keluhan wajib diisi.")
        if not petugas:
            errors.append("Nama petugas pemeriksa wajib diisi.")
        if status not in STATUS_KUNJUNGAN:
            errors.append("Status kunjungan wajib dipilih.")

        tanggal_obj = kunjungan.tanggal
        if tanggal:
            try:
                tanggal_obj = datetime.strptime(tanggal, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Format tanggal tidak valid.")
        else:
            errors.append("Tanggal kunjungan wajib diisi.")

        if errors:
            for e in errors:
                flash(e, "danger")
            form_data = {
                "santri_id": santri_id, "tanggal": tanggal, "keluhan": keluhan,
                "diagnosa": diagnosa, "tindakan": tindakan, "petugas": petugas, "status": status,
            }
            return render_template(
                "admin/kunjungan_form.html", mode="ubah", kunjungan=form_data, kunjungan_id=kunjungan_id,
                daftar_santri=daftar_santri, daftar_obat=daftar_obat, status_list=STATUS_KUNJUNGAN,
            )

        kunjungan.santri_id = int(santri_id)
        kunjungan.tanggal = tanggal_obj
        kunjungan.keluhan = keluhan
        kunjungan.diagnosa = diagnosa or None
        kunjungan.tindakan = tindakan or None
        kunjungan.petugas = petugas
        kunjungan.status = status
        db.session.commit()
        flash("Data kunjungan berhasil diperbarui.", "success")
        return redirect(url_for("admin.kunjungan_list"))

    return render_template(
        "admin/kunjungan_form.html", mode="ubah", kunjungan=kunjungan, kunjungan_id=kunjungan_id,
        daftar_santri=daftar_santri, daftar_obat=daftar_obat, status_list=STATUS_KUNJUNGAN,
    )


@admin_bp.route("/kunjungan/<int:kunjungan_id>/hapus", methods=["POST"])
@login_required
def kunjungan_hapus(kunjungan_id):
    kunjungan = Kunjungan.query.get_or_404(kunjungan_id)
    db.session.delete(kunjungan)
    db.session.commit()
    flash("Data kunjungan berhasil dihapus.", "success")
    return redirect(url_for("admin.kunjungan_list"))
