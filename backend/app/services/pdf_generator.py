import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_threat_pdf(report_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00f2fe'), # Cyan style matching our dark theme
        spaceAfter=15
    )
    
    normal_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4facfe'),
        spaceAfter=10
    )
    
    story.append(Paragraph("AI CyberShield Phishing Threat Intelligence Report", title_style))
    story.append(Spacer(1, 12))
    
    # Add metadata info
    meta_text = f"<b>Scan Outcome:</b> {report_data.get('prediction', 'Unknown')}<br/>" \
                f"<b>Threat Risk Score:</b> {report_data.get('risk_score', 0)} / 100 ({report_data.get('severity', 'Low')})<br/>" \
                f"<b>Neural Engine Confidence:</b> {report_data.get('confidence', 0)}%<br/>" \
                f"<b>Targeted Attack Vector:</b> {report_data.get('attack_type', 'N/A')}<br/>" \
                f"<b>Classification Model:</b> {report_data.get('model', 'Random Forest')}"
    
    story.append(Paragraph(meta_text, normal_style))
    story.append(Spacer(1, 15))
    
    # Threat Indicators Table
    story.append(Paragraph("Identified Phishing Threat Indicators", header_style))
    indicators_list = report_data.get("indicators", [])
    if not indicators_list:
        indicators_list = ["No threat signatures identified"]
        
    table_data = [["Detected Threat Signatures / Indicators"]]
    for indicator in indicators_list:
        table_data.append([indicator])
        
    t = Table(table_data, colWidths=[400])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("Defense and Mitigation Recommendations", header_style))
    rec_text = "1. DO NOT interact with any links, attachments, or requests inside the scanned email.<br/>" \
               "2. Verify the sender out-of-band (e.g., text, call, Slack) if the request involves financials or credentials.<br/>" \
               "3. Flag and report this sender's address to your enterprise IT SOC team."
    story.append(Paragraph(rec_text, normal_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
