# -*- coding: utf-8 -*-

import calendar
import os
from datetime import date

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


# ============================================================
# AGENTS
# ============================================================

def load_agents():

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, section
            FROM astreintes_agents
            ORDER BY id
            """
        ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "section": row[2],
        }
        for row in rows
    ]


def save_agents(agents):

    with get_connection() as conn:

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

        conn.commit()


def next_agent_id(agents):
    return (
        max(
            (a["id"] for a in agents),
            default=0
        )
        + 1
    )


def add_agent(name, section):

    agents = load_agents()

    agent = {
        "id": next_agent_id(agents),
        "name": name.strip(),
        "section": section,
    }

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO astreintes_agents
                (id, name, section)
            VALUES
                (%s, %s, %s)
            """,
            (
                agent["id"],
                agent["name"],
                agent["section"],
            ),
        )

        conn.commit()

    agents.append(agent)

    return agents


def update_agent(agent_id, name=None, section=None):

    agents = load_agents()

    for agent in agents:

        if agent["id"] == agent_id:

            if name is not None:
                agent["name"] = name.strip()

            if section is not None:
                agent["section"] = section

            break

    save_agents(agents)

    return agents


def delete_agent(agent_id):

    agents = [
        a
        for a in load_agents()
        if a["id"] != agent_id
    ]

    with get_connection() as conn:

        conn.execute(
            """
            DELETE FROM astreintes_agents
            WHERE id = %s
            """,
            (agent_id,),
        )

        conn.commit()

    return agents


def agents_by_section():

    agents = load_agents()

    return {
        section: [
            a
            for a in agents
            if a["section"] == section
        ]
        for section in config.ASTREINTES_SECTIONS
    }


# ============================================================
# DONNÉES MENSUELLES
# ============================================================

def month_file(year, month):
    """
    Conservé pour compatibilité avec l'ancien code JSON.
    """
    return os.path.join(
        config.ASTREINTES_DATA_DIR,
        f"{year}-{int(month):02d}.json"
    )


def cell_key(agent_id, day):
    return f"{agent_id}|{day}"


def load_month(year, month):

    data = {}

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT agent_id, day, state
            FROM astreintes_cells
            WHERE year = %s
              AND month = %s
            """,
            (
                year,
                month,
            ),
        ).fetchall()

    for agent_id, day, state in rows:

        key = cell_key(agent_id, day)

        data[key] = state

    return data


def save_cell(year, month, agent_id, day, state):

    with get_connection() as conn:

        if state:

            conn.execute(
                """
                INSERT INTO astreintes_cells
                    (year, month, agent_id, day, state)
                VALUES
                    (%s, %s, %s, %s, %s)

                ON CONFLICT
                    (year, month, agent_id, day)

                DO UPDATE SET
                    state = EXCLUDED.state
                """,
                (
                    year,
                    month,
                    agent_id,
                    day,
                    state,
                ),
            )

        else:

            conn.execute(
                """
                DELETE FROM astreintes_cells
                WHERE year = %s
                  AND month = %s
                  AND agent_id = %s
                  AND day = %s
                """,
                (
                    year,
                    month,
                    agent_id,
                    day,
                ),
            )

        conn.commit()


# ============================================================
# CALENDRIER
# ============================================================

def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def day_letter(year, month, day):

    weekday = date(
        year,
        month,
        day
    ).weekday()

    return config.JOURS_LETTRE_FR[weekday]


def is_weekend(year, month, day):

    weekday = date(
        year,
        month,
        day
    ).weekday()

    return weekday >= 5