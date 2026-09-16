# -*- coding: utf-8 -*-
import calendar
import json
import os

import config


def ensure_dirs():
    os.makedirs(config.ASTREINTES_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(config.ASTREINTES_AGENTS_FILE), exist_ok=True)


# --- Agents ---

def load_agents():
    ensure_dirs()
    if os.path.exists(config.ASTREINTES_AGENTS_FILE):
        with open(config.ASTREINTES_AGENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_agents(agents):
    ensure_dirs()
    with open(config.ASTREINTES_AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)


def next_agent_id(agents):
    return (max((a["id"] for a in agents), default=0)) + 1


def add_agent(name, section):
    agents = load_agents()
    agents.append({"id": next_agent_id(agents), "name": name.strip(), "section": section})
    save_agents(agents)
    return agents


def update_agent(agent_id, name=None, section=None):
    agents = load_agents()
    for a in agents:
        if a["id"] == agent_id:
            if name is not None:
                a["name"] = name.strip()
            if section is not None:
                a["section"] = section
    save_agents(agents)
    return agents


def delete_agent(agent_id):
    agents = [a for a in load_agents() if a["id"] != agent_id]
    save_agents(agents)
    return agents


def agents_by_section():
    agents = load_agents()
    return {section: [a for a in agents if a["section"] == section] for section in config.ASTREINTES_SECTIONS}


# --- Données mensuelles ---

def month_file(year, month):
    return os.path.join(config.ASTREINTES_DATA_DIR, f"{year}-{int(month):02d}.json")


def cell_key(agent_id, day):
    return f"{agent_id}|{day}"


def load_month(year, month):
    ensure_dirs()
    path = month_file(year, month)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cell(year, month, agent_id, day, state):
    ensure_dirs()
    data = load_month(year, month)
    key = cell_key(agent_id, day)
    if state:
        data[key] = state
    else:
        data.pop(key, None)
    with open(month_file(year, month), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def day_letter(year, month, day):
    # Python: Monday=0 ... Sunday=6 -> correspond directement à JOURS_LETTRE_FR
    weekday = __import__("datetime").date(year, month, day).weekday()
    return config.JOURS_LETTRE_FR[weekday]


def is_weekend(year, month, day):
    weekday = __import__("datetime").date(year, month, day).weekday()
    return weekday >= 5
