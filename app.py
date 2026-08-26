"""
TalentLens AI — Enterprise AI Resume Intelligence & Recruitment Platform.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

import charts
import database
from database import (
    DB_PATH, clear_resumes, delete_job_role, delete_resume,
    get_job_roles, get_resumes, init_db, save_job_role,
    save_resume, update_analysis
)
from matcher import match_resume
from resume_parser import extract_text, parse_resume
from utils import (
    SAMPLE_JOB_ROLES, create_pdf_report, seed_sample_data, to_dataframe
)

# Application Configuration
ROOT = Path(__file__).resolve().parent
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)

st.set_page_config(
    page_title="TalentLens AI — Enterprise Talent Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database and Seed Default Roles if Empty
init_db()
if not get_job_roles():
    for role in SAMPLE_JOB_ROLES:
        save_job_role(
            title=role["title"],
            description=role["description"],
            category=role["category"],
            required_skills=role["required_skills"],
            min_experience=role["min_experience"]
        )


def load_css() -> None:
    """Inject custom stylesheet."""
    css_path = ROOT / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def metric_card(value: Any, label: str) -> None:
    """Render modern KPI metric card."""
    st.markdown(
        f'<div class="metric-card"><div class="n">{value}</div><div class="l">{label}</div></div>',
        unsafe_allow_html=True
    )


def skill_badges(skills: list[str], badge_type: str = "normal") -> str:
    """Render list of skills as clean styled HTML chips."""
    if not skills:
        return "<span style='color:#64748b; font-size:0.85rem;'>None detected</span>"
    cls_map = {
        "normal": "badge",
        "matched": "badge badge-matched",
        "missing": "badge badge-missing"
    }
    css_class = cls_map.get(badge_type, "badge")
    return "".join(f'<span class="{css_class}">{s}</span>' for s in skills)


def status_badge(status: str) -> str:
    """Render suitability recommendation status pill."""
    css = {
        "Excellent Match": "excellent",
        "Shortlist": "shortlist",
        "Maybe": "maybe",
        "Reject": "reject",
        "Not analyzed": "maybe"
    }.get(status, "maybe")
    return f'<span class="status {css}">{status}</span>'


# ===================== Navigation Sidebar =====================

def render_sidebar(rows: list[dict[str, Any]], roles: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
    """Render executive sidebar with active role selection and navigation."""
    with st.sidebar:
        st.markdown("## ✦ TalentLens AI")
        st.caption("Enterprise Candidate Screening & Matching Platform")
        st.divider()

        # Active Job Profile Selector
        st.markdown("**Active Evaluation Role**")
        role_titles = [r["title"] for r in roles]
        if not role_titles:
            role_titles = ["General Screening"]
        
        selected_role_title = st.selectbox(
            "Select target role",
            role_titles,
            index=0,
            label_visibility="collapsed"
        )
        active_role = next((r for r in roles if r["title"] == selected_role_title), None)

        st.divider()
        st.markdown("**Navigation**")
        page = st.radio(
            "Navigation Menu",
            [
                "🏠 Dashboard Overview",
                "📁 Resume Ingestion",
                "💼 Job Role Profiles",
                "⚡ AI Batch Screening",
                "🔍 Candidate Deep Dive",
                "⚖️ Candidate Comparison",
                "📊 Talent Analytics",
                "🗄️ Database & Settings",
                "ℹ️ About Platform"
            ],
            label_visibility="collapsed"
        )

        st.divider()
        # Sidebar Summary Box
        st.markdown(
            f"""<div style='background:rgba(15,23,42,0.6); padding:0.9rem; border-radius:12px; border:1px solid rgba(51,65,85,0.4); font-size:0.85rem;'>
            <div style='color:#94a3b8; margin-bottom:4px;'>SYSTEM STATUS</div>
            <div style='color:#38bdf8; font-weight:700;'>● SQLite Database Active</div>
            <div style='color:#e2e8f0; margin-top:4px;'>👥 Candidates: <b>{len(rows)}</b></div>
            <div style='color:#e2e8f0;'>💼 Active Roles: <b>{len(roles)}</b></div>
            </div>""",
            unsafe_allow_html=True
        )

        st.write("")
        if st.button("✨ Load Demo Dataset", use_container_width=True):
            seed_sample_data(database)
            st.toast("Loaded sample job roles and candidate profiles!", icon="✅")
            st.rerun()

    return page, active_role


# ===================== Page 1: Dashboard =====================

def page_dashboard(rows: list[dict[str, Any]], active_role: dict[str, Any] | None) -> None:
    role_name = active_role["title"] if active_role else "All Roles"
    
    st.markdown(
        f"""<div class="hero">
            <h1>Recruitment Intelligence with Clarity.</h1>
            <p>Evaluating candidate pool against <b>{role_name}</b>. Ingest resumes, calculate multi-factor lexical & semantic similarity, and surface top talent in seconds.</p>
        </div>""",
        unsafe_allow_html=True
    )

    # Summary Metrics
    total = len(rows)
    analyzed = sum(r["recommendation"] != "Not analyzed" for r in rows)
    top_matches = sum(r["recommendation"] == "Excellent Match" for r in rows)
    shortlisted = sum(r["recommendation"] in ("Excellent Match", "Shortlist") for r in rows)
    avg_score = round(sum(r["match_score"] for r in rows) / total, 1) if total else 0.0

    cols = st.columns(4)
    with cols[0]: metric_card(total, "Total Candidates")
    with cols[1]: metric_card(f"{top_matches}", "Top Tier (85%+)")
    with cols[2]: metric_card(f"{shortlisted}", "Shortlist Eligible")
    with cols[3]: metric_card(f"{avg_score}%", "Average Match")

    st.write("")
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("### Top Ranked Candidates")
        if rows:
            df = to_dataframe(rows).head(5)
            st.dataframe(
                df[["Rank", "Candidate", "Score", "Status", "Exp (Yrs)", "Skills"]],
                use_container_width=True,
                hide_index=True,
                column_config={"Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f%%")}
            )
        else:
            st.info("No candidates in the database yet. Upload resumes or load the demo dataset to begin.")

    with c2:
        st.markdown("### Quick Actions")
        st.markdown("""<div class="info-card">
            <h4>⚡ One-Click Batch Screening</h4>
            <p>Screen all candidate resumes against the active role simultaneously with automated scoring.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Run Batch Screen Now", type="primary", use_container_width=True):
            if not active_role:
                st.error("Please configure a Job Role first.")
            elif not rows:
                st.warning("Please upload candidate resumes first.")
            else:
                progress = st.progress(0, text="Screening candidates...")
                for i, cand in enumerate(rows, 1):
                    res = match_resume(cand["resume_text"], active_role["description"], active_role.get("min_experience", 0))
                    update_analysis(cand["id"], res["score"], res["recommendation"], res["breakdown"], active_role["title"])
                    progress.progress(i / len(rows), text=f"Evaluated {cand['candidate_name']} ({i}/{len(rows)})")
                progress.empty()
                st.toast("Batch screening finished successfully!", icon="🚀")
                st.rerun()

    st.markdown("<div class='footer'>TalentLens AI Enterprise Edition &bull; Precision Recruitment Analytics</div>", unsafe_allow_html=True)


