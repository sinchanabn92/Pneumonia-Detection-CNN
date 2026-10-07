import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.config import settings

def generate_pdf_report(record: dict, output_path: Path) -> Path:
    """
    Generates a professional ReportLab PDF summary for an analysis record.
    Includes:
    - Headers, timestamps, analysis ID
    - Dual image view (Original Chest X-ray and Grad-CAM overlay)
    - Comprehensive numerical metrics (probabilities, confidence, uncertainty, status)
    - Architecture & calibration parameters
    - Prominent research disclaimers
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=8,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#78350f"),
        backColor=colors.HexColor("#fef3c7"),
        borderColor=colors.HexColor("#f59e0b"),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=10,
        spaceAfter=8
    )

    elements = []

    # Title & Subtitle
    elements.append(Paragraph("PNEUMONIA-AI-SYSTEM", title_style))
    elements.append(Paragraph("RESEARCH PROTOTYPE &bull; CLINICAL ANALYSIS REPORT", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

    # Analysis Metadata
    date_str = record.get("created_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    analysis_id = record.get("id", "N/A")
    orig_name = record.get("original_filename", "N/A")

    meta_data = [
        [Paragraph("<b>Analysis ID:</b>", body_style), Paragraph(str(analysis_id), body_style),
         Paragraph("<b>Date/Time:</b>", body_style), Paragraph(str(date_str), body_style)],
        [Paragraph("<b>Original File:</b>", body_style), Paragraph(str(orig_name), body_style),
         Paragraph("<b>Architecture:</b>", body_style), Paragraph("DenseNet121 (Robustness Fine-tuned)", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[1.1 * inch, 2.3 * inch, 1.1 * inch, 2.5 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))

    # Core Diagnostic Summary Table
    pred = record.get("prediction", "N/A")
    status = record.get("status", "N/A")
    pneumonia_prob = record.get("pneumonia_probability", 0.0)
    normal_prob = record.get("normal_probability", 0.0)
    conf = record.get("confidence", 0.0)
    uncertainty = record.get("uncertainty", 0.0)
    thresh = record.get("decision_threshold", 0.16)
    u_thresh = record.get("uncertainty_threshold", 0.10)
    temp = record.get("temperature", 1.0726)

    pred_color = "#dc2626" if pred == "PNEUMONIA" else "#16a34a"
    status_color = "#16a34a" if status == "ACCEPTED" else "#d97706"

    pred_p = Paragraph(f"<font color='{pred_color}'><b>{pred}</b></font>", ParagraphStyle("Pred", parent=body_style, fontSize=11))
    status_p = Paragraph(f"<font color='{status_color}'><b>{status}</b></font>", ParagraphStyle("Stat", parent=body_style, fontSize=10))

    results_data = [
        [Paragraph("<b>Prediction</b>", body_style), pred_p,
         Paragraph("<b>Analysis Status</b>", body_style), status_p],
        [Paragraph("<b>P(Pneumonia)</b>", body_style), Paragraph(f"{pneumonia_prob:.4f} (Threshold: {thresh})", body_style),
         Paragraph("<b>P(Normal)</b>", body_style), Paragraph(f"{normal_prob:.4f}", body_style)],
        [Paragraph("<b>Confidence</b>", body_style), Paragraph(f"{conf:.4f}", body_style),
         Paragraph("<b>Uncertainty</b>", body_style), Paragraph(f"{uncertainty:.4f} (Threshold: {u_thresh})", body_style)],
        [Paragraph("<b>Temperature (T)</b>", body_style), Paragraph(f"{temp:.4f} (Calibrated)", body_style),
         Paragraph("<b>Abstention Rule</b>", body_style), Paragraph("Uncertainty > 0.10 &rarr; Review", body_style)],
    ]

    results_table = Table(results_data, colWidths=[1.4 * inch, 2.1 * inch, 1.4 * inch, 2.1 * inch])
    results_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("EVALUATION & PREDICTION METRICS", section_heading))
    elements.append(results_table)
    elements.append(Spacer(1, 10))

    # Dual Images: Original vs Grad-CAM
    orig_path = record.get("original_image_path")
    gradcam_path = record.get("gradcam_image_path")

    image_cells = []
    if orig_path and os.path.exists(orig_path):
        try:
            image_cells.append(RLImage(orig_path, width=3.2 * inch, height=3.2 * inch))
        except Exception:
            image_cells.append(Paragraph("Original Image Preview Unavailable", body_style))
    else:
        image_cells.append(Paragraph("Original image not found", body_style))

    if gradcam_path and os.path.exists(gradcam_path):
        try:
            image_cells.append(RLImage(gradcam_path, width=3.2 * inch, height=3.2 * inch))
        except Exception:
            image_cells.append(Paragraph("Grad-CAM Preview Unavailable", body_style))
    else:
        image_cells.append(Paragraph("Grad-CAM overlay not found", body_style))

    img_table_data = [
        [Paragraph("<b>Original Chest X-Ray</b>", body_style), Paragraph("<b>Grad-CAM Interpretability Overlay (DenseBlock4)</b>", body_style)],
        image_cells
    ]
    img_table = Table(img_table_data, colWidths=[3.5 * inch, 3.5 * inch])
    img_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(Paragraph("VISUAL INTERPRETABILITY", section_heading))
    elements.append(img_table)
    elements.append(Spacer(1, 8))

    # Interpretability Explanation
    explain_text = (
        "<b>Interpretability Notice:</b> Grad-CAM (Gradient-weighted Class Activation Mapping) highlights image regions "
        "that contributed most prominently to the model's feature representations in DenseBlock4. It does not provide "
        "definitive clinical anatomical localization, does not prove disease pathology, and must never be interpreted as "
        "an autonomous diagnostic finding."
    )
    elements.append(Paragraph(explain_text, body_style))
    elements.append(Spacer(1, 8))

    # Prominent Disclaimer (Task 39)
    disclaimer_text = (
        "<b>MANDATORY RESEARCH DISCLAIMER:</b><br/>"
        "This application is a research prototype for educational and experimental purposes. It is not a medical "
        "diagnostic device and must not be used as a substitute for evaluation by a qualified healthcare professional."
    )
    elements.append(Paragraph(disclaimer_text, disclaimer_style))

    # Build PDF
    doc.build(elements)
    return output_path
