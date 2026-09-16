# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

import psycopg
import config


# ============================================================
# Connexion Supabase
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas définie.")


# ============================================================
# Migration
# ============================================================

def migrate_planning(conn):
    print("\n--- PLANNINGS ---")

    data_dir = Path(config.DATA_DIR)
    files = sorted(data_dir.glob("*.json"))

    for path in files:
        # On ne traite ici que les fichiers du type 2026-W37.json
        if "-W" not in path.stem:
            continue

        try:
            year_str, week_str = path.stem.split("-W")
            year = int(year_str)
            week = int(week_str)
        except ValueError:
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0

        for key, value in data.items():
            parts = key.split("|", 3)

            if len(parts) != 4:
                print(f"  ⚠️ Clé ignorée : {key}")
                continue

            row_label, day, half_day, agent = parts

            conn.execute(
                """
                INSERT INTO planning_cells
                    (year, week, row_label, day, half_day, agent, value)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT
                    (year, week, row_label, day, half_day, agent)
                DO UPDATE SET value = EXCLUDED.value
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

            count += 1

        print(f"  ✓ {path.name} : {count} cellules")


def migrate_legend(conn):
    print("\n--- LÉGENDE ---")

    if not os.path.exists(config.LEGEND_FILE):
        print("  Aucun fichier de légende trouvé.")
        return

    with open(config.LEGEND_FILE, "r", encoding="utf-8") as f:
        legend = json.load(f)

    for entry in legend:
        code = entry.get("code")

        if not code:
            continue

        conn.execute(
            """
            INSERT INTO legend
                (code, label, bg, fg, data)
            VALUES
                (%s, %s, %s, %s, %s)
            ON CONFLICT (code)
            DO UPDATE SET
                label = EXCLUDED.label,
                bg = EXCLUDED.bg,
                fg = EXCLUDED.fg,
                data = EXCLUDED.data
            """,
            (
                code,
                entry.get("label", ""),
                entry.get("bg", ""),
                entry.get("fg", ""),
                json.dumps(entry, ensure_ascii=False),
            ),
        )

    print(f"  ✓ {len(legend)} entrées de légende")


def migrate_notes(conn):
    print("\n--- NOTES ---")

    if not os.path.exists(config.NOTES_FILE):
        print("  Aucun fichier de notes trouvé.")
        return

    with open(config.NOTES_FILE, "r", encoding="utf-8") as f:
        notes = json.load(f)

    if isinstance(notes, dict):
        notes = [
            {"num": int(num), "text": text}
            for num, text in notes.items()
        ]

    for note in notes:
        conn.execute(
            """
            INSERT INTO notes (num, text)
            VALUES (%s, %s)
            ON CONFLICT (num)
            DO UPDATE SET text = EXCLUDED.text
            """,
            (
                note["num"],
                note.get("text", ""),
            ),
        )

    print(f"  ✓ {len(notes)} notes")


def migrate_astreintes_agents(conn):
    print("\n--- AGENTS D'ASTREINTE ---")

    path = Path(config.ASTREINTES_AGENTS_FILE)

    if not path.exists():
        print("  Aucun fichier d'agents trouvé.")
        return

    with open(path, "r", encoding="utf-8") as f:
        agents = json.load(f)

    for agent in agents:
        conn.execute(
            """
            INSERT INTO astreintes_agents
                (id, name, section)
            VALUES
                (%s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE SET
                name = EXCLUDED.name,
                section = EXCLUDED.section
            """,
            (
                agent["id"],
                agent["name"],
                agent["section"],
            ),
        )

    print(f"  ✓ {len(agents)} agents")


def migrate_astreintes_cells(conn):
    print("\n--- ASTREINTES ---")

    data_dir = Path(config.ASTREINTES_DATA_DIR)

    if not data_dir.exists():
        print("  Aucun dossier d'astreintes trouvé.")
        return

    files = sorted(data_dir.glob("*.json"))

    for path in files:
        # Les fichiers mensuels sont du type 2026-09.json
        if len(path.stem) != 7 or "-" not in path.stem:
            continue

        try:
            year_str, month_str = path.stem.split("-")
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0

        for key, state in data.items():
            parts = key.split("|", 1)

            if len(parts) != 2:
                print(f"  ⚠️ Clé ignorée : {key}")
                continue

            agent_id = int(parts[0])
            day = int(parts[1])

            conn.execute(
                """
                INSERT INTO astreintes_cells
                    (year, month, agent_id, day, state)
                VALUES
                    (%s, %s, %s, %s, %s)
                ON CONFLICT
                    (year, month, agent_id, day)
                DO UPDATE SET state = EXCLUDED.state
                """,
                (
                    year,
                    month,
                    agent_id,
                    day,
                    state,
                ),
            )

            count += 1

        print(f"  ✓ {path.name} : {count} cellules")


# ============================================================
# Programme principal
# ============================================================

def main():
    print("==========================================")
    print(" MIGRATION JSON → SUPABASE")
    print("==========================================")

    with psycopg.connect(DATABASE_URL) as conn:

        migrate_planning(conn)
        migrate_legend(conn)
        migrate_notes(conn)
        migrate_astreintes_agents(conn)
        migrate_astreintes_cells(conn)

        conn.commit()

    print("\n==========================================")
    print(" MIGRATION TERMINÉE")
    print("==========================================")


if __name__ == "__main__":
    main()