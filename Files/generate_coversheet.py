import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document(r'c:\Users\Dell\Desktop\Cloud Projecct\d\CoverSheet.docx')

# =========================================
# TABLE 0 - Course Info
# =========================================
t0 = doc.tables[0]
r1 = t0.rows[1]
# Index: 0=Course, 1=Semester, 2=TeamID, 3=Time, 4=TA, 5=Grade
r1.cells[2].paragraphs[0].clear()
r1.cells[2].paragraphs[0].add_run('Team 10')
# Leave Time, TA, Grade blank (to be filled by supervisor)

# =========================================
# TABLE 1 - Project Identity & Snapshot
# =========================================
t1 = doc.tables[1]
left_cell = t1.rows[0].cells[0]
right_cell = t1.rows[0].cells[1]

# Clear left cell and fill with project identity
for p in left_cell.paragraphs:
    p.clear()

def add_bold_line(cell, text):
    p = cell.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    return p

def add_normal_line(cell, text):
    p = cell.add_paragraph(text)
    return p

# Rebuild left cell
left_cell.paragraphs[0].clear()
left_cell.paragraphs[0].add_run('Project Identity').bold = True

add_normal_line(left_cell, '')
add_bold_line(left_cell, 'Project Name:')
add_normal_line(left_cell, 'NextStep – AI-Powered Career & Recruitment Platform')
add_normal_line(left_cell, '')
add_bold_line(left_cell, 'Project Type:')
add_normal_line(left_cell, 'Mixed (AI + Cloud + Full-Stack Web Application)')
add_normal_line(left_cell, '')
add_bold_line(left_cell, 'Domain:')
add_normal_line(left_cell, 'Recruitment Technology (HRTech) / AI-NLP')
add_normal_line(left_cell, '')
add_bold_line(left_cell, 'Contacts / Links')
add_normal_line(left_cell, 'Live App:    http://13.53.39.78:8080')
add_normal_line(left_cell, 'Backend API: http://13.53.39.78/api')
add_normal_line(left_cell, 'AI Service:  http://13.53.39.78:8001')

# Clear right cell and fill with project snapshot
for p in right_cell.paragraphs:
    p.clear()

right_cell.paragraphs[0].add_run('Project Snapshot').bold = True

snapshot_text = (
    '\n'
    'NextStep is a full-stack, AI-powered recruitment platform deployed on AWS (EC2, S3, RDS).\n\n'
    'Candidates register, upload their PDF/DOCX resume, and a custom fine-tuned BERT NER model '
    '(token classification) automatically extracts their skills, education, and experience. '
    'The parsed data is saved to a MySQL database and displayed in a rich candidate profile.\n\n'
    'Recruiters log in to a separate dashboard, search the entire talent pool by skill or name, '
    'view full candidate profiles, download resumes via pre-signed S3 URLs, and manage hiring '
    'status through an interactive pipeline (Applied → Interview → Offer → Hired → Rejected).\n\n'
    'Stack: FastAPI (Python) · MySQL/SQLAlchemy · BERT (HuggingFace Transformers) · '
    'Docker & Docker Compose · AWS EC2 · AWS S3 · HTML/CSS/JS (Vanilla) · Nginx'
)
right_cell.add_paragraph(snapshot_text)

# =========================================
# TABLE 2 - Team Details
# =========================================
t2 = doc.tables[2]
team = [
    ('1', 'Beshoy Magdy Abdelsaid',  '2100123', 'AI Model Training & Evaluation'),
    ('2', 'Joseph Adel',             '2100456', 'Backend API (FastAPI) & Database'),
    ('3', '',                        '',        'Frontend (HTML/CSS/JS)'),
    ('4', '',                        '',        'Cloud Deployment (AWS EC2, S3)'),
    ('5', '',                        '',        'Docker & DevOps'),
    ('6', '',                        '',        ''),
    ('7', '',                        '',        ''),
    ('8', '',                        '',        ''),
]
# Skip header row (row 0)
for i, (num, name, sid, role) in enumerate(team):
    row = t2.rows[i + 1]
    row.cells[0].paragraphs[0].clear()
    row.cells[0].paragraphs[0].add_run(num)
    row.cells[1].paragraphs[0].clear()
    row.cells[1].paragraphs[0].add_run(name)
    row.cells[2].paragraphs[0].clear()
    row.cells[2].paragraphs[0].add_run(sid)
    row.cells[3].paragraphs[0].clear()
    row.cells[3].paragraphs[0].add_run(role)
    # Leave attendance checkboxes as-is

# =========================================
# TABLE 3 - General Project Evaluation
# Leave Score and Notes for supervisor to fill
# =========================================
t3 = doc.tables[3]
# Rows 1-6 are criteria rows. Row 7 is Total.
# We do NOT fill anything here - supervisor evaluates and fills scores.

# =========================================
# TABLE 4 - Cloud Computing Evaluation
# Only fill "Student Response" column (index 2)
# Score and Notes are for the supervisor to fill
# =========================================
t4 = doc.tables[4]
cloud_responses = [
    (1,
     'We use AWS EC2 (t2.micro) for our server. The backend (FastAPI) and AI service (BERT) run in Docker containers. '
     'We store resumes in AWS S3. We use MySQL for our database on the same EC2 server. '
     'The website is served by a Python HTTP server.'),

    (2,
     'AWS EC2 (Free Tier) runs our code. AWS S3 safely stores the PDF/DOCX resumes. '
     'MySQL stores user data like skills and experience. We connect to S3 using the Python boto3 library. '
     'Passwords and keys are hidden safely in a .env file.'),

    (3,
     'We use Docker to package our backend and AI services. '
     'A docker-compose.yml file lets us start everything with one command (sudo docker compose up). '
     'The Docker containers automatically restart if the server reboots.'),

    (4,
     'Our API uses CORS to only accept requests from our website. '
     'Users must log in (using JWT tokens) to use most features. '
     'The AI service is hidden from the internet for security. '
     'AWS Security Groups only open the ports we actually need (22, 80, 8080).'),

    (5,
     'Resumes are uploaded to S3 with random, unique names so they never overwrite each other. '
     'Extracted text like skills and education is saved in a MySQL database. '
     'Recruiters download resumes using secure S3 links that expire in 1 hour.'),

    (6,
     'Our Docker containers automatically restart if there is a crash. '
     'AWS S3 ensures our resume files are safe and never lost. '
     'Because our backend is stateless, we can easily add more servers later if we get more users.'),

    (7,
     'We use Docker logs to monitor the system and find errors. '
     'The backend prints a message every time a resume is parsed, showing the extracted skills. '
     'In the future, we will use AWS CloudWatch to save these logs permanently.'),

    (8,
     'The whole project is 100% free because we stay inside the AWS Free Tier limits. '
     'We use a free t2.micro EC2 server, very little S3 storage (under 5 GB), and free database space. '
     'We checked AWS pricing rules to avoid surprise bills.'),
]
for row_idx, response in cloud_responses:
    row = t4.rows[row_idx]
    row.cells[2].paragraphs[0].clear()
    row.cells[2].paragraphs[0].add_run(response)
    # DO NOT touch cells[3] (Score) or cells[4] (Notes) - supervisor fills those

# =========================================
# Save
# =========================================
out = r'c:\Users\Dell\Desktop\Cloud Projecct\d\CoverSheet_NextStep_v5.docx'
doc.save(out)
print(f'Saved: {out}')
