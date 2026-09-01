#!/usr/bin/env python3
"""generate_contracts.py — builds the two 2026 service agreement PDFs
(Babysitter Service Agreement and Family Service Agreement) for Elite
Traders Lounge, reflecting the corrected 2026/2027 National Minimum Wage,
the existing (unchanged) commission structure, Paystack split-payment
terms (replacing wallet/FNB language), identity-verification and
proof-of-address requirements, the reference/affidavit requirement, and
the cancellation-rights disclaimer.

Run: python3 generate_contracts.py
Outputs into ./assets/contracts/
"""
import pathlib
import urllib.request

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    HRFlowable, KeepTogether, ListFlowable, ListItem,
)

ROOT = pathlib.Path(__file__).parent
OUT_DIR = ROOT / "assets" / "contracts"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FONT_DIR = pathlib.Path("/tmp/fonts")
FONT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Brand colors (matches style.css)
# ---------------------------------------------------------------------------
INK = HexColor("#2a251d")
MUTED = HexColor("#6e6555")
PRIMARY = HexColor("#c85a3a")   # terracotta
SECONDARY = HexColor("#1f5c52")  # deep teal
FAINT_BG = HexColor("#faf6ef")
LINE = HexColor("#d9cfbe")

COMPANY_EMAIL = "lemo.masethe@elitetraders.co.za"
COMPANY_PHONE = "+27 81 427 0419"
COMPANY_ADDRESS = "4017 Alek Mampana Street, Extension 7, Kwa-Guqa, Mpumalanga, 1039"
COMPANY_REG = "K2017318876"
NMW_RATE = "R30.23"
NMW_EFFECTIVE = "1 March 2026"
NMW_PREV = "R28.79"
GAZETTE = "Government Gazette No. 54075, published 3 February 2026"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONTS = {
    "Body": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Regular.ttf",
    "Body-Bold": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Bold.ttf",
    "Body-Italic": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Italic.ttf",
    "Heading": "https://github.com/google/fonts/raw/main/ofl/worksans/static/WorkSans-SemiBold.ttf",
    "Heading-Bold": "https://github.com/google/fonts/raw/main/ofl/worksans/static/WorkSans-Bold.ttf",
}
for name, url in FONTS.items():
    fp = FONT_DIR / f"{name}.ttf"
    if not fp.exists():
        try:
            urllib.request.urlretrieve(url, fp)
        except Exception:
            pass
    if fp.exists() and fp.stat().st_size > 0:
        try:
            pdfmetrics.registerFont(TTFont(name, str(fp)))
        except Exception:
            pass

def font(name, fallback):
    return name if name in pdfmetrics.getRegisteredFontNames() else fallback

F_BODY = font("Body", "Helvetica")
F_BODY_B = font("Body-Bold", "Helvetica-Bold")
F_BODY_I = font("Body-Italic", "Helvetica-Oblique")
F_HEAD = font("Heading", "Helvetica-Bold")
F_HEAD_B = font("Heading-Bold", "Helvetica-Bold")

styles = getSampleStyleSheet()

