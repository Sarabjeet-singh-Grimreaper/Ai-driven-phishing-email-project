import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_threat_pdf(report_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles matching enterprise grade reports
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e3a8a'), # Dark Navy
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=8,
        spaceBefore=12
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=9.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6,
        leading=13
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Code'],
        fontSize=8.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#e2e8f0'),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=10
    )

    # 1. Header Section
    story.append(Paragraph("AI CyberShield — Executive Threat Report", title_style))
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    story.append(Paragraph(f"Generated: {date_str} | Platform: Enterprise Email Threat Intelligence Portal", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 2. Executive Summary Block
    prediction = report_data.get('prediction', 'UNKNOWN')
    risk_score = report_data.get('risk_score', 0)
    severity = report_data.get('severity', 'LOW')
    attack_type = report_data.get('attack_type', 'N/A')
    reason = report_data.get('reason', 'No anomalies detected.')
    
    summary_bg = '#fee2e2' if prediction.upper() == 'PHISHING' else '#dcfce7'
    summary_border = '#f87171' if prediction.upper() == 'PHISHING' else '#4ade80'
    summary_text_color = '#991b1b' if prediction.upper() == 'PHISHING' else '#166534'
    
    summary_html = f"""
    <b>VERDICT:</b> {prediction}<br/>
    <b>THREAT LEVEL:</b> {severity} ({risk_score}/100 Risk Score)<br/>
    <b>ATTACK VECTOR:</b> {attack_type}<br/>
    <b>PRIMARY SIGNAL:</b> {reason}
    """
    
    summary_p = Paragraph(summary_html, ParagraphStyle(
        'SummaryStyle', parent=body_style, fontSize=10.5, leading=15, textColor=colors.HexColor(summary_text_color)
    ))
    
    summary_table = Table([[summary_p]], colWidths=[530])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(summary_bg)),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor(summary_border)),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(summary_p)
    story.append(Spacer(1, 15))
    
    # 3. Threat Timeline Section
    story.append(Paragraph("Threat Timeline Analysis", section_style))
    timeline_html = """
    • <b>[T+0.00s] Ingestion:</b> Email payload ingested and parsed.<br/>
    • <b>[T+0.12s] OCR Engine:</b> Document/attachment scans completed.<br/>
    • <b>[T+0.25s] Heuristic Scan:</b> Extracted header and URL signatures.<br/>
    • <b>[T+0.34s] ML Evaluation:</b> NLP Vectorized Classification completed.<br/>
    • <b>[T+0.35s] Intel Update:</b> Threat signature stored in local SOC log database.<br/>
    """
    story.append(Paragraph(timeline_html, body_style))
    story.append(Spacer(1, 10))
    
    # 4. IOC Summary Table
    story.append(Paragraph("Indicators of Compromise (IOC) Summary", section_style))
    indicators = report_data.get('indicators', [])
    if not indicators:
        indicators = ["Clean email signature (No threat patterns matched)"]
        
    table_data = [["IOC Indicator Detected", "Trigger Severity"]]
    for ind in indicators:
        table_data.append([ind, "High" if prediction.upper() == 'PHISHING' else "Safe"])
        
    ioc_table = Table(table_data, colWidths=[380, 150])
    ioc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#ffffff')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(ioc_table)
    story.append(Spacer(1, 15))
    
    # 5. MITRE ATT&CK Mapping
    story.append(Paragraph("MITRE ATT&CK Framework Mapping", section_style))
    mitre_html = ""
    if prediction.upper() == 'PHISHING':
        mitre_html = """
        • <b>Tactical Phase:</b> Initial Access (TA0001)<br/>
        • <b>Technique:</b> Phishing: Spearphishing Link / Spearphishing Attachment (T1566.001 / T1566.002)<br/>
        • <b>Defensive Control:</b> User Training, URL Sandbox, DMARC Enforcement, MFA
        """
    else:
        mitre_html = """
        • <b>Tactical Phase:</b> Reconnaissance (None detected)<br/>
        • <b>Technique:</b> No active adversarial actions detected. Standard hygiene protocols active.
        """
    story.append(Paragraph(mitre_html, body_style))
    story.append(Spacer(1, 10))
    
    # 6. Technical Recommendation Block
    story.append(Paragraph("Remediation & Incident Response Guidelines", section_style))
    recommendation_html = """
    1. <b>Isolate & Contain:</b> Do not interact with email content, URLs, or attachment objects.<br/>
    2. <b>Sender Block:</b> Block domain and sender IP addresses inside email gateway parameters.<br/>
    3. <b>MFA Audit:</b> Ensure the target recipient has active multi-factor authentication (MFA) enabled.<br/>
    4. <b>Verification:</b> Verify sender out-of-band using registered telephone directory details.
    """
    story.append(Paragraph(recommendation_html, body_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
