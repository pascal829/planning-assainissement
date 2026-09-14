# -*- coding: utf-8 -*-
import json
import os
from datetime import date, timedelta

import config


def ensure_dirs():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(config.LEGEND_FILE), exist_ok=True)


def cell_key(row_label, day, half_day, agent):
    return f"{row_label}|{day}|{half_day}|{agent}"


def week_file(year, week):
    return os.path.join(config.DATA_DIR, f"{year}-W{int(week):02d}.json")


def load_week(year, week):
    ensure_dirs()
    path = week_file(year, week)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cell(year, week, row_label, day, half_day, agent, value):
    ensure_dirs()
    data = load_week(year, week)
    key = cell_key(row_label, day, half_day, agent)
    if value:
        data[key] = value
    else:
        data.pop(key, None)
    path = week_file(year, week)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_legend():
    ensure_dirs()
    if os.path.exists(config.LEGEND_FILE):
        with open(config.LEGEND_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return list(config.DEFAULT_LEGEND)


def save_legend(legend):
    ensure_dirs()
    with open(config.LEGEND_FILE, "w", encoding="utf-8") as f:
        json.dump(legend, f, ensure_ascii=False, indent=2)


def load_notes():
    """Liste de {num, text} pour les onglets numérotés 1..N (notes libres)."""
    ensure_dirs()
    if os.path.exists(config.NOTES_FILE):
        with open(config.NOTES_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
    else:
        saved = {}
    saved_map = {str(n["num"]): n["text"] for n in saved} if isinstance(saved, list) else saved
    return [
        {"num": i, "text": saved_map.get(str(i), "")}
        for i in range(1, config.NUMBERED_NOTES_COUNT + 1)
    ]


def save_notes(notes):
    ensure_dirs()
    with open(config.NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def legend_lookup(legend):
    """dict code -> entrée légende, pour colorer les cases rapidement."""
    return {entry["code"]: entry for entry in legend}


def monday_of_iso_week(year, week):
    # Le jeudi de la semaine ISO tombe toujours dans la bonne année/semaine
    jan4 = date(year, 1, 4)
    week1_monday = jan4 - timedelta(days=jan4.isoweekday() - 1)
    return week1_monday + timedelta(weeks=week - 1)


def week_date_range_label(year, week):
    monday = monday_of_iso_week(year, week)
    friday = monday + timedelta(days=4)
    mois_fr = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre",
    ]
    if monday.month == friday.month:
        return (f"du lundi {monday.day} au vendredi {friday.day} "
                f"{mois_fr[friday.month - 1]}")
    return (f"du lundi {monday.day} {mois_fr[monday.month - 1]} "
            f"au vendredi {friday.day} {mois_fr[friday.month - 1]}")