def pstyle(name, **kw):
    base = dict(fontName=F_BODY, fontSize=9.5, leading=14, textColor=INK, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(name, **base)

S_TITLE = pstyle("Title2", fontName=F_HEAD_B, fontSize=22, leading=26, textColor=SECONDARY, spaceAfter=4)
S_SUB = pstyle("Sub", fontName=F_BODY, fontSize=11, leading=15, textColor=MUTED, spaceAfter=2)
S_META = pstyle("Meta", fontName=F_BODY, fontSize=8.5, leading=12, textColor=MUTED, spaceAfter=14)
S_H1 = pstyle("H1", fontName=F_HEAD_B, fontSize=13.5, leading=17, textColor=SECONDARY, spaceBefore=16, spaceAfter=6)
S_H2 = pstyle("H2", fontName=F_HEAD, fontSize=10.5, leading=14, textColor=PRIMARY, spaceBefore=10, spaceAfter=4)
S_BODY = pstyle("Body2")
S_BODY_B = pstyle("BodyB", fontName=F_BODY_B)
S_ITALIC = pstyle("Italic2", fontName=F_BODY_I, textColor=MUTED)
S_CALLOUT = pstyle("Callout", fontName=F_BODY, fontSize=9, leading=13, textColor=INK,
                    backColor=FAINT_BG, borderColor=LINE, borderWidth=0.75, borderPadding=8, spaceAfter=10)
S_LI = pstyle("LI", fontName=F_BODY, fontSize=9.5, leading=13.5, spaceAfter=3)
S_SIG = pstyle("Sig", fontName=F_BODY, fontSize=9, leading=16, spaceAfter=2)
S_FOOT = pstyle("Foot", fontName=F_BODY, fontSize=7.5, leading=10, textColor=MUTED)
S_TCELL = pstyle("TCell", fontName=F_BODY, fontSize=7.5, leading=9.5, spaceAfter=0)
S_TCELL_HD = pstyle("TCellHead", fontName=F_BODY_B, fontSize=7.5, leading=9.5, textColor=colors.white, spaceAfter=0)

def bullets(items, style=S_LI):
    return ListFlowable(
        [ListItem(Paragraph(t, style), leftIndent=4, spaceAfter=3) for t in items],
        bulletType="bullet", start="•", leftIndent=14, bulletFontSize=8, bulletColor=PRIMARY,
    )

def rate_table():
    headers = ["Level", "Experience", "Type", "Fixed rate", "Min.", "Family", "Sitter", "Total"]
    rows = [
        ["1", "Entry · 0–1 year", "Day", "R45/hr", "5 hrs", "10%", "10%", "20%"],
        ["2", "Standard · 1–3 yrs, references", "Day", "R55/hr", "5 hrs", "8%", "12%", "20%"],
        ["3", "Advanced · 3+ yrs, First Aid/CPR", "Day", "R65/hr", "4 hrs", "7.5%", "12.5%", "20%"],
        ["3", "Advanced · night rate", "Overnight", "R70/hr", "10 hrs", "10%", "10%", "20%"],
        ["4", "Specialist · overnight/special needs", "Overnight", "R85/hr", "10 hrs", "10%", "10%", "20%"],
        ["1–3", "Full-day flat rate (7 hrs)", "Full-day", "R315 – R450/day", "7 hrs", "Same as Day", "Same as Day", "20%"],
    ]
    data = [[Paragraph(h, S_TCELL_HD) for h in headers]]
    for row in rows:
        data.append([Paragraph(cell, S_TCELL) for cell in row])
    t = Table(data, colWidths=[30, 102, 50, 58, 34, 50, 50, 36], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FAINT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t

def commission_table():
    headers = ["Booking example", "Level", "Sitter fee", "+ Family commission", "= Family pays", "– Sitter commission", "Net to babysitter"]
    rows = [
        ["5-hr day @ R45/hr", "1 – Entry", "R225", "R22.50 (10%)", "R247.50", "R22.50 (10%)", "R202.50"],
        ["5-hr day @ R55/hr", "2 – Standard", "R275", "R22 (8%)", "R297", "R33 (12%)", "R242"],
        ["4-hr day @ R65/hr", "3 – Advanced", "R260", "R19.50 (7.5%)", "R279.50", "R32.50 (12.5%)", "R227.50"],
        ["10-hr overnight @ R70/hr", "3 – Night", "R700", "R70 (10%)", "R770", "R70 (10%)", "R630"],
        ["10-hr overnight @ R85/hr", "4 – Specialist", "R850", "R85 (10%)", "R935", "R85 (10%)", "R765"],
    ]
    data = [[Paragraph(h, S_TCELL_HD) for h in headers]]
    for row in rows:
        data.append([Paragraph(cell, S_TCELL) for cell in row])
    t = Table(data, colWidths=[80, 48, 42, 68, 55, 68, 60], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FAINT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t

def cancel_table(rows):
    data = [["Cancellation timing", "Babysitter compensation", "Family refund"]] + rows
    t = Table(data, colWidths=[130, 165, 127], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), F_BODY_B),
        ("FONTNAME", (0, 1), (-1, -1), F_BODY),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FAINT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def header_footer(party_label):
    def _fn(c, doc):
        c.saveState()
        c.setStrokeColor(LINE)
        c.setLineWidth(0.75)
        c.line(20 * mm, doc.pagesize[1] - 16 * mm, doc.pagesize[0] - 20 * mm, doc.pagesize[1] - 16 * mm)
        c.setFont(F_BODY, 7.5)
        c.setFillColor(MUTED)
        c.drawString(20 * mm, doc.pagesize[1] - 13 * mm, "Elite Traders Lounge (Pty) Ltd · Reg. " + COMPANY_REG)
        c.drawRightString(doc.pagesize[0] - 20 * mm, doc.pagesize[1] - 13 * mm, party_label + " · 2026 Edition")
        c.line(20 * mm, 14 * mm, doc.pagesize[0] - 20 * mm, 14 * mm)
        c.drawString(20 * mm, 9 * mm, COMPANY_EMAIL + "  ·  " + COMPANY_PHONE)
        c.drawRightString(doc.pagesize[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
        c.restoreState()
    return _fn


def cover(title, subtitle, party_note):
    story = []
    story.append(Spacer(1, 30))
    story.append(Paragraph("ELITE TRADERS LOUNGE", pstyle("Brand", fontName=F_HEAD_B, fontSize=13, textColor=PRIMARY, spaceAfter=2)))
    story.append(Paragraph("Babysitting Services · South Africa", pstyle("Brand2", fontName=F_BODY, fontSize=9.5, textColor=MUTED, spaceAfter=28)))
    story.append(Paragraph(title, S_TITLE))
    story.append(Paragraph(subtitle, S_SUB))
    story.append(Spacer(1, 4))
    story.append(Paragraph(party_note, S_META))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=14))
    return story


AFFIDAVIT_TEMPLATE = [
    ("h2", "Appendix A — Standard Reference Letter &amp; Affidavit Template"),
    ("body", "Every babysitter applicant must submit at least one completed reference declaration in this format. It protects the reference-giver (by recording exactly what they are confirming and to whom), the babysitter (by giving a clear, verifiable record of good standing), and the family and Elite Traders Lounge (by providing a traceable, contactable, and — where commissioned — sworn statement of character)."),
    ("callout",
        "<b>REFERENCE DECLARATION / AFFIDAVIT</b><br/><br/>"
        "I, <u>_________________________________</u> (full name of reference), "
        "holding South African ID / passport number <u>_______________________</u>, "
        "residing at <u>_______________________________________________</u>, "
        "declare as follows:<br/><br/>"
        "1. I have known <u>_________________________________</u> (the applicant) for a period of "
        "<u>__________</u> in the capacity of <u>_______________________</u> "
        "(e.g. previous employer, family friend, colleague, community leader).<br/>"
        "2. To the best of my knowledge, the applicant is of good character, trustworthy, and suitable "
        "to be placed in a position of care and trust with children.<br/>"
        "3. I am aware that this declaration is being provided to Elite Traders Lounge (Pty) Ltd "
        "(Reg. " + COMPANY_REG + ") and may be relied upon by Elite Traders Lounge and by any family "
        "engaging the applicant's babysitting services through the Elite Traders Lounge platform.<br/>"
        "4. I consent to being contacted, telephonically or in writing, by Elite Traders Lounge or by a "
        "prospective family, to confirm the contents of this declaration.<br/>"
        "5. I understand that the information provided above is true and correct, and that knowingly "
        "furnishing false information in this declaration may expose me to civil liability and, where "
        "made under oath below, to criminal liability for perjury.<br/><br/>"
        "<b>Reference contact details</b> — Phone: <u>_______________________</u> &nbsp; "
        "Email: <u>_______________________</u><br/><br/>"
        "Signed at <u>_______________</u> on this <u>____</u> day of <u>_______________</u> 20<u>__</u>.<br/><br/>"
        "Reference signature: <u>_______________________________</u><br/><br/>"
        "<b>Optional — Commissioner of Oaths (for formal affidavit status):</b><br/>"
        "I certify that the deponent has acknowledged that they know and understand the contents of this "
        "declaration, which was signed and sworn to before me, and that the regulations contained in "
        "Government Notice No. R1258 of 21 July 1972, as amended, have been complied with.<br/><br/>"
        "Commissioner of Oaths signature: <u>_______________________</u> &nbsp; Full name: <u>_______________________</u><br/>"
        "Designation / ex officio: <u>_______________________</u> &nbsp; Area: <u>_______________________</u> &nbsp; "
        "Date: <u>_______________________</u>"),
    ("body", "Elite Traders Lounge retains a signed copy of this declaration on the applicant's verification file and treats it as a supporting record alongside Smile ID identity verification. A reference given knowingly in bad faith, or later shown to be materially false, may result in the immediate suspension of the applicant's profile pending review."),
]


def identity_section(party):
    is_sitter = party == "sitter"
    items = [
        "<b>South African citizens and permanent residents</b> register using a valid South African ID number, verified through Smile ID.",
    ]
    if is_sitter:
        items += [
            "<b>Foreign nationals may register as independent freelance babysitters</b> using a valid passport, provided they also hold and can produce a valid South African work permit, visa, or other authorisation that permits them to lawfully render paid work in South Africa. This requirement exists so that Elite Traders Lounge and the families it serves do not knowingly facilitate a breach of the Immigration Act 13 of 2002.",
            "A passport-registered babysitter must upload their passport bio-data page and current work permit/visa during verification, and must notify Elite Traders Lounge immediately if that permit expires, is revoked, or is not renewed. A booking may not be accepted or continued using an expired or invalid work permit.",
        ]
    else:
        items += [
            "A family member who is not a South African citizen may register using a valid passport together with proof of lawful residence in South Africa (e.g. a valid visa or permanent residence permit). Because a Family is a client of the platform rather than a paid worker, no work permit is required for Family registration.",
        ]
    items += [
        "<b>Smile ID identity verification is mandatory for every " + ("Babysitter" if is_sitter else "Family member") + "</b> before a profile can be activated or before any booking can proceed. Verification uses facial recognition matched against the submitted ID/passport and typically completes within 5–10 minutes; a failed check can be resubmitted.",
        "<b>Proof of address is mandatory for every " + ("Babysitter" if is_sitter else "Family") + "</b>: a utility bill, bank statement, lease/rental agreement, or municipal account/letter, dated within the last three months and reflecting the applicant's name and residential address.",
    ]
    if is_sitter:
        items.append("<b>A minimum of one completed reference declaration (Appendix A)</b> is mandatory for every Babysitter applicant. Elite Traders Lounge may contact the listed reference directly to confirm its contents before activating the Babysitter's profile.")
    items.append("Elite Traders Lounge displays a <b>\u201cVerified Identity\u201d</b> badge on any profile that has passed Smile ID verification" + (", and a separate \u201cReference Verified\u201d badge once at least one reference has been confirmed" if is_sitter else "") + ". Families and Babysitters are encouraged to only transact with verified profiles.")
    return bullets(items)


def paystack_section(party):
    is_sitter = party == "sitter"
    items = [
        "Elite Traders Lounge does not hold, custody, or take responsibility for any Family or Babysitter funds at any point. All payments are processed through <b>Paystack</b>, a licensed South African payment service provider, using Paystack's Split Payment functionality.",
        "Every " + ("Babysitter" if is_sitter else "Family") + " must have an active Paystack account and must supply the associated Paystack account email address during registration, so Elite Traders Lounge can confirm the account exists before enabling split payments.",
        "Elite Traders Lounge's total commission is always 20% of the Babysitter's fee (per the rate bands in Appendix B), charged on <b>both sides</b> of every booking: the Family's total payment is the Babysitter's fixed fee <b>plus</b> a commission percentage, added as an extra charge; the Babysitter's payout is the same fixed fee <b>minus</b> a commission percentage, deducted before payout. The two percentages differ by Level and booking type but always add up to 20%. When the Family's total payment is made, Paystack's Split Payment infrastructure divides that single transaction automatically: the Babysitter's net amount (fee minus the Babysitter-side commission) is paid into the Babysitter's own linked Paystack account, and Elite Traders Lounge's combined commission share (the Family-side amount plus the Babysitter-side amount) is paid into Elite Traders Lounge's Paystack account, in the same transaction.",
        "No separate Elite Traders Lounge service or platform fee is charged in addition to the two commission amounts described above. Paystack's own standard transaction-processing fees (charged by Paystack, not by Elite Traders Lounge) may apply to a payment and are governed by Paystack's own published pricing, not by this Agreement.",
        "Because Paystack — not Elite Traders Lounge — holds and settles the funds, actual payout timing to a Babysitter's Paystack account follows Paystack's standard settlement schedule. Elite Traders Lounge is not liable for delays caused by Paystack, the Babysitter's or Family's bank, or incorrect Paystack account details supplied by either party.",
        "Cash payments or any payment arranged outside Paystack fall entirely outside this Agreement and outside Elite Traders Lounge's dispute-resolution, fraud-protection, and payment-guarantee processes.",
    ]
    return bullets(items)


def disclaimer_section():
    return bullets([
        "Elite Traders Lounge reserves the right, in its sole discretion, to <b>refuse, suspend, or terminate service</b> to any Family or Babysitter who breaches this Agreement, the Code of Conduct, provides false identity, address, reference, work-permit, or banking/Paystack information, or otherwise engages in conduct that Elite Traders Lounge reasonably considers unsafe, fraudulent, or damaging to the platform or to another user.",
        "This right may be exercised immediately and without prior notice where Elite Traders Lounge reasonably believes a child's safety, a user's safety, or the integrity of the platform is at risk, and with reasonable prior notice in all other cases.",
        "Refusal or termination of service under this clause does not, by itself, entitle the affected party to any refund or compensation beyond what is expressly provided for in the Cancellation Policy (Section 7) for bookings already confirmed at the time of suspension.",
        "A party who believes their profile was suspended or refused service in error may lodge an appeal via the Dispute Resolution process in Section 9.",
    ])


def general_terms():
    return bullets([
        "<b>Governing law:</b> This Agreement is governed by the laws of the Republic of South Africa.",
        "<b>Entire agreement:</b> This Agreement, together with the Terms &amp; Conditions published on the Elite Traders Lounge website, constitutes the entire agreement between the parties regarding its subject matter and supersedes all prior discussions or agreements.",
        "<b>Severability:</b> If any clause of this Agreement is found invalid or unenforceable, the remaining clauses continue in full force and effect.",
        "<b>No waiver:</b> A failure by either party to enforce any provision of this Agreement is not a waiver of that provision or of any other provision.",
        "<b>Assignment:</b> Neither party may assign or transfer their rights or obligations under this Agreement without the prior written consent of Elite Traders Lounge.",
        "<b>Notices:</b> Notices under this Agreement must be sent to the contact email or address recorded on the party's profile, or to Elite Traders Lounge at " + COMPANY_EMAIL + ".",
    ])


def esignature_section():
    return [
        Paragraph(
            "This Agreement may be accepted electronically. Clicking \u201cI Accept\u201d (or the equivalent checkbox) "
            "during registration or booking is recorded, together with the date, time, and account details of the "
            "accepting party, and constitutes a valid electronic signature under the Electronic Communications and "
            "Transactions Act 25 of 2002. Where a physical signature is preferred, the signature blocks below may be "
            "completed and returned to Elite Traders Lounge.",
            S_BODY,
        )
    ]


def signature_blocks(party_label):
    rows = [
        [Paragraph("<b>" + party_label + "</b>", S_SIG), Paragraph("<b>Elite Traders Lounge (Pty) Ltd</b>", S_SIG)],
        [Paragraph("Signature: _____________________________", S_SIG), Paragraph("Signature: _____________________________", S_SIG)],
        [Paragraph("Full name: _____________________________", S_SIG), Paragraph("Name: Lemogang Masethe", S_SIG)],
        [Paragraph("Date: _____________________________", S_SIG), Paragraph("Date: _____________________________", S_SIG)],
    ]
    t = Table(rows, colWidths=[255, 255])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6)]))
    return t


