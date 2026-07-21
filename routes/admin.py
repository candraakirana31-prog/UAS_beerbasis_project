from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func, extract

from extensions import db
from models import Santri, Kunjungan, Obat, STATUS_KUNJUNGAN
from routes.auth import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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
	keluhan_terbanyak = (
		db.session.query(Kunjungan.keluhan, func.count(Kunjungan.id).label("jumlah"))
		.group_by(Kunjungan.keluhan)
		.order_by(func.count(Kunjungan.id).desc())
		.limit(5)
		.all()
	)
	chart_keluhan_labels = [k[0] for k in keluhan_terbanyak]
	chart_keluhan_data = [k[1] for k in keluhan_terbanyak]
	bulan_labels = []
	bulan_data = []
	for i in range(5, -1, -1):
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
		"admin/dashboard.html", total_santri=total_santri, total_kunjungan=total_kunjungan,
		total_kunjungan_bulan_ini=total_kunjungan_bulan_ini, obat_menipis=obat_menipis,
		chart_keluhan_labels=chart_keluhan_labels, chart_keluhan_data=chart_keluhan_data,
		chart_bulan_labels=bulan_labels, chart_bulan_data=bulan_data,
		obat_stok_rendah=obat_stok_rendah, kunjungan_terbaru=kunjungan_terbaru,
	)


@admin_bp.route("/santri")
@login_required
def santri_list():
	q = request.args.get("q", "").strip()
	query = Santri.query
	if q:
		query = query.filter(Santri.nama.ilike(f"%{q}%") | Santri.nis.ilike(f"%{q}%"))
	return render_template("admin/santri_list.html", data_santri=query.order_by(Santri.nama).all(), q=q)


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
			for error in errors:
				flash(error, "danger")
			return render_template("admin/santri_form.html", mode="tambah", santri=request.form)
		db.session.add(Santri(nis=nis, nama=nama, jenis_kelamin=jenis_kelamin, asrama=asrama,
							  tanggal_lahir=tgl_lahir_obj, kontak_wali=kontak_wali or None))
		db.session.commit()
		flash(f"Data santri '{nama}' berhasil ditambahkan.", "success")
		return redirect(url_for("admin.santri_list"))
	return render_template("admin/santri_form.html", mode="tambah", santri=None)


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
			for error in errors:
				flash(error, "danger")
			return render_template("admin/obat_form.html", mode="tambah", obat=request.form)
		db.session.add(Obat(nama_obat=nama_obat, satuan=satuan, stok=int(stok),
							stok_minimum=int(stok_minimum) if stok_minimum else 10,
							keterangan=keterangan or None))
		db.session.commit()
		flash(f"Obat '{nama_obat}' berhasil ditambahkan.", "success")
		return redirect(url_for("admin.obat_list"))
	return render_template("admin/obat_form.html", mode="tambah", obat=None)


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
		santri = Santri.query.get(santri_id) if santri_id else None
		if not santri:
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
			for error in errors:
				flash(error, "danger")
			return render_template("admin/kunjungan_form.html", mode="tambah", kunjungan=request.form,
								   daftar_santri=daftar_santri, daftar_obat=daftar_obat,
								   status_list=STATUS_KUNJUNGAN)
		db.session.add(Kunjungan(santri_id=int(santri_id), tanggal=tanggal_obj, keluhan=keluhan,
								 diagnosa=diagnosa or None, tindakan=tindakan or None, petugas=petugas,
								 status=status, obat_id=obat_obj.id if obat_obj else None,
								 jumlah_obat=jumlah_obat_val))
		if obat_obj and jumlah_obat_val:
			obat_obj.stok -= jumlah_obat_val
		db.session.commit()
		flash("Data kunjungan pemeriksaan berhasil disimpan.", "success")
		return redirect(url_for("admin.kunjungan_list"))
	return render_template("admin/kunjungan_form.html", mode="tambah", kunjungan=None,
						   daftar_santri=daftar_santri, daftar_obat=daftar_obat,
						   status_list=STATUS_KUNJUNGAN)


