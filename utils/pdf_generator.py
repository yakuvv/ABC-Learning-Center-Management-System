# utils/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_receipt_pdf(filepath, r):
    """
    Generate an official receipt PDF.
    r keys: receipt_number, date, amount, method, student_name, school_id, grade_level, term, school_year
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
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
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    
    # Divider line
    story.append(Spacer(1, 5))
    divider = Table([[""]], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor("#15165e")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    # Student and Payment details
    details_data = [
        [Paragraph("<b>Student Details</b>", bold_style), Paragraph("<b>Payment Details</b>", bold_style)],
        [
            Paragraph(f"School ID: {r['school_id']}<br/>Student Name: {r['student_name']}<br/>Grade Level: {r['grade_level']}<br/>School Year: {r['school_year']}<br/>Term: {r['term']}", normal_style),
            Paragraph(f"Amount Paid: <b>₱{float(r['amount']):,.2f}</b><br/>Payment Method: {r['method']}<br/>Payment Status: PAID", normal_style)
        ]
    ]
    details_table = Table(details_data, colWidths=[270, 270])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(details_table)
    
    story.append(Spacer(1, 40))
    
    # Message / Thank You
    thank_you_style = ParagraphStyle(
        'ThankYou',
        parent=normal_style,
        alignment=1, # Center
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
    s keys: school_id, studLname, studFname, studMname, grade_level, section, gender, dob, address, school_year, term, enrollment_date, staff_name, parent_name, parent_contact
    subjects: list of subject dicts with subjectName, description
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'RegTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#15165e"),
        alignment=1, # Center
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'RegSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#122aff"),
        alignment=1, # Center
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
    story.append(Paragraph("Official Certificate of Enrollment / Registration Form", subtitle_style))
    
    # Divider
    divider = Table([[""]], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor("#15165e")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))
    
    # Details layout
    mname = f" {s['studMname']}" if s.get('studMname') else ""
    full_name = f"{s['studLname']}, {s['studFname']}{mname}"
    
    details_data = [
        [
            Paragraph("<b>STUDENT INFORMATION</b>", section_title_style),
            Paragraph("<b>ENROLLMENT & PARENT INFORMATION</b>", section_title_style)
        ],
        [
            Paragraph(
                f"<b>Student ID:</b> {s['school_id']}<br/>"
                f"<b>Name:</b> {full_name}<br/>"
                f"<b>Grade & Section:</b> {s['grade_level']} - {s['section']}<br/>"
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
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 15))
    
    # Enrolled Subjects Section
    story.append(Paragraph("<b>ENROLLED SUBJECTS</b>", section_title_style))
    
    subject_table_data = [[
        Paragraph("<b>Subject Name</b>", bold_style),
        Paragraph("<b>Description</b>", bold_style)
    ]]
    for sub in subjects:
        subject_table_data.append([
            Paragraph(sub['subjectName'], normal_style),
            Paragraph(sub['description'] or 'No description available', normal_style)
        ])
        
    subject_table = Table(subject_table_data, colWidths=[180, 360])
    subject_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(subject_table)
    story.append(Spacer(1, 40))
    
    # Signatures
    sig_data = [
        [
            Paragraph("_____________________________<br/><b>Admin / Staff Signature</b>", normal_style),
            Paragraph("_____________________________<br/><b>Parent / Student Signature</b>", normal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sig_table)
    
    doc.build(story)


def generate_grades_pdf(filepath, f, grades):
    """
    Generate Student Grade Sheet.
    f keys: subject, grade_level, term, school_year, tutor_name, date_printed
    grades: list of dicts with name, studentID, subjects (list of dicts)
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
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
    
    # Header
    story.append(Paragraph("ABC Learning Center", title_style))
    story.append(Paragraph("OFFICIAL CLASS GRADE SHEET", subtitle_style))
    
    # Divider
    divider = Table([[""]], colWidths=[540])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor("#15165e")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))
    
    # Details layout
    details_data = [
        [
            Paragraph(f"<b>Grade Level:</b> {f['grade_level']}", normal_style),
            Paragraph(f"<b>Term:</b> {f['term']}<br/><b>School Year:</b> {f['school_year']}", normal_style),
            Paragraph(f"<b>Tutor:</b> {f['tutor_name']}<br/><b>Date Generated:</b> {f['date_printed']}", normal_style)
        ]
    ]
    details_table = Table(details_data, colWidths=[180, 180, 180])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 10))
    
    # Render each student card as a separate sub-table
    is_shs = f['grade_level'] in ["Grade 11", "Grade 12"]
    
    for idx, student in enumerate(grades):
        story.append(Paragraph(f"<b>{idx + 1}. {student['name'].upper()}</b> (School ID: {student['studentID']})", student_title_style))
        
        # Table of subjects & grades for this student (4 Quarters + Final Grade unified format)
        table_data = [[
            Paragraph("<b>Subject Name</b>", bold_style),
            Paragraph("<b>1st Qtr</b>", bold_style),
            Paragraph("<b>2nd Qtr</b>", bold_style),
            Paragraph("<b>3rd Qtr</b>", bold_style),
            Paragraph("<b>4th Qtr</b>", bold_style),
            Paragraph("<b>Final Grade</b>", bold_style)
        ]]
        
        for sub in student['subjects']:
            table_data.append([
                Paragraph(sub['subjectName'], normal_style),
                Paragraph(sub.get('1st', '—'), normal_style),
                Paragraph(sub.get('2nd', '—'), normal_style),
                Paragraph(sub.get('3rd', '—'), normal_style),
                Paragraph(sub.get('4th', '—'), normal_style),
                Paragraph(f"<b>{sub['final']}</b>", normal_style)
            ])
            
        student_table = Table(table_data, colWidths=[240, 55, 55, 55, 55, 80])
        
        student_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(student_table)
        story.append(Spacer(1, 10))
        
    story.append(Spacer(1, 30))
    
    # Signatures
    sig_data = [
        [
            Paragraph("_____________________________<br/><b>Tutor Signature</b>", normal_style),
            Paragraph("_____________________________<br/><b>Admin / Staff Signature</b>", normal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sig_table)
    
    doc.build(story)
