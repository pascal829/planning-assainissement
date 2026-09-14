# -*- coding: utf-8 -*-
"""
Configuration du planning.
Modifie librement ces listes pour coller à ton organisation
(agents, jours travaillés, lignes du tableau, codes de légende).
"""

# Initiales des agents (colonnes du tableau, une par agent)
AGENTS = ["La", "Pa", "Me", "Ar", "De"]

# Jours de la semaine affichés
DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

# Demi-journées
HALF_DAYS = ["Matin", "Après-midi"]

# Lignes du tableau, regroupées par section.
# "section" affiche un bandeau de titre au-dessus du groupe de lignes.
ROWS = [
    {"section": "ASSAINISSEMENT", "label": "Queyras"},
    {"section": "ASSAINISSEMENT", "label": "Guillestre"},
    {"section": "ASSAINISSEMENT", "label": "Autres"},
    {"section": "ASSAINISSEMENT", "label": "Bureau"},
    {"section": "ASSAINISSEMENT", "label": "Réunions"},
    {"section": "ASSAINISSEMENT", "label": "Arrêt Maladie"},
    {"section": "ASSAINISSEMENT", "label": "Congés"},
]

# Légende par défaut : code -> (libellé, couleur de fond, couleur de texte)
# Les couleurs sont utilisées à l'écran ET dans le PDF exporté.
DEFAULT_LEGEND = [
    {"code": "X", "label": "Assainissement", "bg": "#FFFFFF", "fg": "#000000"},
    {"code": "R", "label": "Point hebdomadaire", "bg": "#4A90D9", "fg": "#FFFFFF"},
    {"code": "D", "label": "Télétravail", "bg": "#FFFFFF", "fg": "#000000"},
    {"code": "M", "label": "Ménage voitures/STEP", "bg": "#000000", "fg": "#FFFFFF"},
    {"code": "E", "label": "Etalonnage A1", "bg": "#FFFFFF", "fg": "#000000"},
    {"code": "J", "label": "Journée cohésion", "bg": "#E03C31", "fg": "#FFFFFF"},
    {"code": "T", "label": "RTT", "bg": "#000000", "fg": "#FFFFFF"},
]

import os

DATA_DIR = "data/plannings"
LEGEND_FILE = "data/legend.json"
NOTES_FILE = "data/notes.json"
NUMBERED_NOTES_COUNT = 10

# --- Accès protégé à la page "Gérer la légende" ---
# Change ce mot de passe (ou définis la variable d'environnement ADMIN_PASSWORD
# sur ton serveur de déploiement plutôt que de le laisser en clair ici).
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Clé secrète Flask pour signer les sessions. En production, définis la
# variable d'environnement SECRET_KEY avec une valeur longue et aléatoire.
SECRET_KEY = os.environ.get("SECRET_KEY")

# --- Module "Astreintes" (planning mensuel, 12 mois / an) ---
ASTREINTES_SECTIONS = ["ASTREINTES D'EXPLOITATION", "ASTREINTES DE DECISION"]

# États possibles d'une case et leur couleur (cycle au clic : vide -> bleu -> orange -> vide)
ASTREINTES_STATES = {
    "bleu": "#2E75B6",
    "orange": "#C0530A",
}

ASTREINTES_AGENTS_FILE = "data/astreintes_agents.json"
ASTREINTES_DATA_DIR = "data/astreintes"

MOIS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]
JOURS_LETTRE_FR = ["L", "M", "M", "J", "V", "S", "D"]  # Lundi..Dimanche