def build_babysitter_pdf():
    path = OUT_DIR / "elite-traders-lounge-babysitter-agreement-2026.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, title="Elite Traders Lounge — Babysitter Service Agreement (2026)",
                             author="Perplexity Computer", topMargin=22 * mm, bottomMargin=20 * mm,
                             leftMargin=20 * mm, rightMargin=20 * mm)
    story = []
    story += cover(
        "Babysitter Service Agreement",
        "2026 Edition · Independent Contractor Terms for Babysitters",
        "Between Elite Traders Lounge (Pty) Ltd (Reg. " + COMPANY_REG + ") (\u201cElite Traders Lounge\u201d) "
        "and the registering Babysitter (\u201cthe Babysitter\u201d). This Agreement replaces and updates the "
        "2025 edition of the Babysitter Service Agreement, correcting the National Minimum Wage figures below "
        "and introducing new verification and payment terms.",
    )

    story.append(Paragraph("1. Parties &amp; Nature of Relationship", S_H1))
    story.append(Paragraph(
        "The Babysitter engages with Elite Traders Lounge as an <b>independent contractor</b>, not as an employee "
        "of Elite Traders Lounge or of any Family. Elite Traders Lounge operates a booking and verification "
        "platform connecting Babysitters with Families; it is not the Babysitter's employer and does not direct "
        "the day-to-day performance of childcare services.", S_BODY))

    story.append(Paragraph("2. Registration &amp; Identity Verification", S_H1))
    story.append(identity_section("sitter"))

    story.append(Paragraph("3. Minimum Wage Compliance", S_H1))
    story.append(Paragraph(
        f"The Babysitter's agreed hourly rate must always fall within the correct Appendix B rate band for their "
        f"experience level, and must never be lower than the current National Minimum Wage — "
        f"<b>{NMW_RATE} per hour, effective {NMW_EFFECTIVE}</b> ({GAZETTE}, a 5.0% increase on the "
        f"{NMW_PREV}/hour 2025 rate), or the applicable rate at the time of service.", S_BODY))
    story.append(Paragraph(
        "If a rate is entered below the platform's minimum for that level, or below the legal minimum wage, "
        "that rate is void and the minimum compliant rate in Appendix B automatically applies. Elite Traders "
        "Lounge reviews and updates this figure whenever the Department of Employment and Labour publishes a "
        "new Government Gazette rate.", S_CALLOUT))

    story.append(Paragraph("4. Appendix B — Rate Bands &amp; Minimum Booking Hours", S_H1))
    story.append(rate_table())
    story.append(Spacer(1, 6))
    story.append(Paragraph("Every Level has one fixed rate — there is no negotiation. Elite Traders Lounge's total commission is always 20% of the Babysitter's fee; the split between the Family-side and Sitter-side percentages differs by Level but always adds up to 20%. Level 1 &amp; 2 day bookings require a minimum of 5 consecutive hours; Level 3 day bookings require a minimum of 4; overnight bookings require a minimum of 10 consecutive hours.", S_ITALIC))

    story.append(Paragraph("5. Commission Structure", S_H1))
    story.append(Paragraph("Elite Traders Lounge's total commission is always 20% of the Babysitter's fee (per Appendix B), charged on both sides of every booking: the Family's total payment is the Babysitter's fixed fee plus a commission percentage as an added charge, and the Babysitter has a commission percentage deducted from their fee before payout — the two percentages differ by Level but always total 20%. Worked examples, at each Level's minimum booking:", S_BODY))
    story.append(commission_table())

    story.append(Paragraph("6. Payments — Paystack Split Payments", S_H1))
    story.append(paystack_section("sitter"))

    story.append(PageBreak())

    story.append(Paragraph("7. Cancellation Policy", S_H1))
    story.append(Paragraph("<b>7.1 Family Cancellation (before service rendered)</b>", S_H2))
    story.append(cancel_table([
        ["\u2265 48 hours before booking", "R0 (no charge)", "100% refund via Paystack"],
        ["24–48 hours before booking", "50% of the agreed net amount", "50% refund via Paystack"],
        ["< 24 hours before booking", "75% of the agreed net amount", "25% refund via Paystack"],
        ["No-show (Family absent)", "100% of the agreed net amount", "R0 refund (full charge)"],
    ]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>7.2 Babysitter Cancellation (before service rendered)</b>", S_H2))
    story.append(cancel_table([
        ["\u2265 48 hours before booking", "R0 (no charge)", "100% refund via Paystack"],
        ["24–48 hours before booking", "25% net (forfeits 75%)", "75% refund via Paystack"],
        ["< 24 hours before booking", "50% net (forfeits 50%)", "50% refund via Paystack"],
        ["No-show (Babysitter absent)", "R0 (forfeits 100%)", "100% refund; profile suspended pending review"],
    ]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>7.3 After service commences:</b> if either party cancels after the Babysitter arrives, full payment "
        "is due for hours already worked (minimum 1 hour). If the Family requests early departure, payment is due "
        "for actual hours worked; no refund applies for early departure initiated by the Family.", S_BODY))

    story.append(Paragraph("8. Code of Conduct", S_H1))
    story.append(bullets([
        "Arrive on time, follow the Family's written care instructions, and never leave a child unsupervised.",
        "No smoking, alcohol, or unauthorised guests while on duty.",
        "Treat Families with respect — discriminatory, abusive, or unsafe behaviour is grounds for immediate suspension.",
        "Report any injury, incident, or safety concern to Elite Traders Lounge and, where relevant, emergency services, as soon as possible.",
        "Never share photos or personal information about a Family or child publicly without written consent.",
    ]))

    story.append(Paragraph("9. Dispute Resolution", S_H1))
    story.append(bullets([
        "Parties should first attempt to resolve any disagreement directly, within 24 hours of it arising.",
        "If unresolved, either party may submit a formal complaint to Elite Traders Lounge with the booking reference and supporting evidence (check-in/check-out timestamps, messages, photos).",
        "Elite Traders Lounge investigates within 5 business days and issues a written decision within 10 business days.",
        "Dual-party check-in/check-out timestamps recorded through the check-in tool are the primary evidence of worked hours in any dispute.",
        "Either party may escalate an unresolved dispute to independent arbitration or the CCMA/relevant regulator after the internal process concludes.",
    ]))

    story.append(Paragraph("10. Termination, Suspension &amp; Right to Refuse Service", S_H1))
    story.append(disclaimer_section())

    story.append(Paragraph("11. Data Protection (POPIA)", S_H1))
    story.append(bullets([
        "Elite Traders Lounge processes personal information (identity, contact, address, reference, and Paystack account details) strictly to verify identity, facilitate bookings, process payments, and maintain safety records, in line with the Protection of Personal Information Act.",
        "Identity verification data (Smile ID checks) and reference declarations are stored securely and are not shared with third parties beyond what is required for verification and legal compliance.",
        "Check-in/check-out timestamps and booking records are retained to resolve disputes and support labour-law compliance.",
        "The Babysitter may request access to, correction of, or deletion of their personal information (subject to legal retention requirements) by emailing " + COMPANY_EMAIL + ".",
    ]))

    story.append(Paragraph("12. Tax Obligations", S_H1))
    story.append(bullets([
        "The Babysitter engages as an independent contractor, not an employee of Elite Traders Lounge or of any Family.",
        "Net income received after commission is taxable under South African law and should be declared to SARS by the Babysitter.",
        "Elite Traders Lounge does not withhold PAYE and does not provide tax advice; the Babysitter should keep their own transaction records and consult a registered tax practitioner as needed.",
    ]))

    story.append(Paragraph("13. General Terms", S_H1))
    story.append(general_terms())

    story.append(Paragraph("14. Digital Signatures &amp; Electronic Acceptance", S_H1))
    story += esignature_section()

    story.append(Spacer(1, 20))
    story.append(signature_blocks("The Babysitter"))

    story.append(PageBreak())
    story += [Paragraph(t, S_BODY if k == "body" else (S_H1 if k == "h2" else S_CALLOUT)) for k, t in AFFIDAVIT_TEMPLATE]

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "This document is a plain-language service agreement template prepared for Elite Traders Lounge's "
        "platform operations. It is not a substitute for independent legal advice; Elite Traders Lounge is "
        "encouraged to have this Agreement reviewed by a qualified South African attorney before relying on it "
        "for enforcement purposes.", S_FOOT))

    doc.build(story, onFirstPage=header_footer("Babysitter Agreement"), onLaterPages=header_footer("Babysitter Agreement"))
    return path