# ===================== Page 2: Resume Ingestion =====================

def page_upload() -> None:
    st.title("📁 Resume Ingestion & Extraction")
    st.caption("Upload candidate resumes in PDF or DOCX formats for automatic parsing and skill detection.")

    t1, t2 = st.tabs(["📤 Upload Files", "💡 Extraction Specifications"])

    with t1:
        uploaded_files = st.file_uploader(
            "Drag and drop PDF or DOCX resumes",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="Upload one or multiple resumes simultaneously."
        )

        if uploaded_files:
            st.info(f"Ready to ingest {len(uploaded_files)} document(s).")
            if st.button("Process & Ingest Resumes", type="primary"):
                progress_bar = st.progress(0, text="Starting parser...")
                success_count = 0
                duplicate_count = 0
                error_list = []

                for idx, file in enumerate(uploaded_files, 1):
                    try:
                        text = extract_text(file)
                        if len(text.strip()) < 20:
                            raise ValueError("Extracted text is too short or empty.")

                        parsed = parse_resume(text, file.name)
                        parsed.update({
                            "match_score": 0.0,
                            "recommendation": "Not analyzed",
                            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "score_breakdown": {},
                            "target_role": ""
                        })

                        if save_resume(parsed):
                            (UPLOADS / file.name).write_bytes(file.getvalue())
                            success_count += 1
                        else:
                            duplicate_count += 1
                    except Exception as err:
                        error_list.append(f"{file.name}: {str(err)}")

                    progress_bar.progress(idx / len(uploaded_files), text=f"Processed {idx} of {len(uploaded_files)}...")

                progress_bar.empty()
                st.success(f"✓ Ingestion complete: {success_count} added, {duplicate_count} duplicates skipped.")
                if error_list:
                    st.error("Some files encountered errors:")
                    st.code("\n".join(error_list))

    with t2:
        st.markdown("""
        #### Supported Extraction Pipeline
        - **Format Coverage**: PDF (layout-preserved via `pdfplumber` & `PyPDF2`) and DOCX (paragraphs and table parsing).
        - **Entity Recognition**: Candidate Name, Email, Phone Number, LinkedIn URL, GitHub URL, Education Level, and Estimated Experience.
        - **Skill Taxonomy**: 250+ categorized industry technical proficiencies.
        """)


