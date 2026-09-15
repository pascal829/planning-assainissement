# -*- coding: utf-8 -*-

import os
from datetime import date, timedelta

import psycopg
import config


def get_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL n'est pas définie.")

    return psycopg.connect(database_url)


def ensure_dirs():
    """
    Conservé pour compatibilité avec l'ancien système JSON.
    Les données sont maintenant stockées dans Supabase.
    """
    return None


def cell_key(row_label, day, half_day, agent):
    return f"{row_label}|{day}|{half_day}|{agent}"


def week_file(year, week):
    """
    Conservé pour compatibilité avec l'ancien code.
    """
    return os.path.join(
        config.DATA_DIR,
        f"{year}-W{int(week):02d}.json"
    )


# ============================================================
# PLANNING
# ============================================================

def load_week(year, week):
    data = {}

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT row_label, day, half_day, agent, value
            FROM planning_cells
            WHERE year = %s
              AND week = %s
            """,
            (year, week),
        ).fetchall()

    for row_label, day, half_day, agent, value in rows:
        key = cell_key(row_label, day, half_day, agent)
        data[key] = value

    return data


def save_cell(year, week, row_label, day, half_day, agent, value):

    with get_connection() as conn:

        if value:
            conn.execute(
                """
                INSERT INTO planning_cells
                    (year, week, row_label, day, half_day, agent, value)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)

                ON CONFLICT
                    (year, week, row_label, day, half_day, agent)

                DO UPDATE SET
                    value = EXCLUDED.value
                """,
                (
                    year,
                    week,
                    row_label,
                    day,
                    half_day,
                    agent,
                    value,
                ),
            )

        else:
            conn.execute(
                """
                DELETE FROM planning_cells
                WHERE year = %s
                  AND week = %s
                  AND row_label = %s
                  AND day = %s
                  AND half_day = %s
                  AND agent = %s
                """,
                (
                    year,
                    week,
                    row_label,
                    day,
                    half_day,
                    agent,
                ),
            )

        conn.commit()


# ============================================================
# LÉGENDE
# ============================================================

def load_legend():

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT data, code, label, bg, fg
            FROM legend
            ORDER BY code
            """
        ).fetchall()

    if not rows:
        return list(config.DEFAULT_LEGEND)

    result = []

    for data, code, label, bg, fg in rows:

        if data:
            entry = dict(data)
        else:
            entry = {
                "code": code,
                "label": label,
                "bg": bg,
                "fg": fg,
            }

        result.append(entry)

    return result


def save_legend(legend):

    with get_connection() as conn:

        conn.execute("DELETE FROM legend")

        for entry in legend:

            code = entry.get("code", "")

            conn.execute(
                """
                INSERT INTO legend
                    (code, label, bg, fg, data)
                VALUES
                    (%s, %s, %s, %s, %s)
                """,
                (
                    code,
                    entry.get("label", ""),
                    entry.get("bg", ""),
                    entry.get("fg", ""),
                    psycopg.types.json.Jsonb(entry),
                ),
            )

        conn.commit()


# ============================================================
# NOTES
# ============================================================

def load_notes():
    """
    Liste de {num, text} pour les onglets numérotés 1..N.
    """

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT num, text
            FROM notes
            """
        ).fetchall()

    saved_map = {
        str(num): text
        for num, text in rows
    }

    return [
        {
            "num": i,
            "text": saved_map.get(str(i), "")
        }
        for i in range(
            1,
            config.NUMBERED_NOTES_COUNT + 1
        )
    ]


def save_notes(notes):

    with get_connection() as conn:

        for note in notes:

            conn.execute(
                """
                INSERT INTO notes (num, text)
                VALUES (%s, %s)

                ON CONFLICT (num)
                DO UPDATE SET
                    text = EXCLUDED.text
                """,
                (
                    note["num"],
                    note.get("text", ""),
                ),
            )

        conn.commit()


# ============================================================
# OUTILS
# ============================================================

def legend_lookup(legend):
    """
    dict code -> entrée légende,
    pour colorer les cases rapidement.
    """
    return {
        entry["code"]: entry
        for entry in legend
    }


def monday_of_iso_week(year, week):
    # Le jeudi de la semaine ISO tombe toujours
    # dans la bonne année/semaine.
    jan4 = date(year, 1, 4)

    week1_monday = (
        jan4 -
        timedelta(days=jan4.isoweekday() - 1)
    )

    return week1_monday + timedelta(
        weeks=week - 1
    )


def week_date_range_label(year, week):

    monday = monday_of_iso_week(year, week)
    friday = monday + timedelta(days=4)

    mois_fr = [
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    ]

    if monday.month == friday.month:

        return (
            f"du lundi {monday.day} "
            f"au vendredi {friday.day} "
            f"{mois_fr[friday.month - 1]}"
        )

    return (
        f"du lundi {monday.day} "
        f"{mois_fr[monday.month - 1]} "
        f"au vendredi {friday.day} "
        f"{mois_fr[friday.month - 1]}"
    )