@admin_bp.route("/santri/<int:santri_id>/ubah", methods=["GET", "POST"])
@login_required
def santri_ubah(santri_id):
	santri = Santri.query.get_or_404(santri_id)
	if request.method == "POST":
		santri.nis = request.form.get("nis", "").strip()
		santri.nama = request.form.get("nama", "").strip()
		santri.jenis_kelamin = request.form.get("jenis_kelamin", "")
		santri.asrama = request.form.get("asrama", "").strip()
		tanggal_lahir = request.form.get("tanggal_lahir", "")
		santri.kontak_wali = request.form.get("kontak_wali", "").strip() or None
		if tanggal_lahir:
			try:
				santri.tanggal_lahir = datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
			except ValueError:
				flash("Format tanggal lahir tidak valid.", "danger")
				return render_template("admin/santri_form.html", mode="ubah", santri=request.form, santri_id=santri_id)
		db.session.commit()
		flash(f"Data santri '{santri.nama}' berhasil diperbarui.", "success")
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


@admin_bp.route("/obat/<int:obat_id>/ubah", methods=["GET", "POST"])
@login_required
def obat_ubah(obat_id):
	obat = Obat.query.get_or_404(obat_id)
	if request.method == "POST":
		obat.nama_obat = request.form.get("nama_obat", "").strip()
		obat.satuan = request.form.get("satuan", "").strip()
		obat.stok = int(request.form.get("stok", "0"))
		obat.stok_minimum = int(request.form.get("stok_minimum", "10") or 10)
		obat.keterangan = request.form.get("keterangan", "").strip() or None
		db.session.commit()
		flash(f"Data obat '{obat.nama_obat}' berhasil diperbarui.", "success")
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


@admin_bp.route("/kunjungan/<int:kunjungan_id>/ubah", methods=["GET", "POST"])
@login_required
def kunjungan_ubah(kunjungan_id):
	kunjungan = Kunjungan.query.get_or_404(kunjungan_id)
	daftar_santri = Santri.query.order_by(Santri.nama).all()
	daftar_obat = Obat.query.order_by(Obat.nama_obat).all()
	if request.method == "POST":
		tanggal = request.form.get("tanggal", "")
		try:
			tanggal_obj = datetime.strptime(tanggal, "%Y-%m-%d").date()
		except ValueError:
			flash("Format tanggal tidak valid.", "danger")
			return render_template("admin/kunjungan_form.html", mode="ubah", kunjungan=request.form,
								   kunjungan_id=kunjungan_id, daftar_santri=daftar_santri,
								   daftar_obat=daftar_obat, status_list=STATUS_KUNJUNGAN)
		kunjungan.santri_id = int(request.form.get("santri_id"))
		kunjungan.tanggal = tanggal_obj
		kunjungan.keluhan = request.form.get("keluhan", "").strip()
		kunjungan.diagnosa = request.form.get("diagnosa", "").strip() or None
		kunjungan.tindakan = request.form.get("tindakan", "").strip() or None
		kunjungan.petugas = request.form.get("petugas", "").strip()
		kunjungan.status = request.form.get("status", "")
		db.session.commit()
		flash("Data kunjungan berhasil diperbarui.", "success")
		return redirect(url_for("admin.kunjungan_list"))
	return render_template("admin/kunjungan_form.html", mode="ubah", kunjungan=kunjungan,
						   kunjungan_id=kunjungan_id, daftar_santri=daftar_santri,
						   daftar_obat=daftar_obat, status_list=STATUS_KUNJUNGAN)


@admin_bp.route("/kunjungan/<int:kunjungan_id>/hapus", methods=["POST"])
@login_required
def kunjungan_hapus(kunjungan_id):
	kunjungan = Kunjungan.query.get_or_404(kunjungan_id)
	db.session.delete(kunjungan)
	db.session.commit()
	flash("Data kunjungan berhasil dihapus.", "success")
	return redirect(url_for("admin.kunjungan_list"))


@admin_bp.route("/obat")
@login_required
def obat_list():
	return render_template("admin/obat_list.html", data_obat=Obat.query.order_by(Obat.nama_obat).all())


@admin_bp.route("/kunjungan")
@login_required
def kunjungan_list():
	data_kunjungan = Kunjungan.query.order_by(Kunjungan.tanggal.desc(), Kunjungan.id.desc()).all()
	return render_template("admin/kunjungan_list.html", data_kunjungan=data_kunjungan)
