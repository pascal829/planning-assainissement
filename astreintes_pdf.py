# -*- coding: utf-8 -*-
"""
Export PDF du planning mensuel d'astreintes.

Ce module ne lit JAMAIS les fichiers directement : il passe uniquement par
astreintes_storage (agents_by_section / load_month). Donc que les données
viennent de fichiers JSON ou de Supabase, ce fichier n'a pas à changer,
tant que ces deux fonctions renvoient :
  - agents_by_section() -> {section: [{"id":..., "name":...}, ...]}
  - load_month(year, month) -> {"<agent_id>|<jour>": "bleu"|"orange", ...}
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import config
import astreintes_storage as astore

NAME_COL_WIDTH = 42 * mm
DAY_COL_WIDTH = 7.7 * mm
ROW_HEIGHT = 6.5 * mm

WEEKEND_BG = colors.HexColor("#F2F2F2")
SECTION_BG = colors.HexColor("#D9D9D9")
HEADER_BG = colors.HexColor("#DCE6F1")


def build_astreintes_pdf(buf, year, month):
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
    mois_nom = config.MOIS_FR[month - 1]

    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A3),
        leftMargin=10 * mm, rightMargin=10 * mm,
        topMargin=10 * mm, bottomMargin=10 * mm,
        title=f"Astreintes {mois_nom} {year}",
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"<b>ASTREINTES — {mois_nom} {year}</b>", styles["Title"]),
        Spacer(1, 6),
    ]

    n_cols = 1 + nb_jours
    style_cmds = []

    # --- En-têtes : ligne "mois" fusionnée, puis lettres, puis numéros ---
    row_mois = [""] + [mois_nom] + [""] * (nb_jours - 1)
    row_lettres = [""] + [j["lettre"] for j in jours]
    row_nums = [""] + [str(j["num"]) for j in jours]
    table_data = [row_mois, row_lettres, row_nums]
    style_cmds.append(("SPAN", (1, 0), (nb_jours, 0)))

    # --- Lignes agents, groupées par section ---
    for section in config.ASTREINTES_SECTIONS:
        r = len(table_data)
        table_data.append([section] + [""] * (n_cols - 1))
        style_cmds += [
            ("SPAN", (0, r), (-1, r)),
            ("BACKGROUND", (0, r), (-1, r), SECTION_BG),
            ("FONTNAME", (0, r), (-1, r), "Helvetica-Bold"),
            ("ALIGN", (0, r), (-1, r), "LEFT"),
        ]

        for agent in agents_par_section.get(section, []):
            r = len(table_data)
            line = [agent["name"]]
            for j in jours:
                state = data.get(astore.cell_key(agent["id"], j["num"]), "")
                line.append("")
                col = j["num"]  # 1..nb_jours -> index colonne
                if state and state in config.ASTREINTES_STATES:
                    style_cmds.append(
                        ("BACKGROUND", (col, r), (col, r),
                         colors.HexColor(config.ASTREINTES_STATES[state]))
                    )
                elif j["weekend"]:
                    style_cmds.append(("BACKGROUND", (col, r), (col, r), WEEKEND_BG))
            table_data.append(line)

    # Week-ends grisés aussi dans les lignes d'en-tête
    for j in jours:
        if j["weekend"]:
            style_cmds.append(("BACKGROUND", (j["num"], 1), (j["num"], 2), colors.HexColor("#C9C9C9")))

    col_widths = [NAME_COL_WIDTH] + [DAY_COL_WIDTH] * nb_jours
    table = Table(table_data, colWidths=col_widths, rowHeights=ROW_HEIGHT)
    table.hAlign = "LEFT"
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 2), HEADER_BG),
        ("FONTNAME", (0, 0), (-1, 2), "Helvetica-Bold"),
        ("LEFTPADDING", (0, 0), (0, -1), 4),
        ("ALIGN", (0, 3), (0, -1), "LEFT"),
    ] + style_cmds))
    story.append(table)

    # --- Légende ---
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Légende</b>", styles["Heading3"]))
    legend_rows = [["", "Astreinte semaine"], ["", "Astreinte week-end"]]
    legend_table = Table(legend_rows, colWidths=[12 * mm, 60 * mm], rowHeights=6 * mm)
    legend_table.hAlign = "LEFT"
    legend_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(config.ASTREINTES_STATES["bleu"])),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor(config.ASTREINTES_STATES["orange"])),
    ]))
    story.append(legend_table)

    doc.build(story)