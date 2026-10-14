"""Build the answer PDF: sections a-f from deliverables/, then the 20-row exhibit from audit.py.
Needs reportlab (pip install reportlab). Usage: python3 build_pdf.py [out.pdf]"""
import re
import subprocess
import sys
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

SECTIONS = [
    ("a", "a-what-happened.md", "a. What happened this week"),
    ("b", "b-call-trace.md", "b. One call traced: C-13"),
    ("c", "c-manager-note.md", "c. Note to the workshop manager"),
    ("d", "d-engineering-ticket.md", "d. Engineering ticket"),
    ("e", "e-fix-and-check.md", "e. Fix tonight, and how to check it"),
    ("f", "f-ai-pushback.md", "f. Two AI answers I did not take"),
]


def exhibit_rows():
    out = subprocess.run([sys.executable, "-I", "audit.py"], capture_output=True, text=True, check=True).stdout
    rows = [[c.strip() for c in ln.split("|")] for ln in out.splitlines() if re.match(r"^C-\d\d \|", ln)]
    totals = next(ln for ln in out.splitlines() if ln.startswith("Totals"))
    assert len(rows) == 20, len(rows)
    return rows, totals


def main(dst="answer.pdf"):
    ss = getSampleStyleSheet()
    body, small = ss["BodyText"], ss["BodyText"].clone("small", fontSize=8, leading=10)
    story, heading_words = [Paragraph("Sparsh Motors Kothrud: call audit, 18-23 August", ss["Title"])], 0
    for key, fname, title in SECTIONS:
        p = Path("deliverables") / fname
        if not p.exists():
            print(f"note: section {key} not written yet, skipped")
            continue
        heading_words += len(title.split())
        story.append(Paragraph(title, ss["Heading2"]))
        for para in p.read_text(encoding="utf-8").strip().split("\n\n"):
            html = "<br/>".join(escape(ln) for ln in para.splitlines())
            story += [Paragraph(html, body), Spacer(1, 4)]
    rows, totals = exhibit_rows()
    story += [PageBreak(), Paragraph("Exhibit: contradictions inside each call (not counted in the word limit)", ss["Heading2"])]
    story.append(Paragraph(
        "R1 booked logged, no ok book_appointment. R2 error return, then booked logged "
        "(includes lookup NOT_FOUND). R3 transfer no_answer, no log_callback. "
        "R4 spoken time differs from confirmed_local (heuristic, reads transcript text). "
        "R5 open job card, no get_vehicle_status. X = rule fired. Source: data/2-call-records.md via audit.py.", small))
    data = [["Call", "Logged outcome", "R1", "R2", "R3", "R4", "R5", "Fired"]] + rows
    t = Table(data, repeatRows=1, colWidths=[18 * mm, 48 * mm] + [12 * mm] * 5 + [16 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("ALIGN", (2, 0), (-1, -1), "CENTER")]))
    story += [Spacer(1, 6), t, Spacer(1, 6), Paragraph(escape(totals), small)]
    SimpleDocTemplate(dst, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                      title="Sparsh Motors call audit").build(story)
    print(f"wrote {dst}; section headings added by this script: {heading_words} words (not in deliverables/)")


if __name__ == "__main__":
    main(*sys.argv[1:2])
