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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* Modern recruiter dashboard typography & layout */
        .recruiter-dashboard {
            margin-top: 15px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        /* Executive Summary Grid & Cards */
        .exec-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .exec-card {
            background-color: var(--secondary-background-color, rgba(240, 242, 246, 0.45));
            border: 1px solid rgba(49, 51, 63, 0.08);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.01);
            transition: all 0.3s ease;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }
        .exec-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            border-color: rgba(49, 51, 63, 0.15);
        }
        .exec-card-title {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: gray;
            margin-bottom: 6px;
        }
        .exec-card-value {
            font-size: 1.0rem;
            font-weight: 800;
            color: var(--text-color, #1F2937);
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
            background-color: var(--secondary-background-color, rgba(240, 242, 246, 0.65));
            color: var(--text-color, #1F2937);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(49, 51, 63, 0.08);
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }
        
        /* Color-coded accent bars for cards */
        .recruiter-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            background: var(--primary-color, #0052e0);
            opacity: 0.9;
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
            transform: translateY(-6px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
            border-color: rgba(49, 51, 63, 0.2);
            background-color: var(--secondary-background-color, rgba(240, 242, 246, 0.85));
        }
        
        .card-header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .card-title-text {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.75;
        }
        
        .card-icon {
            font-size: 1.3rem;
            opacity: 0.9;
        }
        
        .card-value-display {
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1.05;
            margin-bottom: 8px;
            letter-spacing: -0.03em;
        }
        
        .card-subtitle-display {
            font-size: 0.85rem;
            font-weight: 500;
            opacity: 0.85;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        /* Modern chip badges for skills */
        .skills-badge-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
            margin-bottom: 18px;
        }
        
        .chip-badge {
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.01em;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: 1px solid rgba(128, 128, 128, 0.15);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .chip-badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        }
        
        .chip-badge.badge-match {
            background-color: rgba(16, 185, 129, 0.08);
            color: #10B981;
            border-color: rgba(16, 185, 129, 0.22);
        }
        
        .chip-badge.badge-gap {
            background-color: rgba(239, 68, 68, 0.08);
            color: #EF4444;
            border-color: rgba(239, 68, 68, 0.22);
        }
        
        .chip-badge.badge-normal {
            background-color: rgba(59, 130, 246, 0.08);
            color: #3B82F6;
            border-color: rgba(59, 130, 246, 0.22);
        }
        
        /* Timeline component styles */
        .timeline-container {
            position: relative;
            padding-left: 24px;
            margin-top: 20px;
        }
        
        .timeline-container::before {
            content: '';
            position: absolute;
            top: 5px;
            left: 5px;
            width: 2px;
            height: calc(100% - 20px);
            background-color: rgba(49, 51, 63, 0.12);
        }
        
        .timeline-node {
            position: relative;
            padding-bottom: 24px;
        }
        
        .timeline-node::before {
            content: '';
            position: absolute;
            left: -24px;
            top: 6px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: var(--primary-color, #0052e0);
            border: 2px solid var(--background-color, #ffffff);
            box-shadow: 0 0 0 3px rgba(0, 82, 224, 0.15);
            animation: pulse 2.5s infinite;
        }
        
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(0, 82, 224, 0.4);
            }
            70% {
                box-shadow: 0 0 0 6px rgba(0, 82, 224, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(0, 82, 224, 0);
            }
        }
        
        .timeline-role-text {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 3px;
            color: var(--text-color, #1F2937);
        }
        
        .timeline-meta-text {
            font-size: 0.85rem;
            opacity: 0.85;
            margin-bottom: 10px;
            font-weight: 500;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }
        
        .timeline-bullet {
            font-size: 0.88rem;
            margin-left: 12px;
            margin-bottom: 6px;
            line-height: 1.5;
            opacity: 0.9;
        }
        
        /* Recruiter Executive Summary container */
        .exec-summary-box {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            border-left: 4px solid #3B82F6;
            border-radius: 4px 16px 16px 4px;
            padding: 22px;
            margin-bottom: 28px;
            border-top: 1px solid rgba(59, 130, 246, 0.08);
            border-right: 1px solid rgba(59, 130, 246, 0.08);
            border-bottom: 1px solid rgba(59, 130, 246, 0.08);
            box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
        }
        
        .exec-summary-title {
            font-size: 0.88rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #3B82F6;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .exec-summary-text {
            font-size: 0.98rem;
            line-height: 1.55;
            font-style: italic;
            color: var(--text-color, #374151);
        }

        /* Leaderboard table styles */
        .leaderboard-container {
            width: 100%;
            overflow-x: auto;
            margin-top: 15px;
            margin-bottom: 35px;
            border-radius: 16px;
            border: 1px solid rgba(49, 51, 63, 0.08);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
            backdrop-filter: blur(10px);
        }
        
        .leaderboard-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.92rem;
        }
        
        .leaderboard-table th {
            background-color: var(--secondary-background-color, rgba(240, 242, 246, 0.7));
            color: var(--text-color, #1F2937);
            font-weight: 700;
            padding: 16px 20px;
            border-bottom: 2px solid rgba(49, 51, 63, 0.12);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
        }
        
        .leaderboard-table td {
            padding: 16px 20px;
            border-bottom: 1px solid rgba(49, 51, 63, 0.06);
            color: var(--text-color, #374151);
            font-weight: 500;
            vertical-align: middle;
        }
        
        .leaderboard-table tr:hover {
            background-color: rgba(49, 51, 63, 0.02);
        }
        
        /* Rank and Score Pill Styling */
        .rank-cell-display {
            font-weight: 800 !important;
            font-size: 1.1rem;
            color: var(--text-color, #111827);
        }
        
        .leaderboard-pill {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 700;
            text-align: center;
        }
        
        .leaderboard-pill.pill-overall {
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            color: white;
            box-shadow: 0 3px 10px rgba(59, 130, 246, 0.22);
        }
        
        .leaderboard-pill.pill-ats {
            background-color: rgba(16, 185, 129, 0.08);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.18);
        }
        
        /* Mini progress bar cell */
        .mini-progress-container {
            width: 100px;
            background-color: rgba(49, 51, 63, 0.08);
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }
        
        .mini-progress-bar {
            height: 100%;
            border-radius: 6px;
        }
        
        .mini-progress-bar.bar-jd {
            background: linear-gradient(90deg, #3B82F6, #60A5FA);
        }
        
        .mini-progress-bar.bar-semantic {
            background: linear-gradient(90deg, #8B5CF6, #A78BFA);
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(title: str, value: str, subtitle: str, icon: str, color_class: str, help_text: str = ""):
    """
    Renders a single recruiter dashboard metric card.
    
    Args:
        title: Title of the card
        value: Major metric value (e.g. 85%)
        subtitle: Quick contextual description
        icon: Emoji representation of the card
        color_class: Class identifier for theme color ('card-ats', 'card-jd', 'card-skills', 'card-exp')
        help_text: Tooltip explanation
    """
    tooltip_attr = f'title="{help_text}"' if help_text else ''
    title_suffix = ' ℹ️' if help_text else ''
    st.markdown(
        f"""
        <div class="recruiter-card {color_class}">
            <div class="card-header-row">
                <span class="card-title-text" {tooltip_attr} style="cursor: help;">{title}{title_suffix}</span>
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


def calculate_experience_tenure_with_source(parsed_data_or_list: Any) -> tuple[str, str]:
    """
    Calculates total experience tenure and lists the exact date ranges and calculations used.
    Does not include internships in the professional experience calculation.
    
    Returns:
        (tenure_str, calculation_source_str)
    """
    if not parsed_data_or_list:
        return "Not Found", "No experience data available."
        
    employment_list = []
    internship_list = []
    
    if isinstance(parsed_data_or_list, dict):
        # We strictly compute years from professional employment / experience records, NOT internships
        if isinstance(parsed_data_or_list.get("work_experience"), list) and parsed_data_or_list["work_experience"]:
            employment_list = parsed_data_or_list["work_experience"]
        elif isinstance(parsed_data_or_list.get("employment"), list) and parsed_data_or_list["employment"]:
            employment_list = parsed_data_or_list["employment"]
        elif isinstance(parsed_data_or_list.get("experience"), list) and parsed_data_or_list["experience"]:
            employment_list = parsed_data_or_list["experience"]
            
        if isinstance(parsed_data_or_list.get("internships"), list):
            internship_list = parsed_data_or_list["internships"]
    elif isinstance(parsed_data_or_list, list):
        employment_list = parsed_data_or_list
    else:
        return "Not Found", "Invalid data format."
        
    if not employment_list and internship_list:
        return "Internship Experience", "Only internship experience found (excluded from professional tenure)."
        
    if not employment_list:
        return "Not Found", "No professional work experience records found."
        
    import re
    from typing import Optional
    
    def parse_date_to_month_year(date_str: str) -> Optional[tuple[int, int]]:
        date_str = date_str.strip().lower()
        if not date_str:
            return None
            
        months_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        # Search for a 4-digit year
        year_match = re.search(r'\b(20\d{2}|19\d{2})\b', date_str)
        if not year_match:
            return None
        year = int(year_match.group(1))
        
        # Search for month keyword
        month = 1
        for m_name, m_val in months_map.items():
            if m_name in date_str:
                month = m_val
                break
        else:
            # Check for numeric month MM/YYYY or YYYY-MM
            # Exclude the 4-digit year from the month search
            remainder = date_str.replace(str(year), '').strip()
            num_match = re.search(r'\b(0?[1-9]|1[0-2])\b', remainder)
            if num_match:
                month = int(num_match.group(1))
                
        return (month, year)
        
    total_months = 0
    calculation_details = []
    
    for emp in employment_list:
        if not isinstance(emp, dict):
            continue
        role = emp.get("role", "Role")
        company = emp.get("company", "Company")
        duration = emp.get("duration", "")
        if not duration or duration == "Not Found" or duration == "N/A" or not duration.strip():
            continue
            
        # Parse duration
        parts = []
        for sep in ['-', '–', '—', ' to ']:
            if sep in duration:
                p = duration.split(sep)
                if len(p) == 2:
                    parts = p
                    break
        else:
            # Fallback: maybe just year matches
            year_matches = re.findall(r'\b(20\d{2}|19\d{2})\b', duration)
            if len(year_matches) == 2:
                parts = [year_matches[0], year_matches[1]]
                
        if len(parts) == 2:
            start_str, end_str = parts[0].strip(), parts[1].strip()
            start_date = parse_date_to_month_year(start_str)
            
            if start_date:
                # If end is present/current/now, use June 2026 (local time 2026-06-03)
                if end_str.lower() in ['present', 'current', 'now', 'today']:
                    end_date = (6, 2026)
                    end_display = "Present (June 2026)"
                else:
                    end_date = parse_date_to_month_year(end_str)
                    end_display = end_str
                    
                if end_date:
                    start_m, start_y = start_date
                    end_m, end_y = end_date
                    
                    months = (end_y - start_y) * 12 + (end_m - start_m)
                    # Include boundary month
                    months = max(0, months + 1)
                    total_months += months
                    calculation_details.append(
                        f"• {role} at {company}: {start_str} to {end_display} ({months} months)"
                    )
                    continue
                    
        # Fallback to direct year/month search in text
        # If "X years" or "X yrs"
        years_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:yr|year)', duration, re.IGNORECASE)
        if years_match:
            try:
                yrs = float(years_match.group(1))
                m = int(yrs * 12)
                total_months += m
                calculation_details.append(f"• {role} at {company}: {duration} ({m} months)")
                continue
            except ValueError:
                pass
                
        # If "X months"
        months_match = re.search(r'(\d+)\s*(?:mo|month)', duration, re.IGNORECASE)
        if months_match:
            try:
                m = int(months_match.group(1))
                total_months += m
                calculation_details.append(f"• {role} at {company}: {duration} ({m} months)")
                continue
            except ValueError:
                pass
                
    if total_months == 0:
        return "Not Found", "No valid date ranges or durations could be parsed from the professional experience history."
        
    years = total_months / 12.0
    years_int = int(years)
    months_int = total_months % 12
    
    if years_int > 0:
        tenure_str = f"{years_int}.{months_int} Years" if months_int > 0 else f"{years_int} Years"
    else:
        tenure_str = f"{months_int} Months"
        
    source_str = "\n".join(calculation_details) + f"\nTotal: {total_months} months = {tenure_str}"
    return tenure_str, source_str


def calculate_experience_tenure(parsed_data_or_list: Any) -> str:
    """
    Attempts to calculate total tenure strictly based on candidate professional employment history.
    Does not include internships in the tenure calculation.
    """
    tenure, _ = calculate_experience_tenure_with_source(parsed_data_or_list)
    return tenure


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
    
    # Compute Executive summary details for TASK 1 & 6
    skills_percent = semantic_gaps.get("match_percentage", 0) if (jd_text and jd_text.strip()) else 75
    effective_jd_match = jd_match_score if (jd_text and jd_text.strip()) else 70
    overall_score = (ats_score * 0.3) + (effective_jd_match * 0.4) + (skills_percent * 0.3)
    
    # Stars & Assessment (Constructive Verdicts)
    if overall_score >= 85:
        rating = "★★★★★ Excellent Resume"
    elif overall_score >= 70:
        rating = "★★★★☆ Strong Profile"
    elif overall_score >= 50:
        rating = "★★★☆☆ Good AI Foundation"
    else:
        rating = "★★☆☆☆ Needs Tech Polish"
        
    # ATS Readiness
    ats_ready = "ATS Excellent" if ats_score >= 80 else ("ATS Proficient" if ats_score >= 60 else "Requires Formatting Polish")
    
    # JD Alignment
    if jd_text and jd_text.strip():
        jd_align = "Highly Aligned" if effective_jd_match >= 80 else ("Satisfactory Alignment" if effective_jd_match >= 60 else "Low Alignment")
    else:
        jd_align = "N/A - No JD Provided"
        
    # Technical Skill Coverage
    if jd_text and jd_text.strip():
        missing_skills = semantic_gaps.get("missing_skills", [])
        if skills_percent >= 80:
            skill_cov = "Excellent Coverage"
        elif skills_percent >= 60:
            skill_cov = "Satisfactory Coverage"
        elif missing_skills:
            skill_cov = f"Needs Polish in {missing_skills[0]}" if len(missing_skills[0]) < 18 else "Domain Gaps Identified"
        else:
            skill_cov = "Domain Gaps Identified"
    else:
        skill_cov = "Extracted Verified Skills"
        
    # Recruiter Recommendation (Constructive Guidance)
    if overall_score >= 85:
        rec_recommend = "Strongly Recommended"
    elif overall_score >= 70:
        rec_recommend = "Recommended for Interview"
    elif overall_score >= 50:
        rec_recommend = "Recommended with Upskilling"
    else:
        rec_recommend = "Suggest Domain Foundation"
        
    st.markdown("### 🏆 Recruiter Executive Summary")
    
    # Tooltip definitions explaining metrics for Task 3 & 4
    rating_help = "Overall Rating represents the weighted combination of formatting quality (30%), semantic job match (40%), and keyword skill coverage (30%)."
    ats_help = "ATS Readiness indicates formatting compliance and structural parsing compatibility. It measures layout factors rather than direct skill matches."
    jd_help = "JD Alignment measures the semantic and conceptual similarity between the candidate experience and the target JD text, using Cosine similarity embeddings."
    skill_help = "Technical Skill Coverage calculates the percentage of exact and synonym matched skill keywords extracted from the JD against the resume text."
    rec_help = "Recommendation is the derived action pathway based on overall alignment, providing a constructive recruiter guide for candidates."

    # Custom styled HTML grid for Task 1, 3, & 4
    st.markdown(
        f"""
        <div class="exec-card-grid">
            <div class="exec-card" title="{rating_help}" style="cursor: help;">
                <div class="exec-card-title">Overall Rating ℹ️</div>
                <div class="exec-card-value" style="color: #F59E0B;">{rating}</div>
            </div>
            <div class="exec-card" title="{ats_help}" style="cursor: help;">
                <div class="exec-card-title">ATS Readiness ℹ️</div>
                <div class="exec-card-value" style="color: #10B981;">{ats_ready}</div>
            </div>
            <div class="exec-card" title="{jd_help}" style="cursor: help;">
                <div class="exec-card-title">JD Alignment ℹ️</div>
                <div class="exec-card-value" style="color: #3B82F6;">{jd_align}</div>
            </div>
            <div class="exec-card" title="{skill_help}" style="cursor: help;">
                <div class="exec-card-title">Technical Skill Coverage ℹ️</div>
                <div class="exec-card-value" style="color: #8B5CF6;">{skill_cov}</div>
            </div>
            <div class="exec-card" title="{rec_help}" style="cursor: help;">
                <div class="exec-card-title">Recommendation ℹ️</div>
                <div class="exec-card-value" style="color: #EF4444;">{rec_recommend}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 3. METRICS ROW (Renamed for TASK 2)
    col1, col2, col3, col4 = st.columns(4)
    
    # ATS Card (Renamed to Resume Quality for clarity)
    from services.ats_scorer import get_ats_interpretation
    ats_interp = get_ats_interpretation(ats_score).split(" - ")[0]
    with col1:
        render_metric_card(
            title="Resume Quality",
            value=f"{ats_score}/100",
            subtitle="ATS Formatting & Resume Structure",
            icon="🎯",
            color_class="card-ats",
            help_text="Resume Quality measures ATS compatibility, formatting, and resume completeness. It is different from Job Description Match and Technical Skill Coverage."
        )
        
    # JD Match Card (Renamed to Semantic JD Match)
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
            title="Semantic JD Match",
            value=jd_value,
            subtitle=jd_sub,
            icon="💼",
            color_class="card-jd",
            help_text="Semantic JD Match measures the conceptual and semantic alignment between the resume text and the job description, using advanced vector space embeddings."
        )
        
    # Skills Match Percentage (Renamed to Technical Skill Coverage)
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
            title="Technical Skill Coverage",
            value=skills_value,
            subtitle=skills_sub,
            icon="🛠️",
            color_class="card-skills",
            help_text="Technical Skill Coverage measures the exact matching percentage of required technical skills and tools extracted from the job description against the resume profile."
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
                <div class="exec-summary-title">Candidate Snapshot</div>
                <div class="exec-summary-text" style="font-style: normal;">{exec_summary}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Experience Timeline
        st.subheader("⏳ Chronological Work History")
        
        # Display precise calculation source for verification
        _, calc_source = calculate_experience_tenure_with_source(parsed_data)
        st.info(f"**Experience Calculation Source:**\n{calc_source}")
        
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
            
            # Skills Badging (Missing / Gaps - Top 10 with Expander for TASK 3)
            missing_skills = semantic_gaps.get("missing_skills", [])
            if len(missing_skills) > 10:
                render_skills_badges(
                    title="Top 10 Missing Tech Requirements (Skill Gaps)",
                    skills=missing_skills[:10],
                    badge_type="gap"
                )
                with st.expander("🔍 View All Skill Gaps"):
                    render_skills_badges(
                        title="All Missing Tech Requirements",
                        skills=missing_skills,
                        badge_type="gap"
                    )
            else:
                render_skills_badges(
                    title="Missing Tech Requirements (Skill Gaps)",
                    skills=missing_skills,
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


def generate_pdf_report(
    parsed_data: Dict[str, Any],
    ats_score: int,
    jd_match_score: int,
    match_details: Dict[str, Any],
    skill_gaps: List[str],
    suggestions: str
) -> bytes:
    """
    Generates a professional recruiter report in PDF format using reportlab.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Styles for premium look
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0052e0'),
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151')
    )
    
    # Header
    name = parsed_data.get("name", "Candidate Profile")
    story.append(Paragraph(f"Resume.AI Recruiter Report: {name}", title_style))
    story.append(Paragraph(f"Email: {parsed_data.get('email', 'N/A')} | Phone: {parsed_data.get('phone', 'N/A')}", body_style))
    story.append(Spacer(1, 15))
    
    # Summary
    story.append(Paragraph("Candidate Summary", section_style))
    story.append(Paragraph(parsed_data.get("summary", "No summary available."), body_style))
    story.append(Spacer(1, 10))
    
    # Metrics Table
    data = [
        ["Metric", "Value", "Status"],
        ["Resume Quality", f"{ats_score}/100", "ATS Ready" if ats_score >= 80 else "Needs Improvement"],
        ["Semantic JD Match", f"{jd_match_score}%" if jd_match_score else "N/A", "Aligned" if jd_match_score >= 70 else "Review Gaps"],
    ]
    t = Table(data, colWidths=[150, 100, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0052e0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E5E7EB')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # Skills
    story.append(Paragraph("Technical Skills", section_style))
    skills = parsed_data.get("skills", [])
    flat_skills = []
    if isinstance(skills, list):
        flat_skills = skills
    elif isinstance(skills, dict):
        for val in skills.values():
            if isinstance(val, list):
                flat_skills.extend(val)
    story.append(Paragraph(f"<b>Identified Skills</b>: {', '.join(flat_skills) if flat_skills else 'None'}", body_style))
    if skill_gaps:
        story.append(Spacer(1, 5))
        story.append(Paragraph(f"<b>Missing Core Requirements</b>: {', '.join(skill_gaps)}", body_style))
    story.append(Spacer(1, 10))
    
    # Projects
    story.append(Paragraph("Key Projects", section_style))
    projects = parsed_data.get("projects", [])
    if projects and isinstance(projects, list):
        for proj in projects:
            p_name = proj.get("name", "Project")
            p_tech = ", ".join(proj.get("tech_stack", []))
            p_sum = proj.get("summary", "")
            story.append(Paragraph(f"• <b>{p_name}</b> (Tech: {p_tech}) - {p_sum}", body_style))
    else:
        story.append(Paragraph("No major projects listed.", body_style))
    story.append(Spacer(1, 10))
    
    # Recommendations
    story.append(Paragraph("AI Recommendations", section_style))
    clean_sug = suggestions.replace("- Suggestion", "\n• Suggestion")
    story.append(Paragraph(clean_sug or "No suggestions available.", body_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def render_premium_suggestions(suggestions_text: str):
    """
    Parses and displays raw AI suggestions as beautifully styled premium cards.
    """
    import re
    if not suggestions_text:
        st.warning("No suggestions available.")
        return
        
    lines = [line.strip() for line in suggestions_text.split("\n") if line.strip()]
    suggestions = []
    
    current_sug = ""
    for line in lines:
        if re.match(r'^(?:-|\*|•|\d+\.)\s*Suggestion\s*\d+:', line, re.IGNORECASE) or re.match(r'^(?:-|\*|•|\d+\.)\s*\[?Suggestion\s*\d+\]?:', line, re.IGNORECASE):
            if current_sug:
                suggestions.append(current_sug)
            clean_line = re.sub(r'^(?:-|\*|•|\d+\.)\s*Suggestion\s*\d+:\s*', '', line, flags=re.IGNORECASE)
            clean_line = re.sub(r'^(?:-|\*|•|\d+\.)\s*\[?Suggestion\s*\d+\]?:\s*', '', clean_line, flags=re.IGNORECASE)
            current_sug = clean_line
        elif line.startswith(("-", "*", "•", "1.", "2.", "3.")) and not current_sug:
            current_sug = line.strip("- *• 1234567890. ")
        elif current_sug:
            current_sug += " " + line
            
    if current_sug:
        suggestions.append(current_sug)
        
    if not suggestions:
        bullets = [l.strip("- *• 1234567890. ") for l in lines if l.strip().startswith(("-", "*", "•", "1.", "2.", "3."))]
        if bullets:
            suggestions = bullets
        else:
            suggestions = [suggestions_text]
            
    st.markdown("### 💡 AI Strategic Resume Recommendations")
    st.caption("Factual and actionable steps to elevate ATS score and candidate JD alignment:")
    st.markdown("<br>", unsafe_allow_html=True)
    
    for idx, sug in enumerate(suggestions, 1):
        priority = "🔴 High Priority" if idx == 1 else ("🟡 Medium Priority" if idx == 2 else "🟢 Low Priority")
        
        st.markdown(
            f"""
            <div style="background-color: var(--secondary-background-color, rgba(240, 242, 246, 0.45)); border: 1px solid rgba(49, 51, 63, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.01);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 0.8rem; font-weight: 750; text-transform: uppercase; letter-spacing: 0.08em; color: gray;">Suggestion #{idx}</span>
                    <span style="font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; background-color: rgba(128,128,128,0.1);">{priority}</span>
                </div>
                <div style="margin-bottom: 8px;"><strong>⚠️ Problem Area:</strong> Structure or keyword density mismatch against targeted job roles.</div>
                <div style="margin-bottom: 8px;"><strong>💡 Actionable Recommendation:</strong> {sug}</div>
                <div><strong>🚀 Expected Impact:</strong> Maximizes ATS parsing compatibility and structural validation index metrics.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
