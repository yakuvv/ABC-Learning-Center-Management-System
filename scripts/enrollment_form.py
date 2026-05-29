"""
ABC Learning Center — Printed Enrollment Form (reference + PDF generator)

This file documents what parents/students write on paper at the center.
Staff then encodes the same information in the desktop system:
  - Profile Students  -> Section I & II (if new student)
  - Manage Enrollment -> Section III & IV (subjects + batch schedule)
  - Process Payment   -> Section V

Run:
  python scripts/enrollment_form.py              # print field outline in terminal
  python scripts/enrollment_form.py --pdf        # create forms/ABC_Enrollment_Form.pdf
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# FORM CONTENT (what appears on the printed document)
# ---------------------------------------------------------------------------

FORM_TITLE = "ABC LEARNING CENTER"
FORM_SUBTITLE = "Supplementary Tutorial & Review — Enrollment Form"
FORM_NOTE = (
    "For students enrolled in a regular school (Grade 1–12) who need extra help "
    "in selected subjects. Please print clearly. Submit this form to the admin desk."
)

FORM_SECTIONS = [
    {
        "id": "I",
        "title": "STUDENT INFORMATION",
        "fields": [
            ("Last Name", "_______________________________"),
            ("First Name", "_______________________________"),
            ("Middle Name", "_______________________________"),
            ("Gender", "☐ Male   ☐ Female"),
            ("Date of Birth (MM-DD-YYYY)", "_______________________________"),
            ("Complete Address", "_______________________________________________"),
            ("Student Contact No.", "_______________________________"),
            ("Email (optional)", "_______________________________"),
        ],
        "system_module": "Profile Students -> Add New Student",
    },
    {
        "id": "II",
        "title": "PARENT / GUARDIAN",
        "fields": [
            ("Full Name", "_______________________________"),
            ("Contact Number", "_______________________________"),
            ("Relationship to Student", "☐ Mother  ☐ Father  ☐ Guardian  ☐ Other: ________"),
        ],
        "system_module": "Profile Students -> Parent/Guardian section",
    },
    {
        "id": "III",
        "title": "REGULAR SCHOOL (Mon–Fri)",
        "fields": [
            ("Name of Current School", "_______________________________"),
            ("Grade Level this School Year", "☐ G1 ☐ G2 ☐ G3 ☐ G4 ☐ G5 ☐ G6 ☐ G7 ☐ G8 ☐ G9 ☐ G10 ☐ G11 ☐ G12"),
            ("SHS Strand (if Grade 11–12 only)", "☐ STEM  ☐ ABM  ☐ HUMSS  ☐ N/A"),
        ],
        "system_module": "Profile Students -> Regular School Info",
    },
    {
        "id": "IV",
        "title": "TUTORIAL SUBJECTS REQUESTED",
        "description": (
            "Check only the subjects the student needs help with at ABC Learning Center. "
            "Staff will assign an available class schedule (batch)."
        ),
        "subject_checklist_elementary": [
            "☐ Mathematics", "☐ English", "☐ Filipino", "☐ Science",
            "☐ Araling Panlipunan", "☐ MAPEH", "☐ ESP",
        ],
        "subject_checklist_junior_high": [
            "☐ Mathematics", "☐ English", "☐ Science", "☐ Filipino",
            "☐ Araling Panlipunan", "☐ MAPEH", "☐ ESP", "☐ TLE", "☐ Computer Education",
        ],
        "subject_checklist_senior_high": [
            "☐ General Mathematics", "☐ Oral Communication", "☐ Reading and Writing",
            "☐ Physical Education and Health", "☐ Other: _______________________",
        ],
        "schedule_table": {
            "headers": ["Subject (checked above)", "Preferred day", "Preferred time", "Notes"],
            "rows": 4,
            "example": "Mathematics | Saturday | 9:00 AM | ",
        },
        "system_module": "Manage Enrollment -> check subjects + pick Class schedule (batch)",
    },
    {
        "id": "V",
        "title": "PAYMENT (per subject / as quoted by staff)",
        "fields": [
            ("Fee quoted per subject (₱)", "_______________________________"),
            ("Total amount paid today (₱)", "_______________________________"),
            ("Payment method", "☐ Cash   ☐ GCash   ☐ Bank Transfer"),
            ("Official receipt requested", "☐ Yes"),
        ],
        "system_module": "Process Payment -> per subject enrollment",
    },
    {
        "id": "VI",
        "title": "DECLARATION & SIGNATURES",
        "fields": [
            (
                "Agreement",
                "I certify that the information above is true. I understand that ABC Learning "
                "Center provides supplementary tutoring only (not a replacement school) and "
                "that fees are per subject/session as explained by staff.",
            ),
            ("Parent/Guardian Signature", "_______________________________   Date: __________"),
            ("Received by (Staff Name)", "_______________________________   Date: __________"),
        ],
        "system_module": "Staff login records enrollment; receipt issued after payment",
    },
]


def _ascii_safe(text: str) -> str:
    """Avoid Windows console encoding errors."""
    return (
        text.replace("\u2610", "[ ]")
        .replace("\u2013", "-")
        .replace("\u2192", "->")
        .replace("\u20b1", "PHP ")
    )


def print_form_outline():
    """Show form content in the terminal."""
    print("=" * 72)
    print(FORM_TITLE.center(72))
    print(FORM_SUBTITLE.center(72))
    print("=" * 72)
    print(f"\n{_ascii_safe(FORM_NOTE)}\n")
    for sec in FORM_SECTIONS:
        print(f"\n--- Section {sec['id']}: {sec['title']} ---")
        if sec.get("description"):
            print(f"    {_ascii_safe(sec['description'])}")
        if sec.get("system_module"):
            print(f"    [Encoded in system: {sec['system_module']}]")
        for item in sec.get("fields", []):
            if isinstance(item, tuple):
                label, blank = item
                print(f"    - {_ascii_safe(label)}: {_ascii_safe(blank)}")
            else:
                print(f"    - {_ascii_safe(item)}")
        for key in ("subject_checklist_elementary", "subject_checklist_junior_high", "subject_checklist_senior_high"):
            if key in sec:
                label = key.replace("subject_checklist_", "").replace("_", " ").title()
                print(f"    ({label})")
                for s in sec[key]:
                    print(f"      {_ascii_safe(s)}")
        if sec.get("schedule_table"):
            st = sec["schedule_table"]
            print(f"    Schedule preferences ({st['rows']} rows):")
            print(f"      Columns: {' | '.join(st['headers'])}")
            print(f"      Example: {st['example']}")
    print("\n" + "=" * 72)
    print("End of form. Parents keep a copy if staff provides one; original stays at center.")
    print("=" * 72)


def generate_form_pdf(output_path: str | None = None) -> str:
    """Create a printable PDF version of the enrollment form."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "forms")
    os.makedirs(out_dir, exist_ok=True)
    if output_path is None:
        output_path = os.path.join(out_dir, "ABC_Enrollment_Form.pdf")

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "FormTitle", parent=styles["Heading1"],
        fontName="Helvetica-Bold", fontSize=18,
        textColor=colors.HexColor("#15165e"), alignment=1, spaceAfter=6,
    )
    sub = ParagraphStyle(
        "FormSub", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#334155"), alignment=1, spaceAfter=12,
    )
    section = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12,
        textColor=colors.HexColor("#15165e"), spaceBefore=14, spaceAfter=8,
    )
    body = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, leading=14, textColor=colors.HexColor("#1e293b"),
    )
    small = ParagraphStyle(
        "Small", parent=body, fontSize=9, textColor=colors.HexColor("#64748b"),
    )

    story = []
    story.append(Paragraph(FORM_TITLE, title))
    story.append(Paragraph(FORM_SUBTITLE, sub))
    story.append(Paragraph(FORM_NOTE, small))
    story.append(Paragraph(f"<i>Form version — {datetime.now().strftime('%B %Y')}</i>", small))
    story.append(Spacer(1, 8))

    for sec in FORM_SECTIONS:
        story.append(Paragraph(f"{sec['id']}. {sec['title']}", section))
        if sec.get("description"):
            story.append(Paragraph(sec["description"], small))
        rows = []
        for item in sec.get("fields", []):
            if isinstance(item, tuple):
                label, blank = item
                rows.append([
                    Paragraph(f"<b>{label}</b>", body),
                    Paragraph(blank, body),
                ])
            else:
                rows.append([Paragraph(item, body), Paragraph("", body)])
        if rows:
            t = Table(rows, colWidths=[180, 320])
            t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(t)

        for key, heading in [
            ("subject_checklist_elementary", "Elementary (Grades 1–6) — check subjects needed:"),
            ("subject_checklist_junior_high", "Junior High (Grades 7–10):"),
            ("subject_checklist_senior_high", "Senior High (Grades 11–12):"),
        ]:
            if key in sec:
                story.append(Paragraph(heading, body))
                line = " &nbsp;&nbsp; ".join(sec[key])
                story.append(Paragraph(line, body))
                story.append(Spacer(1, 6))

        if sec.get("schedule_table"):
            st = sec["schedule_table"]
            story.append(Paragraph("<b>Preferred class schedule (staff will confirm availability):</b>", body))
            sched_data = [st["headers"]]
            for _ in range(st["rows"]):
                sched_data.append(["", "", "", ""])
            stbl = Table(sched_data, colWidths=[140, 100, 100, 160])
            stbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#15165e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(stbl)
            story.append(Spacer(1, 8))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "<b>For office use only:</b> Learner ID assigned: _________________ "
        "Encoded by: _________________ Date: __________",
        small,
    ))

    doc.build(story)
    return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(description="ABC Learning Center enrollment form reference")
    parser.add_argument("--pdf", action="store_true", help="Generate printable PDF in forms/")
    args = parser.parse_args()
    print_form_outline()
    if args.pdf:
        path = generate_form_pdf()
        print(f"\nPDF saved to:\n  {path}")


if __name__ == "__main__":
    main()
