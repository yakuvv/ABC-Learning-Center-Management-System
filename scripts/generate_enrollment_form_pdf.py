import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_blank_enrollment_form(filepath):
    # I generate a print-ready physical enrollment form matching the system flow, consisting only of Sections 1 to 3 plus signatures.
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 0.4 inch margins for maximizing printable area
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=letter,
        leftMargin=28, 
        rightMargin=28,
        topMargin=28, 
        bottomMargin=28
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom color palette
    PRIMARY_COLOR = colors.HexColor("#15165e")
    TEXT_COLOR = colors.HexColor("#1e293b")
    LINE_COLOR = colors.HexColor("#94a3b8")
    BG_LIGHT = colors.HexColor("#f8fafc")
    
    # Typography Styles
    title_style = ParagraphStyle(
        'FormTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=PRIMARY_COLOR,
        alignment=1,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'FormSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
        spaceAfter=8
    )
    
    section_title_style = ParagraphStyle(
        'FormSectionTitle',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=PRIMARY_COLOR,
        spaceBefore=6,
        spaceAfter=4
    )
    
    field_label_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=TEXT_COLOR
    )
    
    instruction_style = ParagraphStyle(
        'FormInstruction',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        textColor=colors.HexColor("#475569")
    )
    
    batch_option_style = ParagraphStyle(
        'BatchOption',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=TEXT_COLOR,
        leading=9
    )
    
    # Header Section
    story.append(Paragraph("ABC Learning Center", title_style))
    story.append(Paragraph("PHYSICAL ENROLLMENT & REGISTRATION FORM", subtitle_style))
    story.append(Paragraph("Instructions: Fields marked with a red asterisk (<font color=\"red\">*</font>) are required. Please write legibly in BLOCK LETTERS.", instruction_style))
    story.append(Spacer(1, 6))
    
    # Section 1: Student Information
    story.append(Paragraph("1. STUDENT INFORMATION", section_title_style))
    student_data = [
        [
            Paragraph("Last Name <font color=\"red\">*</font>:", field_label_style), "",
            Paragraph("First Name <font color=\"red\">*</font>:", field_label_style), "",
            Paragraph("Middle Name:", field_label_style), ""
        ],
        [
            Paragraph("Date of Birth <font color=\"red\">*</font>:", field_label_style), Paragraph("MM - DD - YYYY", instruction_style),
            Paragraph("Gender <font color=\"red\">*</font>:", field_label_style), Paragraph("[  ] Male   [  ] Female", field_label_style),
            Paragraph("Grade Level <font color=\"red\">*</font>:", field_label_style), Paragraph("", instruction_style)
        ],
        [
            Paragraph("Contact Number <font color=\"red\">*</font>:", field_label_style), "", "",
            Paragraph("Email Address:", field_label_style), "", ""
        ],
        [
            Paragraph("Full Address:", field_label_style), "", "", "", "", ""
        ]
    ]
    
    # Setup structural layout grid for student info
    student_table = Table(
        student_data, 
        colWidths=[95, 95, 75, 100, 95, 95],
        rowHeights=[20, 20, 20, 20]
    )
    student_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Row 1 underlines
        ('LINEBELOW', (1, 0), (1, 0), 0.75, LINE_COLOR),
        ('LINEBELOW', (3, 0), (3, 0), 0.75, LINE_COLOR),
        ('LINEBELOW', (5, 0), (5, 0), 0.75, LINE_COLOR),
        # Row 2 underlines
        ('LINEBELOW', (1, 1), (1, 1), 0.75, LINE_COLOR),
        ('LINEBELOW', (5, 1), (5, 1), 0.75, LINE_COLOR),
        # Row 3 underlines (spanned cells for write-in)
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (4, 2), (5, 2)),
        ('LINEBELOW', (1, 2), (2, 2), 0.75, LINE_COLOR),
        ('LINEBELOW', (4, 2), (5, 2), 0.75, LINE_COLOR),
        # Address underline span
        ('SPAN', (1, 3), (5, 3)),
        ('LINEBELOW', (1, 3), (5, 3), 0.75, LINE_COLOR),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 10))
    
    # Section 2: Parent/Guardian Information
    story.append(Paragraph("2. PARENT / GUARDIAN INFORMATION", section_title_style))
    parent_data = [
        [
            Paragraph("Parent Name <font color=\"red\">*</font>:", field_label_style), "",
            Paragraph("Relationship <font color=\"red\">*</font>:", field_label_style), Paragraph("(e.g., Mother, Father, etc.)", instruction_style)
        ],
        [
            Paragraph("Contact Number <font color=\"red\">*</font>:", field_label_style), "",
            Paragraph("Email Address:", field_label_style), ""
        ]
    ]
    parent_table = Table(
        parent_data, 
        colWidths=[110, 167, 110, 167],
        rowHeights=[20, 20]
    )
    parent_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Underlines for write-in fields
        ('LINEBELOW', (1, 0), (1, 0), 0.75, LINE_COLOR),
        ('LINEBELOW', (3, 0), (3, 0), 0.75, LINE_COLOR),
        ('LINEBELOW', (1, 1), (1, 1), 0.75, LINE_COLOR),
        ('LINEBELOW', (3, 1), (3, 1), 0.75, LINE_COLOR),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(parent_table)
    story.append(Spacer(1, 10))
    
    # Section 3: Subject Enrollment Details
    story.append(Paragraph("3. SUBJECT ENROLLMENT DETAILS", section_title_style))
    
    # Clean Term selector Paragraph (no table boxes)
    story.append(Paragraph("<b>Term to Enroll <font color=\"red\">*</font>:</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; [  ] <b>Term 1</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; [  ] <b>Term 2</b>", field_label_style))
    story.append(Spacer(1, 4))
    
    # Checkbox strings for the fixed Batch A and Batch B choices
    batch_a_label = Paragraph("[  ] <b>Batch A</b> (Saturday 9:00 AM - 11:00 AM)", batch_option_style)
    batch_b_label = Paragraph("[  ] <b>Batch B</b> (Sunday 1:00 PM - 3:00 PM)", batch_option_style)
    
    enrollment_data = [
        [
            Paragraph("<b>Subject Name to Enroll</b>", field_label_style), "",
            Paragraph("<b>Preferred Schedule / Batch</b>", field_label_style), ""
        ],
        ["", "", batch_a_label, batch_b_label],
        ["", "", batch_a_label, batch_b_label],
        ["", "", batch_a_label, batch_b_label],
        ["", "", batch_a_label, batch_b_label],
        ["", "", batch_a_label, batch_b_label],
        ["", "", batch_a_label, batch_b_label],
        ["", "", batch_a_label, batch_b_label],
        ["", "", batch_a_label, batch_b_label]
    ]
    
    enrollment_table = Table(
        enrollment_data, 
        colWidths=[210, 20, 162, 162],
        rowHeights=[20, 20, 20, 20, 20, 20, 20, 20, 20]
    )
    enrollment_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Header styles
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        # Spans for the subject text fields (cols 0 and 1 merge)
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (0, 4), (1, 4)),
        ('SPAN', (0, 5), (1, 5)),
        ('SPAN', (0, 6), (1, 6)),
        ('SPAN', (0, 7), (1, 7)),
        ('SPAN', (0, 8), (1, 8)),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(enrollment_table)
    story.append(Spacer(1, 15))
    
    # Section 4: Undertaking & Signatures
    undertaking_text = (
        "<b>Statement of Agreement:</b> I hereby certify that the information provided in this form is "
        "accurate and up-to-date. I understand that the information will be processed and encoded into the "
        "ABC Learning Center Management System by the administrative staff to complete the enrollment process."
    )
    story.append(Paragraph(undertaking_text, instruction_style))
    story.append(Spacer(1, 25))
    
    sig_data = [
        [
            Paragraph("__________________________________________<br/><b>Student / Parent Signature</b>", field_label_style),
            Paragraph("__________________________________________<br/><b>Date Signed (YYYY-MM-DD)</b>", field_label_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[277, 277])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(sig_table)
    
    doc.build(story)
    print(f"Successfully generated blank enrollment form PDF at: {filepath}")

if __name__ == "__main__":
    # Generate the form inside the forms directory
    target_path = r"c:\Users\anj\Documents\ABC-Learning-Center-Management-System\forms\ABC_Enrollment_Form.pdf"
    generate_blank_enrollment_form(target_path)
