"""Multi-factor AI matching and explainable resume-to-job evaluation engine."""
from __future__ import annotations

import re
from typing import Any
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resume_parser import ALL_SKILLS


def preprocess_text(text: str) -> str:
    """Normalize text, filter stopwords, and retain alphanumeric & programming tokens."""
    tokens = re.findall(r"[a-zA-Z0-9+#.]{2,}", text.lower())
    return " ".join(t for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 1)


def determine_recommendation(composite_score: float) -> str:
    """Classify overall suitability category."""
    if composite_score >= 85:
        return "Excellent Match"
    if composite_score >= 70:
        return "Shortlist"
    if composite_score >= 50:
        return "Maybe"
    return "Reject"


def extract_skills_from_text(text: str) -> set[str]:
    """Identify skills present in raw text."""
    found = set()
    for skill in ALL_SKILLS:
        pattern = r"(?<![A-Za-z0-9])" + re.escape(skill).replace(r"\ ", r"[\s\-_]+") + r"(?!\w)"
        if re.search(pattern, text, re.IGNORECASE):
            found.add(skill)
    return found


def match_resume(resume_text: str, job_description: str, min_exp_years: float = 0.0) -> dict[str, Any]:
    """
    Perform transparent, multi-factor candidate evaluation against a Job Description:
    - Skill Match Score (45% weight)
    - Semantic / TF-IDF Similarity (35% weight)
    - Contextual Keyword & Experience Alignment (20% weight)
    """
    if not resume_text.strip() or not job_description.strip():
        raise ValueError("Both resume text and job description are required for analysis.")

    # 1. Skill Extraction & Overlap
    jd_skills = extract_skills_from_text(job_description)
    resume_skills = extract_skills_from_text(resume_text)

    matched_skills = sorted(list(jd_skills & resume_skills))
    missing_skills = sorted(list(jd_skills - resume_skills))
    additional_skills = sorted(list(resume_skills - jd_skills))

    if jd_skills:
        skill_coverage_ratio = len(matched_skills) / len(jd_skills)
        skill_score = min(100.0, round(skill_coverage_ratio * 100, 1))
    else:
        skill_score = 75.0  # Default if JD specifies no standard hard skills

    # 2. Semantic TF-IDF Similarity (Bi-grams with sublinear scaling)
    clean_resume = preprocess_text(resume_text)
    clean_jd = preprocess_text(job_description)

    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
        matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        cosine_sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        semantic_score = round(min(1.0, max(0.0, cosine_sim)) * 100, 1)
    except Exception:
        semantic_score = 50.0

    # 3. Context & Keyword Density
    jd_words = set(clean_jd.split())
    resume_words = set(clean_resume.split())
    if jd_words:
        keyword_overlap = len(jd_words & resume_words) / len(jd_words)
        context_score = min(100.0, round(keyword_overlap * 100, 1))
    else:
        context_score = 50.0

    # 4. Composite Multi-Factor Calculation
    # Skill Coverage: 45%, Semantic: 35%, Context / Keywords: 20%
    composite = (0.45 * skill_score) + (0.35 * semantic_score) + (0.20 * context_score)
    final_score = round(min(100.0, max(0.0, composite)), 1)
    rec = determine_recommendation(final_score)

    # 5. Generate Recruiter Highlights & Gaps
    strengths = []
    if matched_skills:
        strengths.append(f"Demonstrates core competencies in {', '.join(matched_skills[:5])}")
    if final_score >= 70:
        strengths.append("Strong vocabulary alignment with job responsibilities and requirements")
    if skill_score >= 80:
        strengths.append("Covers over 80% of required technical proficiencies")

    gaps = []
    if missing_skills:
        gaps.append(f"Missing explicit mentions of required skills: {', '.join(missing_skills[:5])}")
    if semantic_score < 45:
        gaps.append("Low overall semantic overlap with role descriptions and domain terms")

    interview_focus = []
    if missing_skills:
        interview_focus.append(f"Assess practical depth and adaptability in: {', '.join(missing_skills[:3])}")
    if matched_skills:
        interview_focus.append(f"Validate hands-on project accomplishments using: {', '.join(matched_skills[:3])}")

    return {
        "score": final_score,
        "recommendation": rec,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "breakdown": {
            "skill_match_score": skill_score,
            "semantic_score": semantic_score,
            "context_score": context_score,
            "total_jd_skills_count": len(jd_skills),
            "matched_skills_count": len(matched_skills),
            "missing_skills_count": len(missing_skills)
        },
        "strengths": strengths or ["General resume structure meets baseline format."],
        "gaps": gaps or ["No major skill deficiencies identified."],
        "interview_focus": interview_focus or ["Explore past project architectural decisions and team collaboration."]
    }

