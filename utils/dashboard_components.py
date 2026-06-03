"""
Recruiter Dashboard UI Components for Streamlit.
Defines premium custom styled cards, timelines, and skill chips using responsive HSL variables.
"""

import streamlit as st
from typing import Dict, Any, List, Optional


def inject_dashboard_styles():
    """
    Injects custom, highly polished, and responsive CSS for the Recruiter Dashboard.
    Uses Streamlit's theme variables to support both Light and Dark modes seamlessly.
    """
    st.markdown(
        """
        <style>
        /* Modern recruiter dashboard typography & layout */
        .recruiter-dashboard {
            margin-top: 10px;
            font-family: inherit;
        }
        
        /* Grid container for metric cards */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        /* Premium Card style with glassmorphic accents */
        .recruiter-card {
            background-color: var(--secondary-background-color, #f0f2f6);
            color: var(--text-color, #31333F);
            border-radius: 16px;
            padding: 22px;
            border: 1px solid rgba(49, 51, 63, 0.12);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        /* Color-coded accent bars for cards */
        .recruiter-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--primary-color, #FF4B4B);
            opacity: 0.8;
        }
        
        .recruiter-card.card-ats::before {
            background: linear-gradient(180deg, #10B981, #059669); /* Green */
        }
        
        .recruiter-card.card-jd::before {
            background: linear-gradient(180deg, #3B82F6, #1D4ED8); /* Blue */
        }
        
        .recruiter-card.card-skills::before {
            background: linear-gradient(180deg, #8B5CF6, #6D28D9); /* Purple */
        }
        
        .recruiter-card.card-exp::before {
            background: linear-gradient(180deg, #F59E0B, #B45309); /* Amber */
        }
        
        .recruiter-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            border-color: rgba(49, 51, 63, 0.25);
        }
        
        .card-header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .card-title-text {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.7;
        }
        
        .card-icon {
            font-size: 1.2rem;
        }
        
        .card-value-display {
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 6px;
            letter-spacing: -0.02em;
        }
        
        .card-subtitle-display {
            font-size: 0.825rem;
            font-weight: 500;
            opacity: 0.85;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        /* Modern chip badges for skills */
        .skills-badge-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
            margin-bottom: 15px;
        }
        
        .chip-badge {
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.01em;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            border: 1px solid rgba(128, 128, 128, 0.15);
            transition: all 0.2s ease;
        }
        
        .chip-badge:hover {
            transform: scale(1.03);
        }
        
        .chip-badge.badge-match {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10B981;
            border-color: rgba(16, 185, 129, 0.25);
        }
        
        .chip-badge.badge-gap {
            background-color: rgba(239, 68, 68, 0.1);
            color: #EF4444;
            border-color: rgba(239, 68, 68, 0.25);
        }
        
        .chip-badge.badge-normal {
            background-color: rgba(59, 130, 246, 0.1);
            color: #3B82F6;
            border-color: rgba(59, 130, 246, 0.25);
        }
        
        /* Timeline component styles */
        .timeline-container {
            position: relative;
            padding-left: 20px;
            margin-top: 15px;
        }
        
        .timeline-container::before {
            content: '';
            position: absolute;
            top: 5px;
            left: 4px;
            width: 2px;
            height: calc(100% - 20px);
            background-color: rgba(49, 51, 63, 0.12);
        }
        
        .timeline-node {
            position: relative;
            padding-bottom: 22px;
        }
        
        .timeline-node::before {
            content: '';
            position: absolute;
            left: -20px;
            top: 5px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: var(--primary-color, #FF4B4B);
            border: 2px solid var(--background-color, #ffffff);
            box-shadow: 0 0 0 3px rgba(255, 75, 75, 0.15);
        }
        
        .timeline-role-text {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 2px;
        }
        
        .timeline-meta-text {
            font-size: 0.825rem;
            opacity: 0.8;
            margin-bottom: 8px;
            font-weight: 500;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .timeline-bullet {
            font-size: 0.85rem;
            margin-left: 10px;
            margin-bottom: 4px;
            line-height: 1.4;
            opacity: 0.9;
        }
        
        /* Recruiter Executive Summary container */
        .exec-summary-box {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.04) 0%, rgba(139, 92, 246, 0.04) 100%);
            border-left: 4px solid #3B82F6;
            border-radius: 4px 12px 12px 4px;
            padding: 20px;
            margin-bottom: 25px;
            border-top: 1px solid rgba(59, 130, 246, 0.08);
            border-right: 1px solid rgba(59, 130, 246, 0.08);
            border-bottom: 1px solid rgba(59, 130, 246, 0.08);
        }
        
        .exec-summary-title {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #3B82F6;
            margin-bottom: 8px;
        }
        
        .exec-summary-text {
            font-size: 0.95rem;
            line-height: 1.5;
            font-style: italic;
        }

        /* Leaderboard table styles */
        .leaderboard-container {
            width: 100%;
            overflow-x: auto;
            margin-top: 10px;
            margin-bottom: 30px;
            border-radius: 12px;
            border: 1px solid rgba(49, 51, 63, 0.12);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        
        .leaderboard-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }
        
        .leaderboard-table th {
            background-color: var(--secondary-background-color, #f0f2f6);
            color: var(--text-color, #31333F);
            font-weight: 700;
            padding: 14px 18px;
            border-bottom: 2px solid rgba(49, 51, 63, 0.15);
            text-transform: uppercase;
            font-size: 0.725rem;
            letter-spacing: 0.05em;
        }
        
        .leaderboard-table td {
            padding: 14px 18px;
            border-bottom: 1px solid rgba(49, 51, 63, 0.08);
            color: var(--text-color, #31333F);
            font-weight: 500;
            vertical-align: middle;
        }
        
        .leaderboard-table tr:hover {
            background-color: rgba(49, 51, 63, 0.03);
        }
        
        /* Rank and Score Pill Styling */
        .rank-cell-display {
            font-weight: 800 !important;
            font-size: 1.05rem;
        }
        
        .leaderboard-pill {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            text-align: center;
        }
        
        .leaderboard-pill.pill-overall {
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            color: white;
            box-shadow: 0 2px 6px rgba(59, 130, 246, 0.25);
        }
        
        .leaderboard-pill.pill-ats {
            background-color: rgba(16, 185, 129, 0.12);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        /* Mini progress bar cell */
        .mini-progress-container {
            width: 100px;
            background-color: rgba(49, 51, 63, 0.1);
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }
        
        .mini-progress-bar {
            height: 100%;
            border-radius: 4px;
        }
        
        .mini-progress-bar.bar-jd {
            background-color: #3B82F6;
        }
        
        .mini-progress-bar.bar-semantic {
            background-color: #8B5CF6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(title: str, value: str, subtitle: str, icon: str, color_class: str):
    """
    Renders a single recruiter dashboard metric card.
    
    Args:
        title: Title of the card
        value: Major metric value (e.g. 85%)
        subtitle: Quick contextual description
        icon: Emoji representation of the card
        color_class: Class identifier for theme color ('card-ats', 'card-jd', 'card-skills', 'card-exp')
    """
    st.markdown(
        f"""
        <div class="recruiter-card {color_class}">
            <div class="card-header-row">
                <span class="card-title-text">{title}</span>
                <span class="card-icon">{icon}</span>
            </div>
            <div class="card-value-display">{value}</div>
            <div class="card-subtitle-display">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_skills_badges(title: str, skills: List[str], badge_type: str = "normal"):
    """
    Renders a clean and visually appealing horizontal list of skill badges.
    
    Args:
        title: Title of the badge cluster
        skills: List of skills to display
        badge_type: 'match' (green), 'gap' (red), or 'normal' (blue)
    """
    if not skills:
        st.markdown(f"**{title}**: *None identified*")
        return

    st.markdown(f"**{title} ({len(skills)})**")
    
    cls_map = {
        "match": "badge-match",
        "gap": "badge-gap",
        "normal": "badge-normal"
    }
    badge_class = cls_map.get(badge_type, "badge-normal")
    icon_map = {
        "match": "✓",
        "gap": "⚡",
        "normal": "⚙️"
    }
    badge_icon = icon_map.get(badge_type, "")

    badges_html = "".join([
        f'<span class="chip-badge {badge_class}">{badge_icon} {s}</span>'
        for s in skills
    ])
    
    st.markdown(
        f'<div class="skills-badge-list">{badges_html}</div>',
        unsafe_allow_html=True
    )


def render_experience_timeline(experience_list: List[Dict[str, Any]]):
    """
    Renders work experience as a clean, vertical chronological timeline.
    
    Args:
        experience_list: List of experience dictionary items
    """
    if not experience_list:
        st.markdown("*No experience timeline recorded.*")
        return

    timeline_html = '<div class="timeline-container">'
    
    for exp in experience_list:
        role = exp.get("role", "Professional Role")
        company = exp.get("company", "Organization")
        duration = exp.get("duration", "N/A")
        
        timeline_html += f"""
        <div class="timeline-node">
            <div class="timeline-role-text">{role}</div>
            <div class="timeline-meta-text">
                <span style="color: #3B82F6; font-weight:600;">🏢 {company}</span>
                <span style="opacity: 0.7;">📅 {duration}</span>
            </div>
        """
        
        responsibilities = exp.get("responsibilities", [])
        if responsibilities:
            for resp in responsibilities[:3]:  # Show top 3 responsibilities to keep visual clarity
                timeline_html += f'<div class="timeline-bullet">• {resp}</div>'
                
        timeline_html += "</div>"
        
    timeline_html += "</div>"
    st.markdown(timeline_html, unsafe_allow_html=True)


def calculate_experience_tenure(parsed_data_or_list: Any) -> str:
    """
    Attempts to calculate total tenure strictly based on candidate professional employment history.
    Does not include internships in the tenure calculation.
    """
    if not parsed_data_or_list:
        return "Not Available"
        
    employment_list = []
    internship_list = []
    
    if isinstance(parsed_data_or_list, dict):
        # We strictly compute years from professional employment / experience records, NOT internships
        if isinstance(parsed_data_or_list.get("employment"), list):
            employment_list = parsed_data_or_list["employment"]
        elif isinstance(parsed_data_or_list.get("experience"), list):
            employment_list = parsed_data_or_list["experience"]
            
        if isinstance(parsed_data_or_list.get("internships"), list):
            internship_list = parsed_data_or_list["internships"]
    elif isinstance(parsed_data_or_list, list):
        employment_list = parsed_data_or_list
    else:
        return "Not Available"
        
    # Check if ONLY internships exist
    if not employment_list and internship_list:
        return "Internship Experience Only"
        
    if not employment_list:
        return "Not Available"
        
    import re
    total_years = 0.0
    has_valid_duration = False
    
    for emp in employment_list:
        if not isinstance(emp, dict):
            continue
        duration = emp.get("duration", "")
        if not duration or duration == "N/A" or duration.strip() == "":
            continue
            
        # Parse common formats: "X years", "Y months", "X yrs", "2019 - 2022"
        # Look for explicit year patterns first
        year_matches = re.findall(r'\b(20\d{2}|19\d{2})\b', duration)
        if len(year_matches) == 2:
            try:
                start = int(year_matches[0])
                end = int(year_matches[1])
                diff = abs(end - start)
                total_years += diff if diff > 0 else 0.5
                has_valid_duration = True
                continue
            except ValueError:
                pass
                
        # Look for "X years" or "X yrs"
        years_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:yr|year)', duration, re.IGNORECASE)
        if years_match:
            try:
                total_years += float(years_match.group(1))
                has_valid_duration = True
                continue
            except ValueError:
                pass
                
        # Look for "X months"
        months_match = re.search(r'(\d+)\s*(?:mo|month)', duration, re.IGNORECASE)
        if months_match:
            try:
                total_years += float(months_match.group(1)) / 12.0
                has_valid_duration = True
            except ValueError:
                pass
                
    if not has_valid_duration:
        # If all employment dates/durations are missing/unparseable, return "Not Available"
        return "Not Available"
        
    if total_years > 0:
        years_int = int(total_years)
        months_int = int((total_years - years_int) * 12)
        if years_int > 0:
            return f"{years_int}+ Years" if months_int < 3 else f"{years_int}.{int(months_int/1.2)} Years"
        else:
            return f"{months_int} Months"
            
    return "Not Available"