# ===================== Page 3: Job Role Profiles =====================

def page_jobs(roles: list[dict[str, Any]]) -> None:
    st.title("💼 Job Role & Description Library")
    st.caption("Manage target job positions, skill requirements, and benchmark criteria.")

    t1, t2 = st.tabs(["📋 Active Job Profiles", "➕ Create / Edit Role"])

    with t1:
        if not roles:
            st.info("No job roles defined. Create a new job description in the next tab.")
        for r in roles:
            with st.expander(f"**{r['title']}** &nbsp;·&nbsp; *{r.get('category', 'Engineering')}* &nbsp;·&nbsp; Min Exp: {r.get('min_experience', 0)} Yrs", expanded=False):
                st.markdown("**Required Skills:**")
                st.markdown(skill_badges(r.get("required_skills", [])), unsafe_allow_html=True)
                st.markdown("**Job Description:**")
                st.code(r["description"], language="text")
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button(f"Delete Role", key=f"del_role_{r['id']}"):
                        delete_job_role(r["id"])
                        st.toast(f"Deleted role: {r['title']}")
                        st.rerun()

    with t2:
        st.subheader("Add or Update Job Position")
        title = st.text_input("Job Title", placeholder="e.g. Senior Backend Engineer (Python & Cloud)")
        cat = st.selectbox("Category", ["Software Engineering", "AI & Data Science", "DevOps & Cloud", "Product & Design", "Management", "Other"])
        min_exp = st.number_input("Minimum Experience (Years)", min_value=0, max_value=25, value=3)
        skills_input = st.text_input("Required Skills (comma-separated)", placeholder="Python, FastAPI, PostgreSQL, Docker, AWS")
        desc = st.text_area("Job Description & Requirements", height=240, placeholder="Paste the complete role description, responsibilities, and qualifications...")

        if st.button("Save Job Role Profile", type="primary"):
            if not title.strip() or not desc.strip():
                st.error("Please provide both a Job Title and Description.")
            else:
                skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
                save_job_role(
                    title=title.strip(),
                    description=desc.strip(),
                    category=cat,
                    required_skills=skills_list,
                    min_experience=int(min_exp)
                )
                st.success(f"Job Role '{title}' saved successfully!")
                st.rerun()


# ===================== Page 4: AI Batch Screening =====================

