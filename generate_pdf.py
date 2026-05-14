from fpdf import FPDF
import re

PRIMARY = (0, 79, 144)
BLACK   = (25, 25, 25)
GRAY    = (100, 100, 100)

class ResumePDF(FPDF):
    def header(self): pass
    def footer(self): pass

pdf = ResumePDF(format="Letter")
pdf.add_page()
pdf.set_margins(16, 8, 16)
pdf.set_auto_page_break(auto=True, margin=8)

W  = pdf.w - 32
LH = 4.8

def write_bold(text, size=9, lh=LH):
    """
    Inline bold writer with MANUAL word-wrap control.
    Measures every word in the correct font BEFORE writing it,
    then decides wrap vs continue — prevents mid-word breaks from
    fpdf2 font-switch metric drift.
    """
    right = pdf.w - pdf.r_margin

    # Tokenise into (token, is_bold) pairs, splitting at whitespace
    tokens = []
    for part in re.split(r'(\*\*.*?\*\*)', text):
        if not part:
            continue
        bold = part.startswith('**') and part.endswith('**')
        content = part[2:-2] if bold else part
        for tok in re.split(r'(\s+)', content):
            if tok:
                tokens.append((tok, bold))

    old_c_margin = pdf.c_margin
    pdf.c_margin = 0  # no cell padding so cell width == text width exactly

    for tok, bold in tokens:
        pdf.set_font("Helvetica", "B" if bold else "", size)
        w = pdf.get_string_width(tok)
        is_space = not tok.strip()

        if is_space:
            if pdf.get_x() > pdf.l_margin:
                pdf.set_x(pdf.get_x() + w)
        else:
            if pdf.get_x() + w > right:
                if pdf.get_x() > pdf.l_margin:
                    pdf.ln(lh)
                    pdf.set_x(pdf.l_margin)
            # cell() never breaks mid-word regardless of metric drift
            pdf.cell(w, lh, tok)

    pdf.c_margin = old_c_margin
    pdf.set_font("Helvetica", "", size)   # always restore to normal

def bullet(text):
    orig  = pdf.l_margin
    indent, bw = 3, 5
    pdf.set_left_margin(orig + indent + bw)
    pdf.set_x(orig + indent)
    pdf.set_font("Helvetica", "", 9)
    pdf.write(LH, "-  ")
    write_bold(text, 9, LH)
    pdf.ln(LH + 0.6)
    pdf.set_left_margin(orig)
    pdf.set_x(orig)

def section(title):
    pdf.ln(1.5)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(*PRIMARY)
    pdf.set_x(pdf.l_margin)
    pdf.cell(W, 5.5, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*PRIMARY)
    pdf.set_line_width(0.35)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + W, pdf.get_y())
    pdf.ln(2.2)
    pdf.set_text_color(*BLACK)

def contact_line(items):
    SEP = "   |   "
    pdf.set_font("Helvetica", "", 8)
    total_w = sum(pdf.get_string_width(lbl + val) for lbl, val, _ in items)
    total_w += pdf.get_string_width(SEP) * (len(items) - 1)
    pdf.set_x(pdf.l_margin + max(0, (W - total_w) / 2))
    for i, (label, value, url) in enumerate(items):
        if i > 0:
            pdf.set_text_color(*GRAY)
            pdf.write(LH, SEP)
        if label:
            pdf.set_text_color(*BLACK)
            pdf.write(LH, label)
        pdf.set_text_color(*PRIMARY)
        pdf.write(LH, value, link=url or "")
    pdf.ln(LH + 1)

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
pdf.set_font("Helvetica", "B", 21)
pdf.set_text_color(*BLACK)
pdf.cell(W, 9, "Deepak Kumar Joshi", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(1)

contact_line([
    ("",        "Hyderabad, India",          None),
    ("Email: ", "dpkjoshi656.dj@gmail.com",  "mailto:dpkjoshi656.dj@gmail.com"),
    ("Phone: ", "+91 9039650540",             "tel:+919039650540"),
])
contact_line([
    ("LinkedIn: ",  "joshi-deepak-kumar",        "https://www.linkedin.com/in/joshi-deepak-kumar/"),
    ("GitHub: ",    "deepakjoshi-dj",             "https://github.com/deepakjoshi-dj"),
    ("Portfolio: ", "deepakjoshi-dj.github.io",   "https://deepakjoshi-dj.github.io"),
])
pdf.ln(1)
pdf.set_text_color(*BLACK)

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
section("Summary")
pdf.set_font("Helvetica", "", 9)
pdf.set_x(pdf.l_margin)
pdf.write(LH,
    "Full Stack Developer with 3+ years of experience building scalable SaaS and AI-powered "
    "web applications using React, Next.js, Node.js, Express, PostgreSQL, and Hasura. "
    "Experienced in owning end-to-end feature development, system design participation, API "
    "architecture, authentication systems, cloud deployments, and observability using Datadog, "
    "AWS, and GCP. Hands-on experience building AI-integrated products, healthcare "
    "interoperability (FHIR), and production-grade monitoring systems."
)
pdf.ln(LH)

# ════════════════════════════════════════════════════════════════════════════
# SKILLS
# ════════════════════════════════════════════════════════════════════════════
section("Skills")
skills = [
    ("Frontend",                   "React.js, Next.js, TypeScript, JavaScript (ES6+), Redux Toolkit, Tailwind CSS, HTML5, CSS3"),
    ("Backend",                    "Node.js, Express.js, REST APIs, Hasura, JWT Authentication, Socket.io"),
    ("Databases",                  "PostgreSQL, MongoDB"),
    ("Cloud & Infrastructure",     "AWS (EC2, SES), GCP (Cloud Run, Cloud Functions/Triggers), Nginx"),
    ("Observability & Monitoring", "Datadog (RUM, Logs, Dashboards), GCP Logging, Performance Monitoring"),
    ("AI Developer Tooling",       "Claude Code, MCP, GPT-assisted debugging & development workflows"),
    ("Version Control / Workflow", "Git, GitHub, Bitbucket, Agile/Scrum"),
]
for label, value in skills:
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*BLACK)
    pdf.write(LH, label + ": ")
    pdf.set_font("Helvetica", "", 9)
    pdf.write(LH, value)
    pdf.ln(LH + 0.5)

