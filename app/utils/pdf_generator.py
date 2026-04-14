import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        name="SubTitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        spaceAfter=10,
    ))
    return styles


def generate_report_card_pdf(student_data: dict, grades: list[dict], comments: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = get_styles()
    elements = []

    elements.append(Paragraph("Alif24 School ERP", styles["TitleCenter"]))
    elements.append(Paragraph(
        f"Tabella — {student_data.get('full_name', '')}",
        styles["SubTitle"],
    ))
    elements.append(Spacer(1, 12))

    info_data = [
        ["O'quvchi:", student_data.get("full_name", "")],
        ["Sinf:", student_data.get("class_name", "")],
        ["O'quv yili:", student_data.get("academic_year", "")],
        ["Semestr:", str(student_data.get("semester", ""))],
    ]
    info_table = Table(info_data, colWidths=[4 * cm, 10 * cm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    grade_header = ["#", "Fan", "Baho", "Max baho", "Izoh"]
    grade_data = [grade_header]
    for i, g in enumerate(grades, 1):
        grade_data.append([
            str(i),
            g.get("subject", ""),
            str(g.get("grade", "")),
            str(g.get("max_grade", "")),
            g.get("comment", ""),
        ])

    grade_table = Table(grade_data, colWidths=[1 * cm, 5 * cm, 2 * cm, 2 * cm, 6 * cm])
    grade_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(grade_table)
    elements.append(Spacer(1, 20))

    if comments.get("teacher_comments"):
        elements.append(Paragraph(
            f"<b>O'qituvchi izohi:</b> {comments['teacher_comments']}",
            styles["Normal"],
        ))
        elements.append(Spacer(1, 8))

    if comments.get("principal_comments"):
        elements.append(Paragraph(
            f"<b>Direktor izohi:</b> {comments['principal_comments']}",
            styles["Normal"],
        ))

    doc.build(elements)
    return buffer.getvalue()


def generate_invoice_pdf(invoice_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = get_styles()
    elements = []

    elements.append(Paragraph("Alif24 School ERP", styles["TitleCenter"]))
    elements.append(Paragraph(f"Hisob-faktura #{invoice_data.get('invoice_number', '')}", styles["SubTitle"]))
    elements.append(Spacer(1, 20))

    info = [
        ["O'quvchi:", invoice_data.get("student_name", "")],
        ["Sana:", invoice_data.get("issue_date", "")],
        ["To'lov muddati:", invoice_data.get("due_date", "")],
    ]
    info_table = Table(info, colWidths=[4 * cm, 10 * cm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    items_header = ["#", "Tavsif", "Summa (UZS)"]
    items_data = [items_header]
    for i, item in enumerate(invoice_data.get("items", []), 1):
        items_data.append([str(i), item.get("description", ""), f"{item.get('amount', 0):,.0f}"])
    items_data.append(["", "Jami:", f"{invoice_data.get('total_amount', 0):,.0f}"])

    items_table = Table(items_data, colWidths=[1.5 * cm, 10 * cm, 4.5 * cm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (1, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)

    doc.build(elements)
    return buffer.getvalue()
