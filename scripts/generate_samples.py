"""
Generate synthetic legal-style PDF documents for assessment demonstration.
Creates 3 samples: clean, noisy (low-text), and mixed.
Run from repo root: python scripts/generate_samples.py
"""
from __future__ import annotations

from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib import colors
except ImportError:
    print("Installing reportlab...")
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib import colors

OUT_DIR = Path("data/sample_inputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", parent=styles["Heading1"], alignment=TA_CENTER, spaceAfter=12, fontSize=16)
heading_style = ParagraphStyle("heading", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6, fontSize=13)
body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=16, spaceAfter=8)
small_style = ParagraphStyle("small", parent=styles["Normal"], fontSize=8, leading=12, textColor=colors.grey)


# ─── Document 1: CLEAN digital legal document ───────────────────────────────

def make_clean_pdf():
    doc = SimpleDocTemplate(str(OUT_DIR / "sample_clean.pdf"), pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    story = []
    story.append(Paragraph("IN THE HIGH COURT OF JUSTICE", title_style))
    story.append(Paragraph("COMMERCIAL DIVISION", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Case No. HC-2024-003812", body_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("<b>BETWEEN:</b>", body_style))
    story.append(Paragraph("MERIDIAN CAPITAL PARTNERS LLP &nbsp;&nbsp;&nbsp;&nbsp; <i>(Claimant)</i>", body_style))
    story.append(Paragraph("and", body_style))
    story.append(Paragraph("NOVA LOGISTICS INTERNATIONAL PLC &nbsp;&nbsp;&nbsp;&nbsp; <i>(Defendant)</i>", body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("PARTICULARS OF CLAIM", heading_style))
    story.append(Paragraph(
        "1. The Claimant, Meridian Capital Partners LLP, is a limited liability partnership registered in England "
        "and Wales under registration number OC412387, with its registered office at 14 Canary Wharf, London, E14 5AB.",
        body_style))
    story.append(Paragraph(
        "2. The Defendant, Nova Logistics International PLC, is a public limited company registered in England "
        "and Wales under registration number 08234561, with its registered office at Unit 7, Heathrow Business Park, "
        "Hounslow, TW6 2AA.",
        body_style))
    story.append(Paragraph(
        "3. By a written agreement dated 14 March 2023 (the 'Agreement'), the Defendant agreed to provide "
        "international freight forwarding and logistics services to the Claimant in respect of a consignment "
        "of commercial electronics destined for the UAE.",
        body_style))

    story.append(Paragraph("KEY DATES", heading_style))
    dates = [
        ("14 March 2023", "Logistics Agreement signed between parties."),
        ("2 April 2023", "Consignment dispatched from Heathrow (AWB No. 176-22938471)."),
        ("19 April 2023", "Delivery deadline per Agreement — consignment not delivered."),
        ("27 April 2023", "Claimant issued formal notice of breach to Defendant."),
        ("10 May 2023", "Defendant acknowledged delay; attributed to port congestion in Dubai."),
        ("15 June 2023", "Consignment partially delivered; 3 of 12 units missing."),
        ("3 August 2023", "Claimant issued letter before action."),
        ("1 September 2023", "Proceedings issued."),
    ]
    for date, event in dates:
        story.append(Paragraph(f"<b>{date}:</b> {event}", body_style))

    story.append(Paragraph("BASIS OF CLAIM", heading_style))
    story.append(Paragraph(
        "4. The Defendant is in breach of the Agreement by reason of its failure to deliver the full consignment "
        "by the agreed delivery date of 19 April 2023 and its failure to account for three missing units "
        "valued at £87,500 each.",
        body_style))
    story.append(Paragraph(
        "5. The Claimant has suffered loss and damage as a direct result of the Defendant's breach, "
        "including but not limited to: (a) the market value of the missing units (£262,500); "
        "(b) consequential losses arising from cancelled contracts with downstream buyers (£94,200); "
        "and (c) storage and insurance costs incurred during the period of delay (£12,800).",
        body_style))

    story.append(Paragraph("RELIEF SOUGHT", heading_style))
    story.append(Paragraph("The Claimant claims:", body_style))
    story.append(Paragraph("(a) Damages in the sum of £369,500;", body_style))
    story.append(Paragraph("(b) Interest pursuant to section 35A of the Senior Courts Act 1981;", body_style))
    story.append(Paragraph("(c) Costs of these proceedings;", body_style))
    story.append(Paragraph("(d) Such further relief as the Court considers appropriate.", body_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Signed: James R. Whitmore, Solicitor for the Claimant &nbsp;&nbsp; Date: 1 September 2023",
                            small_style))
    story.append(Paragraph("Pearson Specter Litt LLP, 100 Kings Road, London, EC2A 4BN | Tel: 020 7123 4567",
                            small_style))

    doc.build(story)
    print("[OK] Created: sample_clean.pdf")


# ─── Document 2: NOISY / LOW-TEXT simulated scanned page ────────────────────

def make_noisy_pdf():
    doc = SimpleDocTemplate(str(OUT_DIR / "sample_noisy.pdf"), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    # Simulate a scanned doc: minimal text, stamp marks, faded content
    story.append(Paragraph("AFFIDAVIT OF SERVICE", title_style))
    story.append(Spacer(1, 0.5*cm))
    # Sparse / partial text — simulates OCR fallback scenario
    story.append(Paragraph(
        "I, Sarah J. Okonkwo, process server, do solemnly and sincerely swear that on the 5th day of "
        "[UNCLEAR] 2023, I attended at the premises located at [PARTIALLY ILLEGIBLE] Road, London ...",
        body_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "... and did serve a true copy of the Claim Form and Particulars of Claim upon the Defendant "
        "Nova Logistics International PLC by leaving the same with a person who appeared to be [UNCLEAR] "
        "at said premises at approximately [UNCLEAR] hours.",
        body_style))
    story.append(Spacer(1, 2*cm))  # big gap = sparse page
    story.append(Paragraph("[STAMP: RECEIVED BY COURT — DATE ILLEGIBLE]", small_style))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph(
        "Sworn before me this ... day of ... 2023",
        body_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Signature: _______________________", body_style))
    story.append(Paragraph("Commissioner for Oaths", body_style))
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(
        "NOTE: This page was digitised from a physical file. Image quality was low. "
        "Some fields may be partially illegible. Cross-reference with original physical document.",
        small_style))

    doc.build(story)
    print("[OK] Created: sample_noisy.pdf")


# ─── Document 3: MIXED — multiple pages, some clean, some unclear ────────────

def make_mixed_pdf():
    doc = SimpleDocTemplate(str(OUT_DIR / "sample_mixed.pdf"), pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    story = []

    # Page 1: Clean structured section
    story.append(Paragraph("WITHOUT PREJUDICE SAVE AS TO COSTS", title_style))
    story.append(Paragraph("LETTER OF SETTLEMENT OFFER", heading_style))
    story.append(Paragraph("Ref: PSL/MCP/NLI/2023/0981 &nbsp;&nbsp; Date: 12 October 2023", body_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>TO:</b> Nova Logistics International PLC, Attention: General Counsel", body_style))
    story.append(Paragraph("<b>FROM:</b> Pearson Specter Litt LLP on behalf of Meridian Capital Partners LLP", body_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Our client Meridian Capital Partners LLP has instructed us to put forward the following settlement "
        "proposal in full and final resolution of the proceedings in Case No. HC-2024-003812.",
        body_style))
    story.append(Paragraph("TERMS OF OFFER", heading_style))
    story.append(Paragraph(
        "1. Payment by the Defendant to the Claimant of the sum of £280,000 (two hundred and eighty thousand "
        "pounds sterling) within 21 days of acceptance of this offer.",
        body_style))
    story.append(Paragraph(
        "2. The Defendant to provide a written undertaking that it will implement an improved cargo tracking "
        "and insurance protocol for all future shipments exceeding £50,000 in declared value.",
        body_style))
    story.append(Paragraph(
        "3. Each party to bear its own costs up to the date of settlement, save that the Defendant shall "
        "contribute £15,000 toward the Claimant's legal costs.",
        body_style))
    story.append(Paragraph(
        "This offer is open for acceptance until 17:00 (GMT) on 26 October 2023, after which it shall "
        "automatically lapse.",
        body_style))

    # Page 2: Partially unclear — simulate poor scan
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Paragraph("EXHIBIT A — INVOICE SUMMARY (SCANNED COPY)", heading_style))
    story.append(Paragraph(
        "Invoice No: [UNCLEAR] &nbsp;&nbsp; Vendor: [PARTIALLY ILLEGIBLE] Electronics Ltd",
        body_style))
    story.append(Paragraph(
        "Line items: 12 x Commercial Display Units @ £87,500 per unit = [UNCLEAR TOTAL]",
        body_style))
    story.append(Paragraph(
        "Shipping instruction ref: [UNCLEAR] &nbsp;&nbsp; Dispatch confirmed: [DATE UNCLEAR]",
        body_style))
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph(
        "Customs declaration: HS Code [UNCLEAR] — Commercial electronics, not for resale. "
        "Country of origin: [PARTIALLY ILLEGIBLE]. Declared value for customs: USD [UNCLEAR].",
        body_style))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("[REMAINDER OF PAGE ILLEGIBLE — PHYSICAL DAMAGE TO ORIGINAL DOCUMENT]", small_style))

    # Page 3: Clean again
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Paragraph("CHRONOLOGY OF COMMUNICATIONS", heading_style))
    comms = [
        ("14 Mar 2023", "Agreement executed. Both parties sign logistics contract."),
        ("28 Mar 2023", "Defendant confirms collection slot at Heathrow for 2 April."),
        ("2 Apr 2023", "Consignment collected by Defendant. AWB issued."),
        ("15 Apr 2023", "Claimant requests status update. Defendant advises 'in transit'."),
        ("20 Apr 2023", "Claimant emails Defendant re: missed delivery deadline."),
        ("27 Apr 2023", "Formal breach notice sent via solicitors."),
        ("10 May 2023", "Defendant responds: delay due to Dubai port congestion."),
        ("15 Jun 2023", "Partial delivery received. 3 units confirmed missing."),
        ("3 Aug 2023", "Letter before action sent."),
        ("1 Sep 2023", "Claim issued in High Court."),
        ("12 Oct 2023", "This settlement offer sent."),
    ]
    for date, event in comms:
        story.append(Paragraph(f"<b>{date}:</b> {event}", body_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Notable gaps: Insurance policy documentation not provided. Cargo manifest for missing 3 units "
        "not located in file. Witness statement from warehouse operative pending.",
        body_style))

    doc.build(story)
    print("[OK] Created: sample_mixed.pdf")


if __name__ == "__main__":
    make_clean_pdf()
    make_noisy_pdf()
    make_mixed_pdf()
    print("\n[OK] All 3 sample PDFs created in data/sample_inputs/")
