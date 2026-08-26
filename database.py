"""SQLite persistence helpers and schema management for TalentLens AI."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "resumes.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection configured to expose rows as dictionaries."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables and perform automatic non-destructive migrations."""
    with get_connection() as conn:
        # Create resumes table if not exists
        conn.execute(
            """CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                skills TEXT,
                resume_file TEXT NOT NULL UNIQUE,
                match_score REAL DEFAULT 0,
                recommendation TEXT DEFAULT 'Not analyzed',
                upload_date TEXT NOT NULL,
                resume_text TEXT DEFAULT '',
                education TEXT DEFAULT '',
                experience TEXT DEFAULT '',
                projects TEXT DEFAULT '',
                certificates TEXT DEFAULT '',
                linkedin TEXT DEFAULT '',
                github TEXT DEFAULT '',
                experience_years REAL DEFAULT 0,
                score_breakdown TEXT DEFAULT '{}',
                target_role TEXT DEFAULT ''
            )"""
        )

        # Create job_roles table if not exists
        conn.execute(
            """CREATE TABLE IF NOT EXISTS job_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT 'Engineering',
                description TEXT NOT NULL,
                required_skills TEXT DEFAULT '[]',
                min_experience INTEGER DEFAULT 0,
                created_date TEXT NOT NULL
            )"""
        )

        # Non-destructive migrations for existing databases
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(resumes)")
        columns = [col["name"] for col in cursor.fetchall()]

        new_columns = [
            ("linkedin", "TEXT DEFAULT ''"),
            ("github", "TEXT DEFAULT ''"),
            ("experience_years", "REAL DEFAULT 0"),
            ("score_breakdown", "TEXT DEFAULT '{}'"),
            ("target_role", "TEXT DEFAULT ''"),
        ]

        for col_name, col_type in new_columns:
            if col_name not in columns:
                try:
                    conn.execute(f"ALTER TABLE resumes ADD COLUMN {col_name} {col_type}")
                except Exception:
                    pass

        conn.commit()


def save_resume(data: dict[str, Any]) -> bool:
    """Insert a parsed resume. Returns False when its file is already in the database."""
    columns = [
        "candidate_name", "email", "phone", "skills", "resume_file", "match_score",
        "recommendation", "upload_date", "resume_text", "education", "experience",
        "projects", "certificates", "linkedin", "github", "experience_years",
        "score_breakdown", "target_role"
    ]
    
    values = []
    for key in columns:
        val = data.get(key, "")
        if key in ("skills", "score_breakdown") and isinstance(val, (list, dict)):
            values.append(json.dumps(val))
        else:
            values.append(val)

    try:
        with get_connection() as conn:
            conn.execute(
                f"INSERT INTO resumes ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
                values
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def update_analysis(
    resume_id: int,
    score: float,
    recommendation: str,
    score_breakdown: dict[str, Any] | None = None,
    target_role: str = ""
) -> None:
    """Update resume evaluation scores and detailed match breakdown."""
    breakdown_json = json.dumps(score_breakdown or {})
    with get_connection() as conn:
        conn.execute(
            """UPDATE resumes 
               SET match_score=?, recommendation=?, score_breakdown=?, target_role=? 
               WHERE id=?""",
            (score, recommendation, breakdown_json, target_role, resume_id)
        )
        conn.commit()


def get_resumes(search: str = "", target_role: str = "") -> list[dict[str, Any]]:
    """Retrieve all resumes, optionally filtered by search keyword or target role."""
    query = "SELECT * FROM resumes WHERE 1=1"
    params: list[Any] = []

    if search.strip():
        term = f"%{search.strip()}%"
        query += " AND (candidate_name LIKE ? OR email LIKE ? OR skills LIKE ? OR resume_text LIKE ?)"
        params.extend([term, term, term, term])

    if target_role.strip() and target_role != "All Roles":
        query += " AND target_role = ?"
        params.append(target_role.strip())

    query += " ORDER BY match_score DESC, upload_date DESC"

    with get_connection() as conn:
        rows = [dict(row) for row in conn.execute(query, params).fetchall()]

    for row in rows:
        try:
            row["skills"] = json.loads(row.get("skills") or "[]")
        except (json.JSONDecodeError, TypeError):
            row["skills"] = []

        try:
            row["score_breakdown"] = json.loads(row.get("score_breakdown") or "{}")
        except (json.JSONDecodeError, TypeError):
            row["score_breakdown"] = {}

    return rows


def delete_resume(resume_id: int) -> None:
    """Delete a single candidate record by ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM resumes WHERE id=?", (resume_id,))
        conn.commit()


def clear_resumes() -> None:
    """Purge all resume records."""
    with get_connection() as conn:
        conn.execute("DELETE FROM resumes")
        conn.commit()


# ===================== Job Role Management =====================

def save_job_role(
    title: str,
    description: str,
    category: str = "Engineering",
    required_skills: list[str] | None = None,
    min_experience: int = 0
) -> bool:
    """Save or update a Job Role profile."""
    from datetime import datetime
    skills_json = json.dumps(required_skills or [])
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO job_roles (title, category, description, required_skills, min_experience, created_date)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(title) DO UPDATE SET
                   category=excluded.category,
                   description=excluded.description,
                   required_skills=excluded.required_skills,
                   min_experience=excluded.min_experience""",
                (title.strip(), category, description.strip(), skills_json, min_experience, date_str)
            )
            conn.commit()
        return True
    except Exception:
        return False


def get_job_roles() -> list[dict[str, Any]]:
    """Fetch all saved job roles."""
    with get_connection() as conn:
        rows = [dict(row) for row in conn.execute("SELECT * FROM job_roles ORDER BY id ASC").fetchall()]
    for row in rows:
        try:
            row["required_skills"] = json.loads(row.get("required_skills") or "[]")
        except (json.JSONDecodeError, TypeError):
            row["required_skills"] = []
    return rows


def delete_job_role(role_id: int) -> None:
    """Delete a job role by ID."""
    with get_connection() as conn:
        conn.execute("DELETE FROM job_roles WHERE id=?", (role_id,))
        conn.commit()
