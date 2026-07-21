from datetime import date
from flask import Blueprint, render_template, current_app
from sqlalchemy import extract

from models import Santri, Kunjungan, Obat

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
	today = date.today()

	total_santri = Santri.query.count()
	total_kunjungan_bulan_ini = Kunjungan.query.filter(
		extract("month", Kunjungan.tanggal) == today.month,
		extract("year", Kunjungan.tanggal) == today.year,
	).count()
	total_jenis_obat = Obat.query.count()

	return render_template(
		"public/index.html",
		nama_pesantren=current_app.config["NAMA_PESANTREN"],
		total_santri=total_santri,
		total_kunjungan_bulan_ini=total_kunjungan_bulan_ini,
		total_jenis_obat=total_jenis_obat,
	)