def page_screening(rows: list[dict[str, Any]], active_role: dict[str, Any] | None) -> None:
    st.title("⚡ AI Batch Screening & Ranking")
    if not active_role:
        st.warning("Please configure or select a target Job Role first.")
        return

    st.caption(f"Evaluating candidate pool against **{active_role['title']}**")

    col_btn, col_filter, col_search = st.columns([1.5, 1.5, 2])
    with col_btn:
        if st.button("🚀 Screen All Candidates Now", type="primary", use_container_width=True):
            if not rows:
                st.warning("No resumes in the database.")
            else:
                prog = st.progress(0, text="Screening candidates...")
                for idx, c in enumerate(rows, 1):
                    res = match_resume(c["resume_text"], active_role["description"], active_role.get("min_experience", 0))
                    update_analysis(c["id"], res["score"], res["recommendation"], res["breakdown"], active_role["title"])
                    prog.progress(idx / len(rows), text=f"Evaluated {c['candidate_name']} ({idx}/{len(rows)})")
                prog.empty()
                st.success("Screening complete!")
                st.rerun()

    with col_filter:
        status_filter = st.selectbox("Filter by Status", ["All", "Excellent Match", "Shortlist", "Maybe", "Reject"])

    with col_search:
        min_score = st.slider("Minimum Match Score (%)", 0, 100, 0)

    # Filter rows
    filtered = rows
    if status_filter != "All":
        filtered = [r for r in filtered if r.get("recommendation") == status_filter]
    if min_score > 0:
        filtered = [r for r in filtered if r.get("match_score", 0) >= min_score]

    st.divider()
    if not filtered:
        st.info("No candidates match the specified filter criteria.")
        return

    df = to_dataframe(filtered)
    st.dataframe(
        df[["Rank", "Candidate", "Score", "Status", "Exp (Yrs)", "Skills", "Email", "Uploaded"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=100, format="%.1f%%"),
            "Email": st.column_config.LinkColumn("Email")
        }
    )

    c_exp1, c_exp2 = st.columns(2)
    with c_exp1:
        st.download_button(
            "📥 Export Ranking (CSV)",
            df.to_csv(index=False).encode(),
            file_name=f"screening_ranking_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c_exp2:
        st.download_button(
            "📥 Export Full Data (JSON)",
            json.dumps(filtered, indent=2).encode(),
            file_name=f"candidates_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )


# ===================== Page 5: Candidate Deep Dive =====================

def page_candidate_detail(rows: list[dict[str, Any]], active_role: dict[str, Any] | None) -> None:
    st.title("🔍 Candidate Deep Dive & Dossier")
    if not rows:
        st.info("Upload resumes to evaluate candidates.")
        return

    jd_text = active_role["description"] if active_role else ""
    target_role_title = active_role["title"] if active_role else "General Role"

    candidate_names = {f"{r['candidate_name']} ({r['resume_file']})": r for r in rows}
    selected_name = st.selectbox("Select Candidate to Inspect", list(candidate_names.keys()))
    candidate = candidate_names[selected_name]

    # Re-evaluate candidate against current JD if requested or missing breakdown
    c_btn1, c_btn2 = st.columns([1.5, 4])
    with c_btn1:
        if st.button("Run AI Deep Evaluation", type="primary", use_container_width=True):
            if not jd_text:
                st.warning("Please configure an active Job Role description first.")
            else:
                with st.spinner("Analyzing candidate competency and semantic relevance..."):
                    res = match_resume(candidate["resume_text"], jd_text)
                    update_analysis(candidate["id"], res["score"], res["recommendation"], res["breakdown"], target_role_title)
                    st.session_state[f"eval_{candidate['id']}"] = res
                st.rerun()

    # Retrieve evaluation results
    eval_data = st.session_state.get(f"eval_{candidate['id']}")
    if not eval_data:
        if jd_text:
            eval_data = match_resume(candidate["resume_text"], jd_text)
        else:
            eval_data = {
                "score": candidate.get("match_score", 0),
                "recommendation": candidate.get("recommendation", "Not analyzed"),
                "matched_skills": candidate.get("skills", []),
                "missing_skills": [],
                "breakdown": candidate.get("score_breakdown", {}),
                "strengths": ["Document parsed successfully."],
                "gaps": ["Configure a Job Description for gap analysis."],
                "interview_focus": ["General technical background inquiry."]
            }

    st.divider()

    # Top Candidate Header Card
    left_col, right_col = st.columns([1.2, 2])
    with left_col:
        score = eval_data.get("score", candidate["match_score"])
        rec = eval_data.get("recommendation", candidate["recommendation"])
        st.markdown(f"### {candidate['candidate_name']}")
        st.markdown(f"Target Role: **{target_role_title}**")
        st.markdown(status_badge(rec), unsafe_allow_html=True)
        st.write("")
        st.metric("Overall Match Score", f"{score}%")
        st.progress(min(int(score), 100))

        bd = eval_data.get("breakdown", candidate.get("score_breakdown", {}))
        if bd:
            st.caption(f"🎯 Skill Match: **{bd.get('skill_match_score', 0)}%** &bull; 🧠 Semantic Fit: **{bd.get('semantic_score', 0)}%**")

    with right_col:
        st.plotly_chart(charts.candidate_radar_chart(candidate), use_container_width=True)

    # Contact & Social Row
    st.markdown("#### Contact & Credentials")
    co1, co2, co3, co4 = st.columns(4)
    with co1: st.write(f"📧 **Email:** {candidate['email']}")
    with co2: st.write(f"📱 **Phone:** {candidate['phone']}")
    with co3:
        if candidate.get("linkedin"):
            st.markdown(f"💼 **LinkedIn:** [{candidate['linkedin'].split('/')[-1]}]({candidate['linkedin']})")
        else:
            st.write("💼 **LinkedIn:** Not detected")
    with co4:
        if candidate.get("github"):
            st.markdown(f"🐙 **GitHub:** [{candidate['github'].split('/')[-1]}]({candidate['github']})")
        else:
            st.write("🐙 **GitHub:** Not detected")

    # Skills Breakdown Matrix
    st.markdown("#### Skill Gap & Competency Analysis")
    sk1, sk2 = st.columns(2)
    with sk1:
        st.markdown("**✓ Matched Job Skills**")
        st.markdown(skill_badges(eval_data.get("matched_skills", []), "matched"), unsafe_allow_html=True)
    with sk2:
        st.markdown("**✗ Missing / Unverified Skills**")
        st.markdown(skill_badges(eval_data.get("missing_skills", []), "missing"), unsafe_allow_html=True)

    # Recruiter Insights
    st.markdown("#### Recruiter Insights & Interview Guidance")
    in1, in2 = st.columns(2)
    with in1:
        st.markdown("""<div class="info-card">
            <h4>🌟 Key Strengths</h4>
        """ + "".join(f"<p>• {s}</p>" for s in eval_data.get("strengths", [])) + "</div>", unsafe_allow_html=True)
    with in2:
        st.markdown("""<div class="info-card">
            <h4>💡 Recommended Interview Focus</h4>
        """ + "".join(f"<p>• {q}</p>" for q in eval_data.get("interview_focus", [])) + "</div>", unsafe_allow_html=True)

    # Resume Section Details
    with st.expander("📄 Extracted Resume Sections & Raw Text Preview"):
        t_sec1, t_sec2 = st.tabs(["Structured Sections", "Raw Document Text"])
        with t_sec1:
            st.markdown(f"**Estimated Experience:** {candidate.get('experience_years', 0)} Years")
            st.markdown(f"**Education Level:** {candidate.get('education_level', '-')}")
            st.markdown(f"**Education Section:**\n\n{candidate.get('education', '-')}")
            st.markdown(f"**Experience Section:**\n\n{candidate.get('experience', '-')}")
            st.markdown(f"**Key Projects:**\n\n{candidate.get('projects', '-')}")
            st.markdown(f"**Certificates:**\n\n{candidate.get('certificates', '-')}")
        with t_sec2:
            st.text_area("Extracted Resume Content", candidate["resume_text"], height=300, disabled=True)

    # PDF Download
    pdf_bytes = create_pdf_report(candidate, jd_text, target_role_title)
    st.download_button(
        label="📄 Download Executive Candidate Dossier (PDF)",
        data=pdf_bytes,
        file_name=f"{candidate['candidate_name'].replace(' ', '_')}_Assessment_Report.pdf",
        mime="application/pdf",
        type="primary"
    )


# ===================== Page 6: Candidate Comparison =====================

def page_comparison(rows: list[dict[str, Any]]) -> None:
    st.title("⚖️ Side-by-Side Candidate Comparison")
    if len(rows) < 2:
        st.info("Please have at least 2 candidates in the database for comparison.")
        return

    st.caption("Select 2 or 3 candidates for a side-by-side competency matrix and comparative charts.")

    cand_map = {r["candidate_name"]: r for r in rows}
    selected_names = st.multiselect(
        "Select Candidates to Compare",
        list(cand_map.keys()),
        default=list(cand_map.keys())[:min(3, len(cand_map))],
        max_selections=4
    )

    if len(selected_names) < 2:
        st.warning("Please select at least 2 candidates to compare.")
        return

    selected_cands = [cand_map[name] for name in selected_names]

    # Comparison Chart
    st.plotly_chart(charts.comparison_bar_chart(selected_cands), use_container_width=True)

    # Comparison Matrix Table
    st.markdown("### Comparative Evaluation Matrix")
    matrix_data = []
    headers = ["Metric"] + [c["candidate_name"] for c in selected_cands]

    matrix_data.append(["Match Score"] + [f"{c.get('match_score', 0)}%" for c in selected_cands])
    matrix_data.append(["Recommendation"] + [c.get("recommendation", "Not analyzed") for c in selected_cands])
    matrix_data.append(["Estimated Experience"] + [f"{c.get('experience_years', 0)} Yrs" for c in selected_cands])
    matrix_data.append(["Education"] + [c.get("education_level", "Not specified") for c in selected_cands])
    matrix_data.append(["Total Skills Count"] + [str(len(c.get("skills", []))) for c in selected_cands])
    matrix_data.append(["Top Skills"] + [", ".join(c.get("skills", [])[:5]) for c in selected_cands])

    df_comp = pd.DataFrame(matrix_data, columns=headers)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)


# ===================== Page 7: Talent Analytics =====================

def page_analytics(rows: list[dict[str, Any]]) -> None:
    st.title("📊 Talent Analytics & Visual Insights")
    if not rows:
        st.info("Upload resumes and analyze candidates to unlock talent analytics.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.score_distribution(rows), use_container_width=True)
    with c2:
        st.plotly_chart(charts.score_bar(rows), use_container_width=True)

    st.plotly_chart(charts.top_skills(rows), use_container_width=True)


# ===================== Page 8: Database & Admin =====================

def page_database(rows: list[dict[str, Any]]) -> None:
    st.title("🗄️ Candidate Database Repository")
    st.caption("Manage candidate data, export backups, and execute administrative operations.")

    search_query = st.text_input("Search repository by Name, Email, or Skill keyword", placeholder="Search...")
    filtered_rows = get_resumes(search=search_query)

    st.markdown(f"Found **{len(filtered_rows)}** candidate records.")
    if filtered_rows:
        df = to_dataframe(filtered_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "📥 Export Full Candidate Database (CSV)",
        to_dataframe(rows).to_csv(index=False).encode(),
        file_name="candidate_repository_backup.csv",
        mime="text/csv"
    )

    st.divider()
    st.markdown("### Record Maintenance")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**Delete Specific Candidate**")
        target_name = st.selectbox(
            "Select candidate to remove",
            ["Select candidate..."] + [f"{r['id']}: {r['candidate_name']} ({r['resume_file']})" for r in rows]
        )
        if target_name != "Select candidate..." and st.button("Delete Candidate Record", type="secondary"):
            cand_id = int(target_name.split(":")[0])
            cand = next(r for r in rows if r["id"] == cand_id)
            delete_resume(cand_id)
            file_on_disk = UPLOADS / cand["resume_file"]
            if file_on_disk.exists():
                file_on_disk.unlink()
            st.success(f"Candidate {cand['candidate_name']} removed.")
            st.rerun()

    with d2:
        st.markdown("**Purge All Records**")
        if st.checkbox("I confirm permanent deletion of all candidate records"):
            if st.button("Purge Database", type="secondary"):
                clear_resumes()
                if UPLOADS.exists():
                    shutil.rmtree(UPLOADS)
                UPLOADS.mkdir(exist_ok=True)
                st.success("Database purged.")
                st.rerun()


# ===================== Page 9: About Platform =====================

def page_about() -> None:
    st.title("ℹ️ About TalentLens AI")
    st.markdown("""
    ### Enterprise Candidate Screening & Talent Intelligence
    **TalentLens AI** is an explainable, transparent candidate evaluation and recruitment assistant engineered for hiring teams, talent acquisition leaders, and engineering managers.

    #### Core Architectural Pillars:
    1. **Transparent Lexical & Semantic Hybrid Matching**:
       - 45% Skill Intersection Weight (250+ skill taxonomy).
       - 35% TF-IDF N-gram Cosine Semantic Similarity.
       - 20% Contextual & Keyword Alignment.
    2. **Explainability First**:
       - No opaque black-box decisions. Every candidate score is accompanied by granular skill gaps, strengths, and recommended interview questions.
    3. **Privacy & Data Sovereignty**:
       - All resumes, embeddings, and candidate databases reside locally in SQLite and your dedicated storage.

    ---
    *Built with Streamlit, scikit-learn, ReportLab, Plotly, pdfplumber, python-docx, and SQLite.*
    """)


# ===================== Main Application Entrypoint =====================

def main() -> None:
    load_css()
    rows = get_resumes()
    roles = get_job_roles()

    page, active_role = render_sidebar(rows, roles)

    if page == "🏠 Dashboard Overview":
        page_dashboard(rows, active_role)
    elif page == "📁 Resume Ingestion":
        page_upload()
    elif page == "💼 Job Role Profiles":
        page_jobs(roles)
    elif page == "⚡ AI Batch Screening":
        page_screening(rows, active_role)
    elif page == "🔍 Candidate Deep Dive":
        page_candidate_detail(rows, active_role)
    elif page == "⚖️ Candidate Comparison":
        page_comparison(rows)
    elif page == "📊 Talent Analytics":
        page_analytics(rows)
    elif page == "🗄️ Database & Settings":
        page_database(rows)
    else:
        page_about()


if __name__ == "__main__":
    main()

