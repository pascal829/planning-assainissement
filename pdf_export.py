# -*- coding: utf-8 -*-
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import config
import storage

LABEL_COL_WIDTH = 28 * mm
CELL_WIDTH = 7 * mm
ROW_HEIGHT = 6 * mm


def build_pdf(buf, year, week):
    data = storage.load_week(year, week)
    legend = storage.load_legend()
    legend_map = storage.legend_lookup(legend)

    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A3),
        leftMargin=10 * mm, rightMargin=10 * mm,
        topMargin=10 * mm, bottomMargin=10 * mm,
    )
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph(
        f"<b>REGIE ASSAINISSEMENT</b> — Semaine {week} — {storage.week_date_range_label(year, week)}",
        styles["Title"],
    )
    story.append(title)
    story.append(Spacer(1, 6))

    n_agents = len(config.AGENTS)

    # --- Construction des lignes d'en-tête ---
    header_days = [""]
    header_halves = [""]
    header_agents = [""]
    for day in config.DAYS:
        for half in config.HALF_DAYS:
            header_days.append(day)
            header_days.extend([""] * (n_agents - 1))
            header_halves.append(half)
            header_halves.extend([""] * (n_agents - 1))
            header_agents.extend(config.AGENTS)

    table_data = [header_days, header_halves, header_agents]

    # --- Lignes de données, groupées par section ---
    style_cmds = []
    current_section = None
    for row_idx, row in enumerate(config.ROWS, start=3):
        if row["section"] != current_section:
            current_section = row["section"]
            n_cols = 1 + len(config.DAYS) * len(config.HALF_DAYS) * n_agents
            table_data.append([current_section] + [""] * (n_cols - 1))
            style_cmds.append(("SPAN", (0, len(table_data) - 1), (-1, len(table_data) - 1)))
            style_cmds.append(("BACKGROUND", (0, len(table_data) - 1), (-1, len(table_data) - 1), colors.HexColor("#D6D80A")))
            style_cmds.append(("FONTNAME", (0, len(table_data) - 1), (-1, len(table_data) - 1), "Helvetica-Bold"))

        line = [row["label"]]
        col = 1
        for day in config.DAYS:
            for half in config.HALF_DAYS:
                for agent in config.AGENTS:
                    key = storage.cell_key(row["label"], day, half, agent)
                    value = data.get(key, "")
                    line.append(value)
                    if value and value in legend_map:
                        entry = legend_map[value]
                        r = len(table_data)  # ligne où cette valeur sera ajoutée
                        style_cmds.append(("BACKGROUND", (col, r), (col, r), colors.HexColor(entry["bg"])))
                        style_cmds.append(("TEXTCOLOR", (col, r), (col, r), colors.HexColor(entry["fg"])))
                    col += 1
        table_data.append(line)

    # --- Fusions des en-têtes (jours / demi-journées) ---
    col = 1
    for day in config.DAYS:
        style_cmds.append(("SPAN", (col, 0), (col + 2 * n_agents - 1, 0)))
        for half in config.HALF_DAYS:
            style_cmds.append(("SPAN", (col, 1), (col + n_agents - 1, 1)))
            col += n_agents

    col_widths = [LABEL_COL_WIDTH] + [CELL_WIDTH] * (len(config.DAYS) * len(config.HALF_DAYS) * n_agents)

    table = Table(table_data, colWidths=col_widths, rowHeights=ROW_HEIGHT)
    table.hAlign = "LEFT"
    base_style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 2), colors.HexColor("#DCE6F1")),
        ("FONTNAME", (0, 0), (-1, 2), "Helvetica-Bold"),
    ]
    table.setStyle(TableStyle(base_style + style_cmds))
    story.append(table)
    story.append(Spacer(1, 10))

    # --- Légende ---
    story.append(Paragraph("<b>Légende</b>", styles["Heading3"]))
    legend_rows = []
    legend_style = []
    for i, entry in enumerate(legend):
        legend_rows.append([entry["code"], entry["label"]])
        legend_style.append(("BACKGROUND", (0, i), (0, i), colors.HexColor(entry["bg"])))
        legend_style.append(("TEXTCOLOR", (0, i), (0, i), colors.HexColor(entry["fg"])))
    if legend_rows:
        legend_table = Table(legend_rows, colWidths=[15 * mm, 90 * mm])
        legend_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ] + legend_style))
        story.append(legend_table)

    # --- Notes numérotées ---
    notes = [n for n in storage.load_notes() if n["text"]]
    if notes:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Notes</b>", styles["Heading3"]))
        notes_rows = [[str(n["num"]), n["text"]] for n in notes]
        notes_style = [("BACKGROUND", (0, i), (0, i), colors.black) for i in range(len(notes_rows))]
        notes_style += [("TEXTCOLOR", (0, i), (0, i), colors.white) for i in range(len(notes_rows))]
        notes_table = Table(notes_rows, colWidths=[10 * mm, 160 * mm])
        notes_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ] + notes_style))
        story.append(notes_table)

    doc.build(story)
