# pdf_generator.py – Blue Tick Data™ 0.1.5 (Insurer Demo Build)
# Generates insurer-grade PDF certificate with 2-column layout + QR code

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, HRFlowable, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from datetime import datetime
import uuid
import json
import os


# BRAND COLOURS
CORPORATE_BLUE = colors.HexColor("#143A5E")
SILVER = colors.HexColor("#D9D9D9")

# RISK COLOUR MAP
RISK_COLOURS = {
    "LOW": colors.green,
    "GUARDED": colors.blue,
    "MEDIUM": colors.orange,
    "HIGH": colors.red,
    "CRITICAL": colors.darkred
}


def make_qr_code(url, size=120):
    qr_code = qr.QrCodeWidget(url)
    drawing = Drawing(size, size)
    drawing.add(qr_code, name='qr')
    # Tint QR code
    for element in drawing.contents:
        if hasattr(element, "fillColor"):
            element.fillColor = CORPORATE_BLUE
    return drawing


def generate_pdf(path, data):
    styles = getSampleStyleSheet()

    title = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=22, textColor=CORPORATE_BLUE, leading=26, spaceAfter=20)
    subtitle = ParagraphStyle("Subtitle", parent=styles["Heading2"], fontSize=14, textColor=colors.black, spaceAfter=12)
    header_style = ParagraphStyle("Header", parent=styles["Heading3"], fontSize=12, textColor=CORPORATE_BLUE, spaceAfter=6)
    normal = styles["BodyText"]

    story = []

    # HEADER
    cert_id = data.get("certificate_id", str(uuid.uuid4()))
    issued = data.get("verified_at", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    version = data.get("version", "0.1.5")
    url = f"https://bluetickdata.ai/cert/{cert_id}"

    story.append(Paragraph("BLUE TICK DATA™", title))
    story.append(Paragraph("Dataset Verification Certificate", subtitle))
    story.append(Paragraph(f"Version {version}", normal))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Certificate ID:</b> {cert_id}", normal))
    story.append(Paragraph(f"<b>Issued:</b> {issued}", normal))
    story.append(Paragraph(f"<b>Verification URL:</b> {url}", normal))

    # QR
    story.append(make_qr_code(url))
    story.append(Spacer(1, 20))

    # 2-COLUMN SUMMARY
    dataset = data.get("dataset", {})
    overall = data.get("overall_risk", {})

    left_col = [
        [Paragraph("<b>Dataset Hash:</b>", header_style), Paragraph(str(dataset.get("dataset_hash", "—")), normal)],
        [Paragraph("<b>Manifest Hash:</b>", header_style), Paragraph(str(dataset.get("manifest_hash", "—")), normal)],
        [Paragraph("<b>Total Files:</b>", header_style), Paragraph(str(dataset.get("total_files", "—")), normal)],
        [Paragraph("<b>Dataset Size (GB):</b>", header_style), Paragraph(str(dataset.get("dataset_size_gb", "—")), normal)],
        [Paragraph("<b>MIME Breakdown:</b>", header_style), Paragraph(json.dumps(dataset.get("mime_breakdown", {}), indent=2), normal)],
        [Paragraph("<b>Verification Scope:</b>", header_style), Paragraph(dataset.get("verification_scope", "—"), normal)]
    ]

    right_col = [
        [Paragraph("<b>Overall Score:</b>", header_style), Paragraph(str(overall.get("score", "—")), normal)],
        [Paragraph("<b>Risk Band:</b>", header_style), Paragraph(overall.get("risk_band", "—"), normal)],
        [Paragraph("<b>Coverage Level:</b>", header_style), Paragraph(overall.get("coverage_level", "—"), normal)],
        [Paragraph("<b>Premium Adjustment:</b>", header_style), Paragraph(overall.get("premium_adjustment", "—"), normal)],
        [Paragraph("<b>Claim Triggers:</b>", header_style), Paragraph("<br/>".join(data.get("claim_triggers", [])), normal)]
    ]

    table = Table([[left_col, right_col]], colWidths=[270, 270])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, CORPORATE_BLUE),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, SILVER),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # FILE BREAKDOWN
    story.append(Paragraph("File Breakdown (Extract)", header_style))
    file_rows = [[Paragraph(h, header_style) for h in ["Filename", "Hash", "Score", "Risk", "Cover"]]]

    for f in data.get("files", [])[:25]:
        file_rows.append([
            Paragraph(f.get("filename", "—"), normal),
            Paragraph(f.get("sha256", "—")[:12] + "...", normal),
            Paragraph(str(f.get("score", "—")), normal),
            Paragraph(f.get("risk_band", "—"), normal),
            Paragraph(f.get("coverage_level", "—"), normal)
        ])

    file_table = Table(file_rows, colWidths=[150, 130, 80, 80, 100])
    file_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, SILVER),
        ('BACKGROUND', (0, 0), (-1, 0), CORPORATE_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
    ]))
    story.append(file_table)
    story.append(Spacer(1, 20))

    # COMMERCIAL INFO
    story.append(Paragraph("Commercial Information", header_style))
    comm = data.get("commercial", {})

    commercial_table = Table([
        [Paragraph("Verification Certificate Fee (Demo Only):", header_style), Paragraph(str(comm.get("certificate_fee", "£—")), normal)],
        [Paragraph("Premium Adjustment:", header_style), Paragraph(str(overall.get("premium_adjustment", "—")), normal)],
        [Paragraph("Commission Model:", header_style), Paragraph("Blue Tick Data™ operates on a partner commission basis (details upon request).", normal)]
    ])
    commercial_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, SILVER),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (0, 1), colors.whitesmoke)
    ]))
    story.append(commercial_table)
    story.append(Spacer(1, 30))

    # FOOTER
    story.append(HRFlowable(width="100%", color=SILVER))
    story.append(Paragraph(
        "Prototype Certificate – Not For Production Use<br/>"
        "© Blue Tick Data™ 2025 — Dataset Verification & AI Compliance<br/>"
        "<a href='https://bluetickdata.ai'>https://bluetickdata.ai</a>",
        normal
    ))

    # BUILD PDF
    pdf = SimpleDocTemplate(path, pagesize=A4)
    pdf.build(story)
