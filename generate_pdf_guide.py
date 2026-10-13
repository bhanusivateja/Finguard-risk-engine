"""
Script to generate a clean, professional, easy-to-read PDF guide:
'FinGuard_AI_Localhost_Development_Guide.pdf'
Explaining the localhost development in simple, clear points.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

OUTPUT_PDF = Path(r"c:\Users\bhanu\OneDrive\Desktop\PROJECT DETAILSS\FinGuard_AI_Localhost_Development_Guide.pdf")

def create_guide_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    NAVY = colors.HexColor("#0f172a")
    BLUE = colors.HexColor("#0284c7")
    DARK_TEXT = colors.HexColor("#1e293b")
    MUTED_TEXT = colors.HexColor("#475569")
    BG_CARD = colors.HexColor("#f8fafc")
    BORDER_COLOR = colors.HexColor("#cbd5e1")
    GREEN = colors.HexColor("#059669")
    AMBER = colors.HexColor("#d97706")
    RED = colors.HexColor("#dc2626")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=NAVY,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=BLUE,
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=DARK_TEXT,
        leftIndent=14,
        spaceAfter=3,
    )

    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=NAVY,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=DARK_TEXT,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=NAVY,
    )

    story = []

    # Title & Header
    story.append(Paragraph("FinGuard AI: Localhost Development Guide", title_style))
    story.append(
        Paragraph(
            "<b>Project:</b> Intelligent Banking Fraud Detection and Smart Transaction Protection System<br/>"
            "<b>Active Localhost URL:</b> <font color='#0284c7'><b>http://localhost:8501</b></font> &nbsp;|&nbsp; Final-Year B.Tech CSE (AI &amp; ML)",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=10))

    # SECTION 1: WHAT IS RUNNING ON LOCALHOST
    story.append(Paragraph("1. What Is Running on Your Localhost Right Now?", h1_style))
    story.append(
        Paragraph(
            "When you open <b>http://localhost:8501</b> in your web browser, you are running a complete, "
            "locally hosted AI-powered banking security system. Unlike simple UI mockups, this application is backed by "
            "an <b>actual trained machine learning pipeline</b>, a real SQLite database, and a live Dynamic Risk Engine.",
            body_style,
        )
    )

    url_table_data = [
        [
            Paragraph("<b>Component</b>", table_cell_bold),
            Paragraph("<b>Current Status</b>", table_cell_bold),
            Paragraph("<b>What It Does</b>", table_cell_bold),
        ],
        [
            Paragraph("<b>Web App (Frontend)</b>", table_cell_bold),
            Paragraph("<font color='#059669'><b>Active (Port 8501)</b></font>", table_cell_style),
            Paragraph("Streamlit web interface with interactive forms, Plotly gauges, and charts.", table_cell_style),
        ],
        [
            Paragraph("<b>ML Model (Backend)</b>", table_cell_bold),
            Paragraph("<font color='#059669'><b>Trained &amp; Loaded</b></font>", table_cell_style),
            Paragraph("Random Forest (95.4% accuracy) trained on the real IEEE-CIS Fraud dataset.", table_cell_style),
        ],
        [
            Paragraph("<b>Database</b>", table_cell_bold),
            Paragraph("<font color='#059669'><b>finguard.db (SQLite)</b></font>", table_cell_style),
            Paragraph("Saves every evaluated transaction, user profile, and audit trail locally.", table_cell_style),
        ],
    ]
    t1 = Table(url_table_data, colWidths=[1.5 * inch, 1.4 * inch, 4.3 * inch])
    t1.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t1)
    story.append(Spacer(1, 10))

    # SECTION 2: HOW THE SYSTEM WORKS IN 5 EASY STEPS
    story.append(Paragraph("2. How FinGuard AI Evaluates a Transaction (5 Easy Steps)", h1_style))
    steps = [
        "<b>Step 1: Input Received</b> — The system takes the transaction amount, customer profile, device status, IP network, and merchant category.",
        "<b>Step 2: ML Fraud Probability</b> — The trained IEEE-CIS model checks mathematical fraud signatures and outputs a probability score (0 to 100).",
        "<b>Step 3: Behavioral Analysis</b> — The engine checks if the amount is normal for this user (Z-Score), whether transaction frequency is too fast (1-hour velocity), and any failed PIN attempts.",
        "<b>Step 4: Contextual Gateway Risk</b> — It checks environmental flags: Is the user on Tor/VPN? Is the device unrecognized? Is the merchant high-risk (Crypto/Gambling)?",
        "<b>Step 5: Dynamic Risk Score & Decision</b> — All signals combine into a single 0–100 score: <b>ALLOW</b> (&lt;30), <b>VERIFY</b> (30–69), or <b>BLOCK</b> (&ge;70).",
    ]
    for s in steps:
        story.append(Paragraph(f"• {s}", bullet_style))
    story.append(Spacer(1, 10))

    # SECTION 3: PAGES TO DEMONSTRATE
    story.append(Paragraph("3. The 6 Interactive Pages You Can Click On", h1_style))
    pages_data = [
        [
            Paragraph("<b>Page Name</b>", table_cell_bold),
            Paragraph("<b>What to Show During Project Review / Viva</b>", table_cell_bold),
        ],
        [
            Paragraph("<b>1. Overview (app.py)</b>", table_cell_bold),
            Paragraph("Shows live system status, active architecture flow diagram, and system metrics.", table_cell_style),
        ],
        [
            Paragraph("<b>2. Dashboard</b>", table_cell_bold),
            Paragraph("Displays total transactions evaluated, fraud rate, risk distribution histogram, and decision donut chart.", table_cell_style),
        ],
        [
            Paragraph("<b>3. Transaction Analyzer</b>", table_cell_bold),
            Paragraph("<b>The star demo page!</b> Click the 6 preset buttons (Normal Coffee, Cold-Start User, Rapid Draining, Child Gaming) to see real-time score gauges and explanations.", table_cell_style),
        ],
        [
            Paragraph("<b>4. Fraud Monitoring</b>", table_cell_bold),
            Paragraph("A complete searchable audit ledger of all analyzed transactions with CSV export and forensic drill-down inspector.", table_cell_style),
        ],
        [
            Paragraph("<b>5. Model Performance</b>", table_cell_bold),
            Paragraph("Genuine academic metrics comparing Random Forest vs Gradient Boosting vs XGBoost, plus confusion matrix and top features.", table_cell_style),
        ],
        [
            Paragraph("<b>6. Federated Learning</b>", table_cell_bold),
            Paragraph("Shows simulated privacy-preserving collaboration between 3 banks (FedAvg algorithm) with zero customer data leakage.", table_cell_style),
        ],
    ]
    t2 = Table(pages_data, colWidths=[2.1 * inch, 5.1 * inch])
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t2)
    story.append(Spacer(1, 10))

    # SECTION 4: HOW TO START OR STOP THE APP ANYTIME
    story.append(Paragraph("4. How to Start and Stop the Application Anytime", h1_style))
    run_points = [
        "<b>To Open the App Right Now:</b> Just open your browser and go to: <b>http://localhost:8501</b>",
        "<b>To Start the App Tomorrow (One-Click):</b> Double-click the file named <b><code>run_app.bat</code></b> inside your project folder.",
        "<b>To Start via Terminal:</b> Open terminal in the project folder and type: <code>streamlit run app.py</code>",
        "<b>To Run the 11 Unit Tests:</b> Double-click <b><code>run_tests.bat</code></b> (all 11 tests pass with 100% OK).",
    ]
    for r in run_points:
        story.append(Paragraph(f"• {r}", bullet_style))
    story.append(Spacer(1, 10))

    # SECTION 5: SPECIAL INNOVATIONS TO HIGHLIGHT TO EXAMINERS
    story.append(Paragraph("5. Three Standout Features to Mention in Your Presentation", h1_style))
    features = [
        "<b>1. Cold-Start Account Handling:</b> When a new user has 0 historical transactions, FinGuard does not blindly block them or assign zero risk. It uses an adaptive contextual prior.",
        "<b>2. Child-Safe Spending Protection:</b> Detects accidental gaming/in-app purchases on parents' devices and requires parental biometric confirmation.",
        "<b>3. Explainable AI (XAI):</b> Every transaction gives clear human-readable bullet points explaining exactly why a transaction was allowed, challenged, or blocked.",
    ]
    for f in features:
        story.append(Paragraph(f"• {f}", bullet_style))

    doc.build(story)
    print(f"PDF successfully created at: {OUTPUT_PDF}")

if __name__ == "__main__":
    create_guide_pdf()