def build_family_pdf():
    path = OUT_DIR / "elite-traders-lounge-family-agreement-2026.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4, title="Elite Traders Lounge — Family Service Agreement (2026)",
                             author="Perplexity Computer", topMargin=22 * mm, bottomMargin=20 * mm,
                             leftMargin=20 * mm, rightMargin=20 * mm)
    story = []
    story += cover(
        "Family Service Agreement",
        "2026 Edition · Terms for Parents &amp; Guardians Booking a Babysitter",
        "Between Elite Traders Lounge (Pty) Ltd (Reg. " + COMPANY_REG + ") (\u201cElite Traders Lounge\u201d) "
        "and the registering parent or guardian (\u201cthe Family\u201d). This Agreement replaces and updates the "
        "2025 edition, correcting the National Minimum Wage figures below and introducing new verification and "
        "payment terms.",
    )

    story.append(Paragraph("1. Parties &amp; Nature of the Platform", S_H1))
    story.append(Paragraph(
        "Elite Traders Lounge operates a booking and verification platform connecting Families with independent, "
        "Smile ID-verified Babysitters. Elite Traders Lounge is not the Babysitter's employer and the Babysitter "
        "does not become an employee of the Family; the Babysitter provides services as an independent contractor.", S_BODY))

    story.append(Paragraph("2. Registration &amp; Identity Verification", S_H1))
    story.append(identity_section("family"))

    story.append(Paragraph("3. Minimum Wage &amp; Rate Acknowledgement", S_H1))
    story.append(Paragraph(
        f"Every booking must pay the Babysitter at or above the current National Minimum Wage — "
        f"<b>{NMW_RATE} per hour, effective {NMW_EFFECTIVE}</b> ({GAZETTE}) — and within the correct Appendix B "
        f"rate band for the Babysitter's experience level. A rate entered below the applicable minimum is void "
        f"and automatically corrected by the booking system to the compliant minimum shown in Appendix B.", S_BODY))
    story.append(Paragraph(
        "The Family agrees not to negotiate a Babysitter's rate below the legal minimum wage or the applicable "
        "Appendix B band floor, and acknowledges that Elite Traders Lounge's booking system enforces this "
        "automatically.", S_CALLOUT))

    story.append(Paragraph("4. Appendix B — Rate Bands &amp; Minimum Booking Hours", S_H1))
    story.append(rate_table())
    story.append(Spacer(1, 6))
    story.append(Paragraph("Every Level has one fixed rate — there is no negotiation. Level 1 &amp; 2 day bookings require a minimum of 5 consecutive hours; Level 3 day bookings require a minimum of 4; overnight bookings require a minimum of 10 consecutive hours.", S_ITALIC))

    story.append(Paragraph("5. Commission Structure", S_H1))
    story.append(Paragraph("Elite Traders Lounge's total commission is always 20% of the Babysitter's fee (per Appendix B), charged on both sides of every booking: the Family's total payment is the Babysitter's fixed fee plus a commission percentage as an added charge, and the Babysitter has a commission percentage deducted from their fee before payout — the two percentages differ by Level but always total 20%. Worked examples, at each Level's minimum booking:", S_BODY))
    story.append(commission_table())

    story.append(Paragraph("6. Payments — Paystack Split Payments", S_H1))
    story.append(paystack_section("family"))

    story.append(PageBreak())

    story.append(Paragraph("7. Cancellation Policy", S_H1))
    story.append(Paragraph("<b>7.1 Family Cancellation (before service rendered)</b>", S_H2))
    story.append(cancel_table([
        ["\u2265 48 hours before booking", "R0 (no charge)", "100% refund via Paystack"],
        ["24–48 hours before booking", "50% of the agreed net amount", "50% refund via Paystack"],
        ["< 24 hours before booking", "75% of the agreed net amount", "25% refund via Paystack"],
        ["No-show (Family absent)", "100% of the agreed net amount", "R0 refund (full charge)"],
    ]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>7.2 Babysitter Cancellation (before service rendered)</b>", S_H2))
    story.append(cancel_table([
        ["\u2265 48 hours before booking", "R0 (no charge)", "100% refund via Paystack"],
        ["24–48 hours before booking", "25% net (forfeits 75%)", "75% refund via Paystack"],
        ["< 24 hours before booking", "50% net (forfeits 50%)", "50% refund via Paystack"],
        ["No-show (Babysitter absent)", "R0 (forfeits 100%)", "100% refund; profile suspended pending review"],
    ]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>7.3 After service commences:</b> if either party cancels after the Babysitter arrives, full payment "
        "is due for hours already worked (minimum 1 hour). If the Family requests early departure, payment is due "
        "for actual hours worked; no refund applies for early departure initiated by the Family.", S_BODY))

    story.append(Paragraph("8. Family Responsibilities &amp; Code of Conduct", S_H1))
    story.append(bullets([
        "Provide clear, written care instructions (feeding, naps, medication, emergency contacts, house rules) before the booking begins.",
        "Ensure the home environment is safe for the Babysitter and the children in their care.",
        "Treat the Babysitter with respect — discriminatory, abusive, or unsafe behaviour is grounds for immediate suspension of the Family's account.",
        "Report any injury, incident, or safety concern to Elite Traders Lounge and, where relevant, emergency services, as soon as possible.",
        "Confirm arrival and departure via the check-in tool — this protects both the Babysitter's pay and the Family's booking.",
    ]))

    story.append(Paragraph("9. Dispute Resolution", S_H1))
    story.append(bullets([
        "Parties should first attempt to resolve any disagreement directly, within 24 hours of it arising.",
        "If unresolved, either party may submit a formal complaint to Elite Traders Lounge with the booking reference and supporting evidence.",
        "Elite Traders Lounge investigates within 5 business days and issues a written decision within 10 business days.",
        "Dual-party check-in/check-out timestamps recorded through the check-in tool are the primary evidence of worked hours in any dispute.",
        "Either party may escalate an unresolved dispute to independent arbitration or the relevant regulator after the internal process concludes.",
    ]))

    story.append(Paragraph("10. Termination, Suspension &amp; Right to Refuse Service", S_H1))
    story.append(disclaimer_section())

    story.append(Paragraph("11. Data Protection (POPIA)", S_H1))
    story.append(bullets([
        "Elite Traders Lounge processes personal information (identity, contact, address, and Paystack account details) strictly to verify identity, facilitate bookings, process payments, and maintain safety records, in line with the Protection of Personal Information Act.",
        "Identity verification data (Smile ID checks) is stored securely and is not shared with third parties beyond what is required for verification and legal compliance.",
        "Check-in/check-out timestamps and booking records are retained to resolve disputes and support labour-law compliance.",
        "The Family may request access to, correction of, or deletion of their personal information (subject to legal retention requirements) by emailing " + COMPANY_EMAIL + ".",
    ]))

    story.append(Paragraph("12. General Terms", S_H1))
    story.append(general_terms())

    story.append(Paragraph("13. Digital Signatures &amp; Electronic Acceptance", S_H1))
    story += esignature_section()

    story.append(Spacer(1, 20))
    story.append(signature_blocks("The Family"))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "This document is a plain-language service agreement template prepared for Elite Traders Lounge's "
        "platform operations. It is not a substitute for independent legal advice; Elite Traders Lounge is "
        "encouraged to have this Agreement reviewed by a qualified South African attorney before relying on it "
        "for enforcement purposes.", S_FOOT))

    doc.build(story, onFirstPage=header_footer("Family Agreement"), onLaterPages=header_footer("Family Agreement"))
    return path


if __name__ == "__main__":
    p1 = build_babysitter_pdf()
    p2 = build_family_pdf()
    print("Wrote:", p1)
    print("Wrote:", p2)
