import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # Omit header and footer on Title Page
        if self._pageNumber == 1:
            self.restoreState()
            return
            
        # Draw running header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D"))
        self.drawString(54, 550, "REDROB DATA & AI HACKATHON  |  SUBMISSION PRESENTATION")
        
        # Draw header separator rule
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(1)
        self.line(54, 542, 738, 542)
        
        # Draw running footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(54, 36, "Methodology: Rule-Based Semantic Matching & Behavioral Re-Ranking")
        
        # Draw page number
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(738, 36, page_text)
        
        self.restoreState()

def create_presentation(filename="presentation.pdf"):
    # Using Letter landscape for a slide-like format
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        rightMargin=54,
        leftMargin=54,
        topMargin=72,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=36,
        leading=42,
        textColor=colors.HexColor("#1A365D"),
        alignment=0, # Left-aligned
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#319795"),
        alignment=0,
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#718096"),
        alignment=0,
    )
    
    slide_title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=15,
    )
    
    h2_style = ParagraphStyle(
        'SlideH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#319795"),
        spaceBefore=10,
        spaceAfter=6,
    )
    
    body_style = ParagraphStyle(
        'SlideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#2D3748"),
    )
    
    bullet_style = ParagraphStyle(
        'SlideBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5,
    )
    
    story = []
    
    # ==================== SLIDE 1: COVER SLIDE ====================
    story.append(Spacer(1, 1.2 * inch))
    story.append(Paragraph("Redrob Recruiter Matcher AI", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Senior AI Engineer Search — Intelligent Ranking & Behavioral Re-Ranking", subtitle_style))
    story.append(Spacer(1, 30))
    
    # Decorative colored bar
    bar_data = [['']]
    bar_table = Table(bar_data, colWidths=[684], rowHeights=[4])
    bar_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#319795")),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(bar_table)
    story.append(Spacer(1, 1.5 * inch))
    
    meta_text = """
    <b>Team Name:</b> Response 200<br/>
    <b>Primary Contact:</b> Abhishek Vishwakarma<br/>
    <b>OS Platform:</b> Linux (Ubuntu 24.04 LTS)<br/>
    <b>Execution Mode:</b> 100% Offline, Zero APIs, Zero Network Calls
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(PageBreak())
    
    # ==================== SLIDE 2: CHALLENGE & GOALS ====================
    story.append(Paragraph("The Recruiting Dilemma: Beyond Keyword Matching", slide_title_style))
    story.append(Spacer(1, 10))
    
    p1 = """
    Traditional ATS keyword-matching filters fail to find the right candidates. Recruiters are either swamped with irrelevant keyword-stuffed resumes or miss top-tier candidates who don't list specific brand names.
    Our solution ranks candidates the way a human recruiter would: <i>assessing context, experience depth, and real-world availability.</i>
    """
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Core Design Principles:", h2_style))
    story.append(Paragraph("• <b>Rigorous Technical Gating:</b> Calculate actual years of AI/ML-specific experience rather than relying on profile-wide metrics.", bullet_style))
    story.append(Paragraph("• <b>Disqualification of Profile Honeypots:</b> Identify and immediately filter logical inconsistencies (e.g. 0-duration expert skills or impossible startup timelines).", bullet_style))
    story.append(Paragraph("• <b>Filtering Out Non-Product Gaps:</b> Reject candidates with experiences exclusively in mass consulting and IT-service firms.", bullet_style))
    story.append(Paragraph("• <b>Behavioral Modulation:</b> Use real-time availability metrics (notice period, response speed, activity, location) as a tie-breaker, not a replacement for talent.", bullet_style))
    
    story.append(PageBreak())
    
    # ==================== SLIDE 3: DATA ANALYSIS & HONEYPOTS ====================
    story.append(Paragraph("Unmasking profile traps and honeypots", slide_title_style))
    story.append(Spacer(1, 10))
    
    p2 = """
    Analyzing 100,000 candidates revealed intentional traps designed to trigger simple keyword matchers:
    """
    story.append(Paragraph(p2, body_style))
    story.append(Spacer(1, 10))
    
    # Create Table of Honeypot Rules
    table_data = [
        [
            Paragraph("<b>Traps Identified</b>", h2_style),
            Paragraph("<b>System Defense</b>", h2_style),
            Paragraph("<b>Impact</b>", h2_style)
        ],
        [
            Paragraph("<b>Rule 1: Expert Skill, 0 Duration</b><br/>Candidates claiming 'expert' or 'advanced' proficiency in AI tools but listing 0 months of experience.", body_style),
            Paragraph("Identified in 80 profiles.<br/>Immediate disqualification (Score set to 0.0).", body_style),
            Paragraph("Blocks keyword-stuffers.", body_style)
        ],
        [
            Paragraph("<b>Rule 2: Impossible Foundings</b><br/>Candidates claiming employment at startups (Krutrim, Sarvam AI) before those companies were founded (pre-2023).", body_style),
            Paragraph("Identified in 14 profiles.<br/>Immediate disqualification (Score set to 0.0).", body_style),
            Paragraph("Blocks fraudulent histories.", body_style)
        ],
        [
            Paragraph("<b>Rule 3: Consulting Only</b><br/>Candidates whose entire work history is at services firms (TCS, Infosys, Wipro, etc.).", body_style),
            Paragraph("Checks entire career history.<br/>Immediate disqualification (Score set to 0.0).", body_style),
            Paragraph("Ensures product-native engineering talent.", body_style)
        ]
    ]
    
    t = Table(table_data, colWidths=[240, 240, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    
    story.append(PageBreak())
    
    # ==================== SLIDE 4: SCORING ARCHITECTURE ====================
    story.append(Paragraph("Scoring & Re-Ranking Architecture", slide_title_style))
    story.append(Spacer(1, 5))
    
    p3 = """
    Our ranking algorithm computes a candidate's final score by multiplying the <b>Technical Profile Fit</b> with the <b>Behavioral Availability Modifier</b>.
    """
    story.append(Paragraph(p3, body_style))
    story.append(Spacer(1, 10))
    
    # Table of Scoring Weights
    table_data_2 = [
        [
            Paragraph("<b>Technical Fit Component (Weight)</b>", h2_style),
            Paragraph("<b>Description / Formula</b>", h2_style),
            Paragraph("<b>Behavioral Modifier (Range)</b>", h2_style),
            Paragraph("<b>Description / Logic</b>", h2_style)
        ],
        [
            Paragraph("<b>ML Experience Duration (25%)</b>", body_style),
            Paragraph("Months in roles matching ML keywords or description terms. Prefers 3+ years.", body_style),
            Paragraph("<b>Recency & Activity</b>", body_style),
            Paragraph("Bonus for active, penalty for inactivity > 6 months (0.4x).", body_style)
        ],
        [
            Paragraph("<b>Current Title Fit (20%)</b>", body_style),
            Paragraph("1.0 for ML/AI engineers; 0.9 for Data Scientists; 0.8 for Backend w/ ML; 0.0 for non-tech.", body_style),
            Paragraph("<b>Notice Period</b>", body_style),
            Paragraph("Bonus for <=30 days, penalty for >90 days (0.5x).", body_style)
        ],
        [
            Paragraph("<b>Core Skills Alignment (20%)</b>", body_style),
            Paragraph("Core skills (Embeddings, RAG, LoRA, Search) scaled by proficiency & log-scaled duration.", body_style),
            Paragraph("<b>Location/Relocation</b>", body_style),
            Paragraph("Bonus for NCR/Pune; penalty if non-local and not willing to relocate (0.5x).", body_style)
        ],
        [
            Paragraph("<b>Experience Years (15%)</b>", body_style),
            Paragraph("Flat 1.0 for 5-9 years; drops linearly for junior and senior outliers.", body_style),
            Paragraph("<b>Recruiter Response</b>", body_style),
            Paragraph("Bonus for fast, responsive candidates; penalty for response rate < 20% (0.7x).", body_style)
        ],
        [
            Paragraph("<b>Product Fit / Keywords (20%)</b>", body_style),
            Paragraph("Ratio of months at product firms (10%) + occurrence of search/vector terms in job history (10%).", body_style),
            Paragraph("<b>GitHub Activity</b>", body_style),
            Paragraph("Small bonus (+3%) for active GitHub contributors.", body_style)
        ]
    ]
    
    t2 = Table(table_data_2, colWidths=[170, 172, 170, 172])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    
    story.append(PageBreak())
    
    # ==================== SLIDE 5: VALIDATION & PERFORMANCE ====================
    story.append(Paragraph("Validation Results & High-Performance Specs", slide_title_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Output Quality and Schema Validation:", h2_style))
    story.append(Paragraph("• <b>Schema Compliant:</b> Generated CSV file <i>team_run.csv</i> conforms to the exact headers (candidate_id, rank, score, reasoning) required and passed the validator check.", bullet_style))
    story.append(Paragraph("• <b>No Formatting Artifacts:</b> All generated reasoning statements are clean, use natural phrasing, do not contain trailing double periods, and display proper spacing.", bullet_style))
    story.append(Paragraph("• <b>100% Genuine ML Shortlist:</b> The top-ranked candidates consist entirely of high-caliber NLP, AI, and Machine Learning engineers with years of product experience, successfully filtering out QA and frontend profiles.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Compute and Speed Performance:", h2_style))
    story.append(Paragraph("• <b>Fast Execution:</b> Scores and ranks 100,000 profiles in <b>under 13 seconds</b> (averaging 12.26s) on a single CPU core, utilizing vector/matrix logic in NumPy.", bullet_style))
    story.append(Paragraph("• <b>Minimal Memory Footprint:</b> Fits entirely within standard RAM using streaming file reading (JSONL), leaving 99% of resources free.", bullet_style))
    story.append(Paragraph("• <b>Air-Gapped Compliance:</b> Runs entirely offline, requiring zero network calls or external APIs, securing candidate privacy.", bullet_style))
    
    story.append(Spacer(1, 25))
    concl_data = [[
        Paragraph("<b>Conclusion:</b> Our rule-based system delivers a highly-focused, premium shortlist of vetted candidates. By coupling strict technical gating with behavioral modulation, it mirrors the selection quality of an elite recruiter.", body_style)
    ]]
    concl_table = Table(concl_data, colWidths=[684])
    concl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#319795")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(concl_table)
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Presentation successfully saved to {filename}")

if __name__ == "__main__":
    create_presentation()
