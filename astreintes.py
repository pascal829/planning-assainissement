# -*- coding: utf-8 -*-
from datetime import date

from flask import Blueprint, render_template, request, jsonify, redirect, url_for

import config
import astreintes_storage as astore
from auth import admin_required

astreintes_bp = Blueprint("astreintes", __name__, template_folder="templates")


@astreintes_bp.route("/")
def index():
    today = date.today()
    return redirect(url_for("astreintes.month_view", year=today.year, month=today.month))


@astreintes_bp.route("/<int:year>/<int:month>")
def month_view(year, month):
    # normalise un mois hors bornes (ex: mois 13 -> janvier année suivante)
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1

    nb_jours = astore.days_in_month(year, month)
    jours = [
        {
            "num": d,
            "lettre": astore.day_letter(year, month, d),
            "weekend": astore.is_weekend(year, month, d),
        }
        for d in range(1, nb_jours + 1)
    ]
    data = astore.load_month(year, month)
    agents_par_section = astore.agents_by_section()

    prev_month, prev_year = (month - 1, year) if month > 1 else (12, year - 1)
    next_month, next_year = (month + 1, year) if month < 12 else (1, year + 1)

    return render_template(
        "astreintes.html",
        year=year, month=month,
        mois_nom=config.MOIS_FR[month - 1],
        jours=jours,
        sections=config.ASTREINTES_SECTIONS,
        agents_par_section=agents_par_section,
        data=data,
        states=config.ASTREINTES_STATES,
        cell_key=astore.cell_key,
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month,
    )


@astreintes_bp.route("/api/save", methods=["POST"])
def api_save():
    payload = request.get_json()
    astore.save_cell(
        payload["year"], payload["month"],
        payload["agent_id"], payload["day"], payload["state"],
    )
    return jsonify({"ok": True})


@astreintes_bp.route("/agents", methods=["GET", "POST"])
@admin_required
def agents():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            name = request.form.get("name", "").strip()
            section = request.form.get("section")
            if name and section in config.ASTREINTES_SECTIONS:
                astore.add_agent(name, section)
        elif action == "update":
            agent_id = int(request.form.get("agent_id"))
            astore.update_agent(
                agent_id,
                name=request.form.get("name", "").strip(),
                section=request.form.get("section"),
            )
        elif action == "delete":
            agent_id = int(request.form.get("agent_id"))
            astore.delete_agent(agent_id)
        return redirect(url_for("astreintes.agents"))

    return render_template(
        "astreintes_agents.html",
        agents=astore.load_agents(),
        sections=config.ASTREINTES_SECTIONS,
    )
