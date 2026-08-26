"""Executive report generation, sample dataset seeder, and export utilities."""
from __future__ import annotations

import io
from datetime import datetime
from xml.sax.saxutils import escape
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert database rows into a clean, presentation-ready DataFrame."""
    records = []
    for r in rows:
        bd = r.get("score_breakdown", {})
        records.append({
            "Rank": 0,
            "Candidate": r.get("candidate_name", "Unknown"),
            "Target Role": r.get("target_role") or "General",
            "Score": r.get("match_score", 0),
            "Status": r.get("recommendation", "Not analyzed"),
            "Exp (Yrs)": r.get("experience_years", 0),
            "Skills": ", ".join(r.get("skills", [])[:6]) + ("..." if len(r.get("skills", [])) > 6 else ""),
            "Email": r.get("email", "-"),
            "Phone": r.get("phone", "-"),
            "Uploaded": r.get("upload_date", "-")
        })
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("Score", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index + 1
    return df


def create_pdf_report(candidate: dict[str, Any], jd: str, target_role: str = "") -> bytes:
    """Generate a high-impact, beautifully styled executive PDF candidate assessment report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
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
        fontName="Helvetica-Bold",
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica",
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e3a8a"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        fontName="Helvetica"
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("TALENTLENS AI &bull; CANDIDATE ASSESSMENT DOSSIER", subtitle_style))
    story.append(Paragraph(escape(candidate.get("candidate_name", "Candidate Report")), title_style))
    role_label = target_role or candidate.get("target_role") or "General Screening"
    story.append(Paragraph(f"<b>Evaluated Role:</b> {escape(role_label)} &nbsp;|&nbsp; <b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 0.1 * inch))

    # 2. Executive Scorecard Box
    score = candidate.get("match_score", 0)
    rec = candidate.get("recommendation", "Not analyzed")
    bd = candidate.get("score_breakdown", {})

    status_color = colors.HexColor("#10b981") if "Excellent" in rec else colors.HexColor("#3b82f6") if "Shortlist" in rec else colors.HexColor("#f59e0b") if "Maybe" in rec else colors.HexColor("#ef4444")

    scorecard_data = [
        [
            Paragraph("<b>Overall Match Score</b>", cell_bold),
            Paragraph("<b>Recommendation</b>", cell_bold),
            Paragraph("<b>Skill Coverage</b>", cell_bold),
            Paragraph("<b>Semantic Fit</b>", cell_bold),
        ],
        [
            Paragraph(f"<font size='16' color='#1e3a8a'><b>{score}%</b></font>", body_style),
            Paragraph(f"<b>{rec}</b>", body_style),
            Paragraph(f"<b>{bd.get('skill_match_score', score)}%</b>", body_style),
            Paragraph(f"<b>{bd.get('semantic_score', score)}%</b>", body_style),
        ]
    ]
    t_scorecard = Table(scorecard_data, colWidths=[1.7 * inch, 1.8 * inch, 1.7 * inch, 1.7 * inch])
    t_scorecard.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_scorecard)
    story.append(Spacer(1, 0.15 * inch))

    # 3. Candidate Profile Details Table
    story.append(Paragraph("Candidate Profile Summary", section_heading))
    profile_data = [
        [Paragraph("<b>Email:</b>", cell_bold), Paragraph(escape(candidate.get("email", "-")), body_style),
         Paragraph("<b>Phone:</b>", cell_bold), Paragraph(escape(candidate.get("phone", "-")), body_style)],
        [Paragraph("<b>LinkedIn:</b>", cell_bold), Paragraph(escape(candidate.get("linkedin") or "Not provided"), body_style),
         Paragraph("<b>GitHub:</b>", cell_bold), Paragraph(escape(candidate.get("github") or "Not provided"), body_style)],
        [Paragraph("<b>Estimated Exp:</b>", cell_bold), Paragraph(f"{candidate.get('experience_years', 0)} Years", body_style),
         Paragraph("<b>Education:</b>", cell_bold), Paragraph(escape(candidate.get("education_level") or candidate.get("education", "-")[:40]), body_style)],
    ]
    t_profile = Table(profile_data, colWidths=[1.2 * inch, 2.3 * inch, 1.2 * inch, 2.2 * inch])
    t_profile.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(t_profile)
    story.append(Spacer(1, 0.15 * inch))

    # 4. Skills Breakdown
    story.append(Paragraph("Technical Skills & Requirements Analysis", section_heading))
    all_skills = ", ".join(candidate.get("skills", [])) or "None explicitly detected"
    story.append(Paragraph(f"<b>Detected Candidate Skills:</b> {escape(all_skills)}", body_style))
    story.append(Spacer(1, 0.05 * inch))

    # 5. Evaluation Notes & Interview Guidance
    story.append(Paragraph("Recruiter Evaluation & Interview Focus", section_heading))
    story.append(Paragraph("<b>Key Strengths Identified:</b>", cell_bold))
    story.append(Paragraph(f"&bull; Profile exhibits relevant competency for the position with verified keywords in core domains.", body_style))
    story.append(Paragraph(f"&bull; Document parsed with structural integrity and verifiable background milestones.", body_style))
    story.append(Spacer(1, 0.05 * inch))

    story.append(Paragraph("<b>Recommended Interview Focus:</b>", cell_bold))
    story.append(Paragraph(f"&bull; Validate hands-on architectural problem-solving and recent project responsibilities.", body_style))
    story.append(Paragraph(f"&bull; Deep dive into practical tooling depth and team communication skills.", body_style))
    story.append(Spacer(1, 0.15 * inch))

    # 6. Target Job Description Excerpt
    story.append(Paragraph("Job Description Reference Excerpt", section_heading))
    clean_jd = (jd[:500] + "...") if len(jd) > 500 else (jd or "No specific job description supplied.")
    story.append(Paragraph(escape(clean_jd).replace("\n", "<br/>"), body_style))

    doc.build(story)
    return buffer.getvalue()


# ===================== Sample Data Seeder =====================

SAMPLE_JOB_ROLES = [
    {
        "title": "Senior Full Stack Engineer (React & Python)",
        "category": "Software Engineering",
        "min_experience": 4,
        "required_skills": ["Python", "React", "TypeScript", "FastAPI", "PostgreSQL", "Docker", "AWS", "REST API", "Git", "CI/CD"],
        "description": """We are looking for a Senior Full Stack Engineer to lead the architecture and development of our modern cloud applications.
Responsibilities:
- Build responsive, interactive web frontends using React, TypeScript, and modern state management.
- Design scalable backend microservices and REST APIs using Python, FastAPI, or Django.
- Architect database schemas and optimize queries in PostgreSQL.
- Containerize services with Docker and deploy to AWS infrastructure.
- Collaborate with cross-functional teams in an Agile/Scrum environment with CI/CD automation."""
    },
    {
        "title": "Lead AI / Machine Learning Engineer",
        "category": "AI & Data Science",
        "min_experience": 5,
        "required_skills": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "NLP", "LLMs", "RAG", "LangChain", "Docker", "MLOps", "FastAPI"],
        "description": """Seeking an experienced Machine Learning / Generative AI Engineer to build cutting-edge AI features.
Responsibilities:
- Develop, fine-tune, and evaluate deep learning and NLP models (LLMs, transformers, RAG architectures).
- Deploy production inference pipelines with FastAPI, Docker, and MLOps tooling.
- Collaborate with software engineers to integrate vector databases (Pinecone/ChromaDB).
- Drive data preprocessing, feature engineering, and performance benchmarking."""
    },
    {
        "title": "Cloud DevOps & Infrastructure Specialist",
        "category": "DevOps & Cloud",
        "min_experience": 3,
        "required_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "GitHub Actions", "Linux", "Python", "Prometheus", "Grafana"],
        "description": """We are hiring a Cloud DevOps Specialist to automate and scale our cloud infrastructure.
Responsibilities:
- Manage multi-region cloud environments on AWS using Infrastructure as Code (Terraform).
- Configure Kubernetes (K8s) clusters, service meshes, and autoscaling policies.
- Build resilient CI/CD delivery pipelines using GitHub Actions and Docker.
- Implement monitoring, observability, and alerting with Prometheus, Grafana, and ELK."""
    }
]

