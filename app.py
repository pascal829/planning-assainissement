# -*- coding: utf-8 -*-
from datetime import date
from io import BytesIO

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for

import config
import storage
from auth import admin_required

app = Flask(__name__)
@app.route("/ping")
def ping():
    return "OK", 200
app.secret_key = config.SECRET_KEY

from astreintes import astreintes_bp
app.register_blueprint(astreintes_bp, url_prefix="/astreintes")


def current_year_week():
    today = date.today()
    y, w, _ = today.isocalendar()
    return y, w


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == config.ADMIN_PASSWORD:
            session["is_admin"] = True
            next_url = request.args.get("next") or url_for("legende")
            return redirect(next_url)
        error = "Mot de passe incorrect."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/")
def index():
    year = request.args.get("year", type=int)
    week = request.args.get("week", type=int)
    if not year or not week:
        year, week = current_year_week()

    data = storage.load_week(year, week)
    legend = storage.load_legend()
    legend_map = storage.legend_lookup(legend)
    notes = storage.load_notes()

    # semaine précédente / suivante (gère le passage d'année)
    prev_date = storage.monday_of_iso_week(year, week) - __import__("datetime").timedelta(days=7)
    next_date = storage.monday_of_iso_week(year, week) + __import__("datetime").timedelta(days=7)
    prev_year, prev_week, _ = prev_date.isocalendar()
    next_year, next_week, _ = next_date.isocalendar()

    return render_template(
        "index.html",
        year=year,
        week=week,
        date_range=storage.week_date_range_label(year, week),
        agents=config.AGENTS,
        days=config.DAYS,
        half_days=config.HALF_DAYS,
        rows=config.ROWS,
        data=data,
        legend=legend,
        legend_map=legend_map,
        notes=notes,
        prev_year=prev_year, prev_week=prev_week,
        next_year=next_year, next_week=next_week,
        cell_key=storage.cell_key,
    )


@app.route("/api/save", methods=["POST"])
def api_save():
    payload = request.get_json()
    storage.save_cell(
        payload["year"], payload["week"],
        payload["row"], payload["day"], payload["half"], payload["agent"],
        payload["value"].strip(),
    )
    return jsonify({"ok": True})


@app.route("/legende", methods=["GET", "POST"])
@admin_required
def legende():
    if request.method == "POST":
        codes = request.form.getlist("code")
        labels = request.form.getlist("label")
        bgs = request.form.getlist("bg")
        fgs = request.form.getlist("fg")
        legend = []
        for code, label, bg, fg in zip(codes, labels, bgs, fgs):
            code = code.strip()
            if code:
                legend.append({"code": code, "label": label.strip(), "bg": bg, "fg": fg})
        storage.save_legend(legend)
    return render_template("legende.html", legend=storage.load_legend(), notes=storage.load_notes())


@app.route("/notes/save", methods=["POST"])
@admin_required
def notes_save():
    notes = []
    for i in range(1, config.NUMBERED_NOTES_COUNT + 1):
        text = request.form.get(f"note_{i}", "").strip()
        notes.append({"num": i, "text": text})
    storage.save_notes(notes)
    return render_template("legende.html", legend=storage.load_legend(), notes=notes)


@app.route("/export/pdf")
def export_pdf():
    year = request.args.get("year", type=int)
    week = request.args.get("week", type=int)
    if not year or not week:
        year, week = current_year_week()

    from pdf_export import build_pdf
    buf = BytesIO()
    build_pdf(buf, year, week)
    buf.seek(0)
    filename = f"planning_semaine_{week:02d}_{year}.pdf"
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=filename)


if __name__ == "__main__":
    storage.ensure_dirs()
    app.run(debug=True, host="0.0.0.0", port=5000)