def render_recruiter_dashboard(
    parsed_data: Dict[str, Any],
    ats_score: int,
    jd_match_score: int,
    match_details: Dict[str, Any],
    skill_gaps: List[str],
    resume_text: str,
    jd_text: Optional[str] = None
):
    """
    Renders the complete visual Recruiter Dashboard on Streamlit.
    
    Args:
        parsed_data: Output of parsed resume json
        ats_score: 0-100 calculated ATS score
        jd_match_score: 0-100 hybrid match score
        match_details: Keyword and semantic breakdown
        skill_gaps: Missing tech requirements
        resume_text: Raw resume context
        jd_text: Optional job description text
    """
    inject_dashboard_styles()
    
    st.markdown('<div class="recruiter-dashboard">', unsafe_allow_html=True)
    
    # 1. RUN SEMANTIC SKILL GAP ANALYSIS
    semantic_gaps = {
        "matched_skills": [],
        "missing_skills": [],
        "recommended_skills": [],
        "match_percentage": 0
    }
    
    if jd_text and jd_text.strip():
        from services.skill_gap_analyzer import analyze_skill_gaps
        # Run our semantic matching module
        semantic_gaps = analyze_skill_gaps(parsed_data.get("skills", {}), jd_text)
        
    # 2. GENERATE RECRUITER EXECUTIVE SUMMARY
    from services.llm_parser import generate_recruiter_summary
    
    # Retrieve executive summary (cached/stored in state to avoid redundant calls)
    summary_key = f"recruiter_sum_{parsed_data.get('name', '')}"
    if summary_key not in st.session_state:
        with st.spinner("🧠 Generating Candidate Executive Profile..."):
            st.session_state[summary_key] = generate_recruiter_summary(parsed_data)
            
    exec_summary = st.session_state[summary_key]
    
    # 3. METRICS ROW
    col1, col2, col3, col4 = st.columns(4)
    
    # ATS Card
    from services.ats_scorer import get_ats_interpretation
    ats_interp = get_ats_interpretation(ats_score).split(" - ")[0]
    with col1:
        render_metric_card(
            title="ATS Compatibility",
            value=f"{ats_score}/100",
            subtitle=f"🎯 {ats_interp}",
            icon="🎯",
            color_class="card-ats"
        )
        
    # JD Match Card
    if jd_text and jd_text.strip():
        from services.jd_matcher import get_jd_match_interpretation
        jd_interp = get_jd_match_interpretation(jd_match_score).split(" - ")[0]
        jd_value = f"{jd_match_score}%"
        jd_sub = f"💼 {jd_interp}"
    else:
        jd_value = "N/A"
        jd_sub = "💡 Job description missing"
        
    with col2:
        render_metric_card(
            title="JD Alignment",
            value=jd_value,
            subtitle=jd_sub,
            icon="💼",
            color_class="card-jd"
        )
        
    # Skills Match Percentage (Using Semantic Matching!)
    if jd_text and jd_text.strip():
        skills_value = f"{semantic_gaps['match_percentage']}%"
        skills_sub = f"🛠️ {len(semantic_gaps['matched_skills'])} matched requirements"
    else:
        # Sum total parsed skills
        skills_data = parsed_data.get("skills", [])
        if isinstance(skills_data, list):
            total_skills = len(skills_data)
        elif isinstance(skills_data, dict):
            total_skills = sum(
                len(v) if isinstance(v, list) else 0 
                for v in skills_data.values()
            )
        else:
            total_skills = 0
        skills_value = str(total_skills)
        skills_sub = "🛠️ Extracted skills"
        
    with col3:
        render_metric_card(
            title="Skills Match",
            value=skills_value,
            subtitle=skills_sub,
            icon="🛠️",
            color_class="card-skills"
        )
        
    # Experience Level Card
    tenure = calculate_experience_tenure(parsed_data)
    
    employment_list = parsed_data.get("employment", [])
    internship_list = parsed_data.get("internships", [])
    experience_list = parsed_data.get("experience", [])
    
    latest_role = "Professional"
    if employment_list and isinstance(employment_list, list) and len(employment_list) > 0:
        latest_role = employment_list[0].get("role", "Professional")
    elif internship_list and isinstance(internship_list, list) and len(internship_list) > 0:
        latest_role = internship_list[0].get("role", "Professional")
    elif experience_list and isinstance(experience_list, list) and len(experience_list) > 0:
        latest_role = experience_list[0].get("role", "Professional")
        
    if len(latest_role) > 20:
        latest_role = latest_role[:17] + "..."
        
    with col4:
        render_metric_card(
            title="Experience Profile",
            value=tenure,
            subtitle=f"👤 {latest_role}",
            icon="👤",
            color_class="card-exp"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. LOWER SECTION (EXECUTIVE PROFILE + EXPERIENCE AND SKILLS GRID)
    sec_col1, sec_col2 = st.columns([1.1, 0.9])
    
    with sec_col1:
        st.subheader("📋 Candidate Profile & Summary")
        
        # Executive Summary Box
        st.markdown(
            f"""
            <div class="exec-summary-box">
                <div class="exec-summary-title">Recruiter Executive Summary</div>
                <div class="exec-summary-text">"{exec_summary}"</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Experience Timeline
        st.subheader("⏳ Chronological Work History")
        
        has_any_exp = False
        if employment_list and isinstance(employment_list, list) and len(employment_list) > 0:
            st.markdown("**Professional Experience**")
            render_experience_timeline(employment_list)
            has_any_exp = True
            
        if internship_list and isinstance(internship_list, list) and len(internship_list) > 0:
            st.markdown("**Internships**")
            render_experience_timeline(internship_list)
            has_any_exp = True
            
        if not has_any_exp and experience_list and isinstance(experience_list, list) and len(experience_list) > 0:
            render_experience_timeline(experience_list)
            has_any_exp = True
            
        if not has_any_exp:
            st.markdown("*No experience timeline recorded.*")
        
    with sec_col2:
        st.subheader("🛠️ Technical Alignment Analysis")
        
        if jd_text and jd_text.strip():
            # Keyword and Semantic Breakdown
            st.markdown("**Core Match Breakdown**")
            break_col1, break_col2 = st.columns(2)
            with break_col1:
                st.metric("Keyword Match Score", f"{match_details.get('keyword_score', 0)}%", help="Exact skill overlapping")
            with break_col2:
                # Use the semantic percentage from the new skill gap analyzer
                st.metric("Semantic Fit Score", f"{semantic_gaps['match_percentage']}%", help="Conceptual and job relevance overlap")
                
            st.divider()
            
            # Skills Badging (Matched - extracted from semantic matches)
            matched_names = [m["jd_skill"] for m in semantic_gaps["matched_skills"]]
            render_skills_badges(
                title="Matched Core Requirements",
                skills=matched_names,
                badge_type="match"
            )
            
            # Skills Badging (Missing / Gaps - extracted from semantic missing skills)
            render_skills_badges(
                title="Missing Tech Requirements (Skill Gaps)",
                skills=semantic_gaps["missing_skills"],
                badge_type="gap"
            )
            
            # Upskilling Recommendations
            if semantic_gaps.get("recommended_skills"):
                st.divider()
                st.markdown("**📚 Recommended Upskilling Pathways**")
                st.caption("Custom learning recommendations tailored to the identified skill gaps:")
                
                for rec in semantic_gaps["recommended_skills"]:
                    with st.expander(f"📖 Study Pathway: {rec['skill']}"):
                        st.markdown(f"**Recommended Path:**\n{rec['pathway']}")
                        st.markdown(f"🔗 [Official Documentation & Tutorials]({rec['resource_url']})")
        else:
            st.info("💡 Provide a job description on the side inputs to unlock deep skill gap analysis, semantic matchmaking, and JD alignment scores!")
            
            # Render regular parsed skills
            skills_dict = parsed_data.get("skills", [])
            if isinstance(skills_dict, list):
                render_skills_badges(
                    title="Extracted Skills",
                    skills=skills_dict,
                    badge_type="normal"
                )
            elif isinstance(skills_dict, dict):
                for cat, s_list in skills_dict.items():
                    if s_list:
                        render_skills_badges(
                            title=cat.replace("_", " ").title(),
                            skills=s_list,
                            badge_type="normal"
                        )
                    
        # Missing ATS Elements Warning
        from services.ats_scorer import get_missing_ats_elements
        missing_ats = get_missing_ats_elements(parsed_data)
        if missing_ats:
            st.divider()
            st.markdown("**⚠️ Missing ATS Compatibility Elements**")
            st.warning(", ".join(missing_ats))
            
    st.markdown('</div>', unsafe_allow_html=True)


def render_bulk_leaderboard(ranked_candidates: List[Any]):
    """
    Renders a stunning, enterprise-grade Leaderboard Table for recruiters.
    Features:
    - Glowing overall score pills.
    - Mini inline progress bars for JD Alignment and Semantic Similarity.
    - Styled ranking markers (🥇, 🥈, 🥉 medals for top 3).
    - Summary metrics cards at the top.
    """
    inject_dashboard_styles()
    
    if not ranked_candidates:
        st.warning("⚠️ No candidate scores available to display.")
        return

    # 1. SUMMARY CARDS
    total_candidates = len(ranked_candidates)
    top_candidate = ranked_candidates[0]
    avg_ats = sum(c.ats_score for c in ranked_candidates) / total_candidates
    avg_overall = sum(c.overall_score for c in ranked_candidates) / total_candidates

    st.markdown("### 🏆 Candidate Comparison Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            title="Total Evaluated",
            value=str(total_candidates),
            subtitle="👤 Candidates analyzed",
            icon="👥",
            color_class="card-exp"
        )
    with col2:
        render_metric_card(
            title="Top Rank",
            value=f"{top_candidate.overall_score:.1f}%",
            subtitle=f"👑 {top_candidate.name}",
            icon="👑",
            color_class="card-ats"
        )
    with col3:
        render_metric_card(
            title="Average ATS Score",
            value=f"{avg_ats:.1f}/100",
            subtitle="🎯 Batch profile structure",
            icon="🎯",
            color_class="card-jd"
        )
    with col4:
        render_metric_card(
            title="Average Overall Score",
            value=f"{avg_overall:.1f}%",
            subtitle="⚖️ Weighted benchmark",
            icon="⚖️",
            color_class="card-skills"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Interactive Leaderboard Table")

    # 2. HTML TABLE GENERATION
    table_html = """<div class="leaderboard-container">
<table class="leaderboard-table">
<thead>
<tr>
<th>Rank</th>
<th>Name</th>
<th>Email</th>
<th>Overall Score</th>
<th>ATS Score</th>
<th>Skills Match</th>
<th>Semantic Fit</th>
</tr>
</thead>
<tbody>"""

    for rank, candidate in enumerate(ranked_candidates, 1):
        # Medal emoji for top 3
        rank_icon = ""
        if rank == 1:
            rank_icon = "🥇"
        elif rank == 2:
            rank_icon = "🥈"
        elif rank == 3:
            rank_icon = "🥉"
        else:
            rank_icon = f"#{rank}"

        overall_percent = f"{candidate.overall_score:.1f}%"
        ats_val = f"{candidate.ats_score}/100"
        
        # JD alignment and semantic similarity percentages
        jd_match = candidate.combined_jd_match
        semantic_match = int(candidate.semantic_match * 100)

        # Progress bar colors and widths
        jd_bar_width = min(max(jd_match, 0), 100)
        sem_bar_width = min(max(semantic_match, 0), 100)

        table_html += f"""<tr>
<td>
<div class="rank-cell-display">{rank_icon}</div>
</td>
<td style="font-weight: 700;">{candidate.name}</td>
<td style="opacity: 0.85; font-size: 0.85rem;">{candidate.email}</td>
<td>
<span class="leaderboard-pill pill-overall">{overall_percent}</span>
</td>
<td>
<span class="leaderboard-pill pill-ats">{ats_val}</span>
</td>
<td>
<div class="mini-progress-container">
<div class="mini-progress-bar bar-jd" style="width: {jd_bar_width}%;"></div>
</div>
<span style="font-size: 0.85rem; font-weight: 700;">{jd_match}%</span>
</td>
<td>
<div class="mini-progress-container">
<div class="mini-progress-bar bar-semantic" style="width: {sem_bar_width}%;"></div>
</div>
<span style="font-size: 0.85rem; font-weight: 700; color: #8B5CF6;">{semantic_match}%</span>
</td>
</tr>"""

    table_html += """</tbody>
</table>
</div>"""

    st.markdown(table_html, unsafe_allow_html=True)
