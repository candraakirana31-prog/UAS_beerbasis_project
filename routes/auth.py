from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models import Admin

auth_bp = Blueprint("auth", __name__)


def login_required(view_func):
	"""Decorator untuk melindungi halaman admin/dashboard agar tidak bisa diakses tanpa login."""

	@wraps(view_func)
	def wrapped(*args, **kwargs):
		if not session.get("admin_id"):
			flash("Silakan login terlebih dahulu untuk mengakses halaman ini.", "warning")
			return redirect(url_for("auth.login", next=request.path))
		return view_func(*args, **kwargs)

	return wrapped


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if session.get("admin_id"):
		return redirect(url_for("admin.dashboard"))

	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")

		if not username or not password:
			flash("Username dan password wajib diisi.", "danger")
			return render_template("auth/login.html", username=username)

		admin = Admin.query.filter_by(username=username).first()

		if admin and admin.check_password(password):
			session["admin_id"] = admin.id
			session["admin_nama"] = admin.nama_lengkap
			flash(f"Selamat datang, {admin.nama_lengkap}!", "success")
			next_url = request.args.get("next")
			return redirect(next_url or url_for("admin.dashboard"))

		flash("Username atau password salah.", "danger")
		return render_template("auth/login.html", username=username)

	return render_template("auth/login.html", username="")


@auth_bp.route("/logout")
def logout():
	session.clear()
	flash("Anda telah berhasil logout.", "success")
	return redirect(url_for("public.index"))