SAMPLE_CANDIDATES = [
    {
        "candidate_name": "Alexander Hayes",
        "email": "alex.hayes@example.com",
        "phone": "+1 (555) 234-8901",
        "linkedin": "https://linkedin.com/in/alex-hayes-tech",
        "github": "https://github.com/alexhayes-dev",
        "skills": ["Python", "React", "TypeScript", "FastAPI", "Django", "PostgreSQL", "Docker", "AWS", "REST API", "Git", "CI/CD", "Redis", "Agile"],
        "resume_file": "Alexander_Hayes_FullStack.pdf",
        "match_score": 92.5,
        "recommendation": "Excellent Match",
        "experience_years": 6.0,
        "education_level": "Bachelor's Degree",
        "education": "B.S. in Computer Science, University of Washington",
        "experience": "Lead Full Stack Developer at NexaTech (2020 - Present)\n- Led architecture of SaaS web platform using React, TypeScript and FastAPI\n- Reduced database latency by 45% using PostgreSQL indexing and Redis caching\n- Mentored junior engineers and instituted automated CI/CD pipelines on AWS",
        "projects": "Distributed Task Queue: Built high-throughput task processor with Python & Redis.\nE-Commerce Microservices: Created modular microservice ecosystem with Docker & FastAPI.",
        "certificates": "AWS Certified Solutions Architect &bull; Scrum Master Certified",
        "resume_text": "Alexander Hayes | alex.hayes@example.com | +1 (555) 234-8901 | linkedin.com/in/alex-hayes-tech\nSummary: Experienced Senior Full Stack Software Engineer with 6+ years specializing in Python, FastAPI, Django, React, TypeScript, PostgreSQL, and AWS cloud deployment. Passionate about scalable architecture and high-performance APIs.",
        "target_role": "Senior Full Stack Engineer (React & Python)"
    },
    {
        "candidate_name": "Dr. Sophia Chen",
        "email": "sophia.chen@ai-research.org",
        "phone": "+1 (555) 789-4321",
        "linkedin": "https://linkedin.com/in/dr-sophia-chen",
        "github": "https://github.com/sophia-ml",
        "skills": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "NLP", "LLMs", "Generative AI", "RAG", "LangChain", "Hugging Face", "FastAPI", "Docker", "MLOps", "Pandas", "NumPy"],
        "resume_file": "Sophia_Chen_AIML.pdf",
        "match_score": 95.0,
        "recommendation": "Excellent Match",
        "experience_years": 7.5,
        "education_level": "Ph.D. / Doctorate",
        "education": "Ph.D. in Artificial Intelligence, Stanford University (2018)",
        "experience": "Staff AI Research Engineer at OmniAI Labs (2021 - Present)\n- Researched and deployed enterprise RAG systems using LangChain, Vector DBs, and open-source LLMs\n- Optimized model inference throughput by 3.5x using ONNX and TensorRT\n- Published 4 top-tier NLP papers in ACL and NeurIPS",
        "projects": "Enterprise RAG Pipeline: Multimodal retrieval system using PyTorch & Hugging Face.\nNeural Text Summarizer: Production-grade summarizer serving 100k daily queries.",
        "certificates": "Deep Learning Specialization (DeepLearning.AI)",
        "resume_text": "Dr. Sophia Chen | sophia.chen@ai-research.org | +1 (555) 789-4321\nStaff AI & Machine Learning Scientist with 7+ years building enterprise LLMs, RAG, PyTorch, Hugging Face, NLP, and scalable MLOps architectures.",
        "target_role": "Lead AI / Machine Learning Engineer"
    },
    {
        "candidate_name": "Marcus Vance",
        "email": "marcus.vance@cloudops.net",
        "phone": "+1 (555) 345-6712",
        "linkedin": "https://linkedin.com/in/marcus-vance-cloud",
        "github": "https://github.com/mvance-infra",
        "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "GitHub Actions", "Jenkins", "Linux", "Python", "Prometheus", "Grafana", "Bash", "Ansible", "Nginx"],
        "resume_file": "Marcus_Vance_DevOps.pdf",
        "match_score": 88.0,
        "recommendation": "Shortlist",
        "experience_years": 4.5,
        "education_level": "Bachelor's Degree",
        "education": "B.Tech in Information Technology, Georgia Tech",
        "experience": "Senior DevOps Engineer at CloudScale Systems (2021 - Present)\n- Managed 150+ microservice containers in multi-cluster Kubernetes on AWS\n- Automated infrastructure deployment using Terraform and GitHub Actions\n- Reduced system downtime by 70% with Prometheus & Grafana real-time monitoring",
        "projects": "GitOps Infrastructure Orchestrator: Automated multi-environment provisioning with Terraform.\nZero-Downtime Deployment Pipeline: Blue-green deployment pipeline with Docker & K8s.",
        "certificates": "Certified Kubernetes Administrator (CKA) &bull; AWS Certified SysOps Administrator",
        "resume_text": "Marcus Vance | marcus.vance@cloudops.net | +1 (555) 345-6712\nDevOps & Cloud Engineer with 4.5 years managing AWS infrastructure, Docker, Kubernetes, Terraform, Prometheus, and CI/CD pipelines.",
        "target_role": "Cloud DevOps & Infrastructure Specialist"
    },
    {
        "candidate_name": "Elena Rostova",
        "email": "elena.rostova@frontend-dev.io",
        "phone": "+1 (555) 654-9870",
        "linkedin": "https://linkedin.com/in/elena-rostova",
        "github": "https://github.com/elena-rostova",
        "skills": ["React", "JavaScript", "TypeScript", "HTML5", "CSS3", "Tailwind CSS", "Redux", "REST API", "Figma", "Git", "Next.js", "Node.js"],
        "resume_file": "Elena_Rostova_Frontend.pdf",
        "match_score": 78.5,
        "recommendation": "Shortlist",
        "experience_years": 3.5,
        "education_level": "Bachelor's Degree",
        "education": "B.S. in Software Engineering, UC Berkeley",
        "experience": "Frontend Engineer at PixelCraft Studio (2022 - Present)\n- Built responsive web dashboards using React 18, TypeScript, and Tailwind CSS\n- Translated complex Figma design systems into pixel-perfect UI component libraries",
        "projects": "Design System Library: 60+ accessible React components with Tailwind CSS.\nCrypto Analytics Dashboard: Real-time interactive charting web application.",
        "certificates": "Meta Frontend Developer Professional Certificate",
        "resume_text": "Elena Rostova | elena.rostova@frontend-dev.io | React Frontend Developer with 3.5+ years building UI applications, TypeScript, Next.js, and modern CSS systems.",
        "target_role": "Senior Full Stack Engineer (React & Python)"
    }
]


def seed_sample_data(database_module) -> None:
    """Populate sample job roles and candidate profiles for instant testing."""
    for role in SAMPLE_JOB_ROLES:
        database_module.save_job_role(
            title=role["title"],
            description=role["description"],
            category=role["category"],
            required_skills=role["required_skills"],
            min_experience=role["min_experience"]
        )

    for cand in SAMPLE_CANDIDATES:
        from datetime import datetime
        cand_copy = cand.copy()
        cand_copy["upload_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        cand_copy["score_breakdown"] = {
            "skill_match_score": cand["match_score"] + 2,
            "semantic_score": cand["match_score"] - 1,
            "context_score": cand["match_score"],
            "total_jd_skills_count": 10,
            "matched_skills_count": len(cand["skills"])
        }
        database_module.save_resume(cand_copy)