# ════════════════════════════════════════════════════════════════════════════
# EXPERIENCE
# ════════════════════════════════════════════════════════════════════════════
section("Experience")
pdf.set_x(pdf.l_margin)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(*BLACK)
pdf.write(LH, "Full Stack Developer")
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(*GRAY)
pdf.write(LH, "  -  ")
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(*PRIMARY)
pdf.write(LH, "Thinkhat")
pdf.ln(LH + 0.3)

pdf.set_x(pdf.l_margin)
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*GRAY)
pdf.write(LH, "February 2023 - Present  |  Hyderabad, Telangana")
pdf.ln(LH + 1.2)
pdf.set_text_color(*BLACK)

for b in [
    "Designed and delivered end-to-end product features for the **SOCRATIC AI platform** using **React**, **Node.js**, **Hasura**, and **Redux**.",
    "Built a **user feedback and analytics system** to capture response quality insights, enabling data-informed improvements to AI product behavior.",
    "Achieved **99% application uptime** and reduced mean time to resolution by **40%** through proactive monitoring using **Datadog RUM, logs, and dashboards**.",
    "Integrated **FHIR-compliant APIs** and frontend workflows to support healthcare interoperability requirements.",
    "Built and optimized **responsive dashboard interfaces** for content management and operational workflows across devices.",
    "Implemented **JWT-based authentication and authorization** across frontend routes and backend APIs for secure access control.",
    "Collaborated in feature architecture discussions focused on scalability and maintainability.",
]:
    bullet(b)

# ════════════════════════════════════════════════════════════════════════════
# PERSONAL PROJECT
# ════════════════════════════════════════════════════════════════════════════
section("Personal Project")
pdf.set_x(pdf.l_margin)
pdf.set_font("Helvetica", "BI", 10)
pdf.set_text_color(*BLACK)
pdf.write(LH, "Codrly")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*GRAY)
pdf.write(LH, "  |  ")
pdf.set_text_color(*PRIMARY)
pdf.write(LH, "github.com/deepakjoshi-dj/Codrly",
          link="https://github.com/deepakjoshi-dj/Codrly")
pdf.ln(LH + 1.2)
pdf.set_text_color(*BLACK)

for b in [
    "Built a full-stack developer networking platform using **React**, **Node.js**, **Express**, and **MongoDB** with authentication and real-time communication features.",
    "Implemented **Socket.io-based real-time chat** with reconnection handling and message persistence for reliable communication.",
    "Deployed backend services on **AWS EC2**, configured **Nginx** as a reverse proxy, and integrated **Amazon SES** for transactional email delivery.",
]:
    bullet(b)

# ════════════════════════════════════════════════════════════════════════════
# EDUCATION
# ════════════════════════════════════════════════════════════════════════════
section("Education")

C1 = W * 0.70
C2 = W * 0.30

def edu(degree, school, period, cgpa):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(*BLACK)
    pdf.cell(C1, LH, school, new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(C2, LH, period, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*BLACK)
    pdf.cell(C1, LH, degree, new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*PRIMARY)
    pdf.cell(C2, LH, "CGPA: " + cgpa, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

edu("Master of Computer Applications (MCA)",
    "Chandigarh University", "Jul 2024 - 2026", "8.90")
edu("Bachelor of Vocation (B.Voc) in Software Development",
    "Indira Gandhi National Tribal University", "Jul 2017 - Jun 2020", "7.50")

pdf.output("/Users/deepakjoshi/Projects/Resume/Deepak_Kumar_Joshi_Full_Stack_Developer.pdf")
print(f"Pages: {pdf.page}  |  Done.")
