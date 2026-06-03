"""
ATS (Applicant Tracking System) scoring service.
Evaluates resume compatibility with ATS systems.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_ats_score(resume_data: Dict[str, Any], keyword_match_score: Optional[int] = None) -> int:
    """
    Calculates ATS compatibility score for a resume using actual resume quality metrics.
    
    Score Components:
    - Contact Information (10)
    - Skills Section (20)
    - Education Section (15)
    - Experience Section (20)
    - Projects Section (15)
    - Resume Structure (10)
    - Keyword Coverage (10)
    
    Maximum = 100
    
    Args:
        resume_data: Parsed resume dictionary
        keyword_match_score: Optional keyword match score against job description
        
    Returns:
        int: ATS score 0-100
    """
    if not resume_data or not isinstance(resume_data, dict):
        logger.warning("Invalid resume data for ATS scoring")
        return 0
    
    score = 0
    
    # 1. Contact Information: 10 points
    # (5 points for email, 5 points for phone)
    email = resume_data.get("email")
    phone = resume_data.get("phone")
    if email and email != "N/A" and email.strip():
        score += 5
        logger.debug("✓ Email present: +5")
    if phone and phone != "N/A" and phone.strip():
        score += 5
        logger.debug("✓ Phone present: +5")
        
    # 2. Skills Section: 20 points
    skills = resume_data.get("skills", [])
    if isinstance(skills, list):
        if len(skills) > 0 and not all(s == "N/A" for s in skills):
            score += 20
            logger.debug("✓ Skills present: +20")
    elif isinstance(skills, dict):
        has_skills = any(isinstance(v, list) and len(v) > 0 for v in skills.values())
        if has_skills:
            score += 20
            logger.debug("✓ Skills present: +20")
            
    # 3. Education Section: 15 points
    education = resume_data.get("education", [])
    if isinstance(education, list) and len(education) > 0:
        score += 15
        logger.debug("✓ Education present: +15")
        
    # 4. Experience Section: 20 points (Employment + Internships)
    employment = resume_data.get("employment", [])
    internships = resume_data.get("internships", [])
    # Support backward compatibility with "experience" key
    experience = resume_data.get("experience", [])
    
    has_exp = False
    if isinstance(employment, list) and len(employment) > 0:
        has_exp = True
    elif isinstance(internships, list) and len(internships) > 0:
        has_exp = True
    elif isinstance(experience, list) and len(experience) > 0:
        has_exp = True
        
    if has_exp:
        score += 20
        logger.debug("✓ Experience present: +20")
        
    # 5. Projects Section: 15 points
    projects = resume_data.get("projects", [])
    if isinstance(projects, list) and len(projects) > 0:
        score += 15
        logger.debug("✓ Projects present: +15")
        
    # 6. Resume Structure: 10 points
    # Evaluates presence of core sections (Up to 10 points based on completeness of 6 major categories)
    sections_present = 0
    if resume_data.get("name") and resume_data.get("name") != "N/A":
        sections_present += 1
    if (email and email != "N/A") or (phone and phone != "N/A"):
        sections_present += 1
    if isinstance(skills, list) and len(skills) > 0:
        sections_present += 1
    elif isinstance(skills, dict) and any(isinstance(v, list) and len(v) > 0 for v in skills.values()):
        sections_present += 1
    if education:
        sections_present += 1
    if employment or internships or experience:
        sections_present += 1
    if projects:
        sections_present += 1
        
    structure_score = int((sections_present / 6) * 10)
    score += structure_score
    logger.debug(f"✓ Resume Structure Completeness ({sections_present}/6): +{structure_score}")
    
    # 7. Keyword Coverage: 10 points
    # (Scale keyword match score if available, or fall back to skill variety density)
    if keyword_match_score is not None:
        coverage = min(10, int(keyword_match_score / 10))
        score += coverage
        logger.debug(f"✓ Keyword Match Coverage: +{coverage}")
    else:
        # Density fallback
        flat_skills = []
        if isinstance(skills, list):
            flat_skills = skills
        elif isinstance(skills, dict):
            for s_list in skills.values():
                if isinstance(s_list, list):
                    flat_skills.extend(s_list)
        skills_count = len([s for s in flat_skills if s != "N/A"])
        coverage = min(10, skills_count)
        score += coverage
        logger.debug(f"✓ Skills Density Coverage ({skills_count}): +{coverage}")
        
    final_score = min(score, 100)
    logger.info(f"ATS Score calculated: {final_score}/100")
    return final_score


def get_ats_interpretation(score: int) -> str:
    """
    Provides interpretation of ATS score.
    
    Args:
        score: ATS score 0-100
        
    Returns:
        str: Interpretation text
    """
    if score >= 90:
        return "Excellent ATS Compatibility - Ready for submission"
    elif score >= 70:
        return "Good ATS Compatibility - Minor improvements recommended"
    elif score >= 50:
        return "Fair ATS Compatibility - Significant improvements needed"
    else:
        return "Poor ATS Compatibility - Major restructuring required"


def get_missing_ats_elements(resume_data: Dict[str, Any]) -> list[str]:
    """
    Identifies missing elements affecting ATS score.
    
    Args:
        resume_data: Parsed resume dictionary
        
    Returns:
        list: Missing elements that would improve ATS score
    """
    missing = []
    
    if not resume_data.get("name") or resume_data.get("name") == "N/A":
        missing.append("Name")
    
    email = resume_data.get("email")
    phone = resume_data.get("phone")
    
    # Sub-dict contact check for compatibility
    contact = resume_data.get("contact", {})
    if not email or email == "N/A":
        missing.append("Email address")
    if not phone or phone == "N/A":
        missing.append("Phone number")
    
    skills = resume_data.get("skills", [])
    has_skills = False
    if isinstance(skills, list) and len(skills) > 0:
        has_skills = True
    elif isinstance(skills, dict) and any(isinstance(v, list) and len(v) > 0 for v in skills.values()):
        has_skills = True
        
    if not has_skills:
        missing.append("Skills section")
    
    education = resume_data.get("education", [])
    if not education:
        missing.append("Education details")
        
    employment = resume_data.get("employment", [])
    internships = resume_data.get("internships", [])
    experience = resume_data.get("experience", [])
    if not employment and not internships and not experience:
        missing.append("Experience/Employment details")
    
    projects = resume_data.get("projects", [])
    if not projects:
        missing.append("Projects section")
    return missing
