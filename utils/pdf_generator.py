# utils/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def _receipt_payment_lines(r):
    lines = [
        f"Amount Paid: <b>₱{float(r['amount']):,.2f}</b>",
        f"Payment Method: {r['method']}",
    ]
    if (r.get("method") or "").lower() == "cash":
        tendered = r.get("amount_tendered")
        if tendered is not None:
            lines.append(f"Cash Received: ₱{float(tendered):,.2f}")
        change = r.get("change_due")
        if change is not None and float(change) > 0:
            lines.append(f"Change: ₱{float(change):,.2f}")
    lines.append("Payment Status: PAID")
    return "<br/>".join(lines)


def generate_receipt_pdf(filepath, r):
    """
    Generate an official receipt PDF.
    r keys: receipt_number, date, amount, amount_tendered, change_due, method, ...
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            leftMargin=36, rightMargin=36,
                            topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor("#15165e"),
        spaceAfter=15
    )

    normal_style = ParagraphStyle(
        'ReceiptNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#1e293b"),
        leading=14
    )

    bold_style = ParagraphStyle(
        'ReceiptBold',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )

    # Title
    story.append(Paragraph("ABC Learning Center", title_style))

    # Header Section
    header_data = [
        [
            Paragraph("<b>ABC Learning Center Management System</b><br/>Lan-Based Desktop System", normal_style),
            Paragraph(f"<b>OFFICIAL RECEIPT</b><br/><b>Receipt No:</b> {r['receipt_number']}<br/><b>Date:</b> {r['date']}", normal_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(header_table)

    # Divider line
    story.append(Spacer(1, 5))
    divider = Table([[""]], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor("#15165e")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))

    # Student and Payment details
    details_data = [
        [Paragraph("<b>Student Details</b>", bold_style),
         Paragraph("<b>Payment Details</b>", bold_style)],
        [
            Paragraph(
                f"School ID: {r['school_id']}<br/>"
                f"Student Name: {r['student_name']}<br/>"
                f"Grade Level: {r['grade_level']}<br/>"
                f"School Year: {r['school_year']}<br/>"
                f"Term: {r['term']}",
                normal_style
            ),
            Paragraph(_receipt_payment_lines(r), normal_style)
        ]
    ]
    details_table = Table(details_data, colWidths=[270, 270])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)

    enrolled = r.get("enrolled_lines") or []
    if enrolled:
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            "<b>Enrolled Subjects (per term · 2-hour sessions)</b>", bold_style
        ))
        for line in enrolled:
            story.append(Paragraph(f"• {line}", normal_style))

    if r.get("total_due") is not None:
        story.append(Spacer(1, 10))
        bal_after = r.get("balance_after", 0)
        story.append(Paragraph(
            f"<b>Enrollment fees (term):</b> ₱{float(r['total_due']):,.2f}<br/>"
            f"<b>Total paid to date:</b> ₱{float(r.get('total_paid', r['amount'])):,.2f}<br/>"
            f"<b>Remaining balance:</b> ₱{float(bal_after):,.2f}",
            normal_style,
        ))

    story.append(Spacer(1, 40))

    # Thank you
    thank_you_style = ParagraphStyle(
        'ThankYou',
        parent=normal_style,
        alignment=1,
        fontName='Helvetica-Oblique',
        fontSize=11,
        textColor=colors.HexColor("#64748b")
    )
    story.append(Paragraph("Thank you for choosing ABC Learning Center!", thank_you_style))
    story.append(Spacer(1, 10))

    doc.build(story)


def generate_registration_pdf(filepath, s, subjects):
    """
    Generate Certificate of Enrollment / Registration Form.
    s keys: school_id, studLname, studFname, studMname, grade_level, section,
            gender, dob, address, school_year, term, enrollment_date, staff_name,
            parent_name, parent_contact
    subjects: list of subject dicts with subjectName, description
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            leftMargin=36, rightMargin=36,
                            topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'RegTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#15165e"),
        alignment=1,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'RegSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#122aff"),
        alignment=1,
        spaceAfter=15
    )

    section_title_style = ParagraphStyle(
        'RegSectionTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor("#15165e"),
        spaceBefore=10,
        spaceAfter=5
    )

    normal_style = ParagraphStyle(
        'RegNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#1e293b"),
        leading=12
    )

    bold_style = ParagraphStyle(
        'RegBold',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )

    # Header
    story.append(Paragraph("ABC Learning Center", title_style))
    story.append(Paragraph("Official Certificate of Enrollment / Registration Form",
                            subtitle_style))

    # Divider
    divider = Table([[""]], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, colors.HexColor("#15165e")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))

    # Details layout
    mname     = f" {s['studMname']}" if s.get('studMname') else ""
    full_name = f"{s['studLname']}, {s['studFname']}{mname}"

    details_data = [
        [
            Paragraph("<b>STUDENT INFORMATION</b>", section_title_style),
            Paragraph("<b>ENROLLMENT &amp; PARENT INFORMATION</b>", section_title_style)
        ],
        [
            Paragraph(
                f"<b>Student ID:</b> {s['school_id']}<br/>"
                f"<b>Name:</b> {full_name}<br/>"
                f"<b>Grade &amp; Section:</b> {s['grade_level']} - {s['section']}<br/>"
                f"<b>Gender:</b> {s['gender']}<br/>"
                f"<b>Date of Birth:</b> {s['dob']}<br/>"
                f"<b>Address:</b> {s['address'] or '—'}",
                normal_style
            ),
            Paragraph(
                f"<b>School Year:</b> {s['school_year']}<br/>"
                f"<b>Term:</b> {s['term']}<br/>"
                f"<b>Enrollment Date:</b> {s['enrollment_date']}<br/>"
                f"<b>Registered By (Staff):</b> {s['staff_name'] or '—'}<br/>"
                f"<b>Parent/Guardian:</b> {s['parent_name'] or '—'}<br/>"
                f"<b>Parent Contact No:</b> {s['parent_contact'] or '—'}",
                normal_style
            )
        ]
    ]

    details_table = Table(details_data, colWidths=[270, 270])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 15))

    # Enrolled Subjects Section
    story.append(Paragraph("<b>ENROLLED SUBJECTS</b>", section_title_style))

    subject_table_data = [[
        Paragraph("<b>Subject Name</b>", bold_style),
        Paragraph("<b>Description</b>",  bold_style)
    ]]
    for sub in subjects:
        subject_table_data.append([
            Paragraph(sub['subjectName'], normal_style),
            Paragraph(sub['description'] or 'No description available', normal_style)
        ])

    subject_table = Table(subject_table_data, colWidths=[180, 360])
    subject_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND',    (0, 0), (-1,  0), colors.HexColor("#f8fafc")),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(subject_table)
    story.append(Spacer(1, 40))

    # Signatures
    sig_data = [[
        Paragraph("_____________________________<br/><b>Admin / Staff Signature</b>",
                  normal_style),
        Paragraph("_____________________________<br/><b>Parent / Student Signature</b>",
                  normal_style)
    ]]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('ALIGN',  (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(sig_table)

    doc.build(story)


def generate_grades_pdf(filepath, f, grades):
    """
    Generate Student Grade Sheet (simplified single overall grade per subject).
    f keys: subject, grade_level, term, school_year, tutor_name, date_printed
    grades: list of dicts with name, studentID, subjects (list of dicts with
            subjectName, numeric, letter, description)
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            leftMargin=36, rightMargin=36,
                            topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'GradesTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#15165e"),
        alignment=1,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'GradesSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#122aff"),
        alignment=1,
        spaceAfter=15
    )

    normal_style = ParagraphStyle(
        'GradesNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#1e293b"),
        leading=12
    )

    bold_style = ParagraphStyle(
        'GradesBold',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )

    student_title_style = ParagraphStyle(
        'StudentTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor("#15165e"),
        spaceBefore=12,
        spaceAfter=4
    )

    # ── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph("ABC Learning Center", title_style))
    story.append(Paragraph("OFFICIAL CLASS GRADE SHEET", subtitle_style))

    divider = Table([[""]], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEBELOW',     (0, 0), (-1, -1), 1.5, colors.HexColor("#15165e")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))

    # ── Sheet meta ───────────────────────────────────────────────────────────
    details_data = [[
        Paragraph(f"<b>Grade Level:</b> {f['grade_level']}", normal_style),
        Paragraph(f"<b>Term:</b> {f['term']}<br/>"
                  f"<b>School Year:</b> {f['school_year']}", normal_style),
        Paragraph(f"<b>Tutor:</b> {f['tutor_name']}<br/>"
                  f"<b>Date Generated:</b> {f['date_printed']}", normal_style),
    ]]
    details_table = Table(details_data, colWidths=[180, 180, 180])
    details_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(details_table)

    # ── Grading scale legend ─────────────────────────────────────────────────
    story.append(Spacer(1, 6))
    legend_data = [[
        Paragraph("<b>Grading Scale:</b>",              bold_style),
        Paragraph("A+ (95–100) Excellent",              normal_style),
        Paragraph("A (90–94) Very Good",                normal_style),
        Paragraph("B+ (85–89) Good",                    normal_style),
        Paragraph("B (80–84) Satisfactory",             normal_style),
        Paragraph("C (75–79) Fair",                     normal_style),
        Paragraph("D/F (&lt;75) Needs Improvement",     normal_style),
    ]]
    legend_table = Table(legend_data, colWidths=[80, 72, 72, 64, 72, 56, 124])
    legend_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('FONTSIZE',      (0, 0), (-1, -1), 7),
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 10))

    # ── Student cards ────────────────────────────────────────────────────────
    for idx, student in enumerate(grades):
        story.append(Paragraph(
            f"<b>{idx + 1}. {student['name'].upper()}</b>"
            f" (School ID: {student['studentID']})",
            student_title_style
        ))

        # Columns: Subject Name | Numeric | Letter | Description
        table_data = [[
            Paragraph("<b>Subject Name</b>",  bold_style),
            Paragraph("<b>Numeric</b>",       bold_style),
            Paragraph("<b>Letter</b>",        bold_style),
            Paragraph("<b>Description</b>",   bold_style),
        ]]

        row_styles = []
        for row_idx, sub in enumerate(student['subjects'], start=1):
            numeric = sub.get('numeric',     '—')
            letter_grade = sub.get('letter',      '—')
            desc    = sub.get('description', '—')

            # Colour-coded grade cells: blue = passing, red = failing
            try:
                num_val    = float(numeric)
                cell_color = (colors.HexColor("#dbeafe")
                              if num_val >= 75
                              else colors.HexColor("#fee2e2"))
            except (ValueError, TypeError):
                cell_color = colors.white

            row_styles.append(
                ('BACKGROUND', (1, row_idx), (3, row_idx), cell_color)
            )

            table_data.append([
                Paragraph(sub['subjectName'],  normal_style),
                Paragraph(f"<b>{numeric}</b>", bold_style),
                Paragraph(f"<b>{letter_grade}</b>",  bold_style),
                Paragraph(desc,                normal_style),
            ])

        student_table = Table(table_data, colWidths=[240, 65, 65, 170])
        base_styles = [
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('BACKGROUND',    (0, 0), (-1,  0), colors.HexColor("#f8fafc")),
            ('ALIGN',         (1, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        student_table.setStyle(TableStyle(base_styles + row_styles))
        story.append(student_table)
        story.append(Spacer(1, 10))

    story.append(Spacer(1, 30))

    # ── Signatures ───────────────────────────────────────────────────────────
    sig_data = [[
        Paragraph("_____________________________<br/><b>Tutor Signature</b>",
                  normal_style),
        Paragraph("_____________________________<br/><b>Admin / Staff Signature</b>",
                  normal_style),
    ]]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('ALIGN',  (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(sig_table)

    doc.build(story)
