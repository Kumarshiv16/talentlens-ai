"""Modern Plotly visual analytics and radar chart factories for TalentLens AI."""
from __future__ import annotations

from collections import Counter
from typing import Any
import plotly.express as px
import plotly.graph_objects as go

# Common dark layout configuration
THEME_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color="#e2e8f0"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def score_distribution(rows: list[dict[str, Any]]) -> go.Figure:
    """Donut chart depicting candidate evaluation breakdown."""
    labels = ["Excellent Match", "Shortlist", "Maybe", "Reject", "Not analyzed"]
    color_map = {
        "Excellent Match": "#10b981",  # Emerald
        "Shortlist": "#3b82f6",        # Blue
        "Maybe": "#f59e0b",            # Amber
        "Reject": "#ef4444",           # Rose/Red
        "Not analyzed": "#64748b"      # Slate
    }

    counts = {label: sum(r.get("recommendation") == label for r in rows) for label in labels}
    active_labels = [k for k, v in counts.items() if v > 0]
    active_values = [counts[k] for k in active_labels]
    active_colors = [color_map[k] for k in active_labels]

    if not active_values:
        active_labels = ["No Data"]
        active_values = [1]
        active_colors = ["#334155"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=active_labels,
                values=active_values,
                hole=0.62,
                marker=dict(colors=active_colors, line=dict(color="#0f172a", width=2)),
                textinfo="percent+label",
                hoverinfo="label+value+percent",
            )
        ]
    )
    fig.update_layout(
        **THEME_LAYOUT,
        title=dict(text="Candidate Suitability Distribution", font=dict(size=16, color="#f8fafc")),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    return fig


def score_bar(rows: list[dict[str, Any]]) -> go.Figure:
    """Horizontal ranked bar chart of candidate match scores."""
    sorted_rows = sorted(rows, key=lambda x: x.get("match_score", 0), reverse=True)[:15]
    names = [r["candidate_name"] for r in sorted_rows][::-1]
    scores = [r["match_score"] for r in sorted_rows][::-1]

    colors = []
    for s in scores:
        if s >= 85:
            colors.append("#10b981")
        elif s >= 70:
            colors.append("#3b82f6")
        elif s >= 50:
            colors.append("#f59e0b")
        else:
            colors.append("#ef4444")

    fig = go.Figure(
        data=[
            go.Bar(
                x=scores,
                y=names,
                orientation="h",
                marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.1)", width=1)),
                text=[f"{s:.1f}%" for s in scores],
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        **THEME_LAYOUT,
        title=dict(text="Top Candidates by Match Score", font=dict(size=16, color="#f8fafc")),
        xaxis=dict(range=[0, 105], title="Match Score (%)", gridcolor="#1e293b"),
        yaxis=dict(title="", gridcolor="rgba(0,0,0,0)"),
    )
    return fig


def top_skills(rows: list[dict[str, Any]]) -> go.Figure:
    """Frequency analysis of detected skills across candidates."""
    counts = Counter(skill for row in rows for skill in row.get("skills", []))
    items = counts.most_common(12)
    
    if not items:
        skills, freqs = ["No skills detected"], [0]
    else:
        skills = [x[0] for x in items][::-1]
        freqs = [x[1] for x in items][::-1]

    fig = go.Figure(
        data=[
            go.Bar(
                x=freqs,
                y=skills,
                orientation="h",
                marker=dict(
                    color=freqs,
                    colorscale="Tealgrn",
                    line=dict(color="rgba(255,255,255,0.1)", width=1)
                ),
                text=freqs,
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        **THEME_LAYOUT,
        title=dict(text="Most Prevalent Skills in Candidate Pool", font=dict(size=16, color="#f8fafc")),
        xaxis=dict(title="Candidate Count", gridcolor="#1e293b", dtick=1),
        yaxis=dict(title="", gridcolor="rgba(0,0,0,0)"),
    )
    return fig


def candidate_radar_chart(candidate: dict[str, Any]) -> go.Figure:
    """Spider / Radar chart showing multidimensional candidate strength."""
    breakdown = candidate.get("score_breakdown", {})
    categories = ["Skill Match", "Semantic Relevancy", "Context & Keywords", "Profile Completeness", "Overall Fit"]
    
    skill_score = breakdown.get("skill_match_score", candidate.get("match_score", 60))
    semantic_score = breakdown.get("semantic_score", candidate.get("match_score", 50))
    context_score = breakdown.get("context_score", candidate.get("match_score", 55))
    
    # Completeness heuristic based on filled fields
    fields = [candidate.get("education"), candidate.get("experience"), candidate.get("projects"), candidate.get("skills")]
    completeness = (sum(1 for f in fields if f and f != "Not detected") / len(fields)) * 100
    overall = candidate.get("match_score", 0)

    values = [skill_score, semantic_score, context_score, completeness, overall]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(59, 130, 246, 0.25)",
            line=dict(color="#38bdf8", width=2),
            name=candidate.get("candidate_name", "Candidate")
        )
    )
    fig.update_layout(
        **THEME_LAYOUT,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e293b", color="#94a3b8"),
            angularaxis=dict(gridcolor="#1e293b", color="#e2e8f0"),
            bgcolor="rgba(15, 23, 42, 0.6)"
        ),
        title=dict(text="Competency Breakdown Radar", font=dict(size=15, color="#f8fafc")),
        showlegend=False,
    )
    return fig


def comparison_bar_chart(candidates: list[dict[str, Any]]) -> go.Figure:
    """Grouped bar chart for side-by-side comparison."""
    categories = ["Overall Match", "Skill Score", "Semantic Similarity", "Context Score"]
    fig = go.Figure()

    palette = ["#38bdf8", "#34d399", "#f472b6", "#fbbf24"]

    for idx, cand in enumerate(candidates):
        bd = cand.get("score_breakdown", {})
        vals = [
            cand.get("match_score", 0),
            bd.get("skill_match_score", cand.get("match_score", 0)),
            bd.get("semantic_score", cand.get("match_score", 0)),
            bd.get("context_score", cand.get("match_score", 0)),
        ]
        color = palette[idx % len(palette)]
        fig.add_trace(
            go.Bar(
                name=cand.get("candidate_name", f"Candidate {idx+1}"),
                x=categories,
                y=vals,
                marker_color=color
            )
        )

    fig.update_layout(
        **THEME_LAYOUT,
        barmode="group",
        title=dict(text="Side-by-Side Factor Comparison", font=dict(size=16, color="#f8fafc")),
        yaxis=dict(range=[0, 105], title="Score (%)", gridcolor="#1e293b"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    return fig

