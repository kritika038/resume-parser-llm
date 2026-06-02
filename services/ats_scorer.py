"""
ATS (Applicant Tracking System) scoring service.
Evaluates resume compatibility with ATS systems.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_ats_score(resume_data: Dict[str, Any]) -> int:
    """
    Calculates ATS compatibility score for a resume.
    
    Uses weighted component scoring:
    - Name: 10 points
    - Email: 10 points
    - Phone: 10 points
    - Skills Section: 30 points
    - Experience Data: 20 points
    - Projects: 20 points
    
    Total: 100 points (maximum)
    
    Args:
        resume_data: Parsed resume dictionary
        
    Returns:
        int: ATS score 0-100
        
    Examples:
        >>> resume = {"name": "John", "contact": {"email": "john@example.com"}, ...}
        >>> score = calculate_ats_score(resume)
        >>> print(f"ATS Score: {score}/100")
    """
    if not resume_data or not isinstance(resume_data, dict):
        logger.warning("Invalid resume data for ATS scoring")
        return 0
    
    score = 0
    
    # Name: 10 points
    if resume_data.get("name") and resume_data["name"].strip():
        score += 10
        logger.debug("✓ Name present: +10")
    
    # Contact information
    contact = resume_data.get("contact", {})
    if isinstance(contact, dict):
        # Email: 10 points
        if contact.get("email") and contact["email"].strip():
            score += 10
            logger.debug("✓ Email present: +10")
        
        # Phone: 10 points
        if contact.get("phone") and contact["phone"].strip():
            score += 10
            logger.debug("✓ Phone present: +10")
    
    # Skills section: 30 points
    skills = resume_data.get("skills", {})
    if isinstance(skills, dict) and any(skills.values()):
        # Check if at least one skill category is non-empty
        has_skills = any(
            isinstance(v, list) and len(v) > 0 
            for v in skills.values()
        )
        if has_skills:
            score += 30
            logger.debug("✓ Skills present: +30")
    
    # Experience: 20 points
    experience = resume_data.get("experience", [])
    if isinstance(experience, list) and len(experience) > 0:
        # Check if experiences have required fields
        has_valid_exp = any(
            exp.get("role") and exp.get("company") and exp.get("duration")
            for exp in experience
        )
        if has_valid_exp:
            score += 20
            logger.debug("✓ Experience present: +20")
    
    # Projects: 20 points
    projects = resume_data.get("projects", [])
    if isinstance(projects, list) and len(projects) > 0:
        # Check if projects have required fields
        has_valid_proj = any(
            proj.get("name") and proj.get("tech_stack")
            for proj in projects
        )
        if has_valid_proj:
            score += 20
            logger.debug("✓ Projects present: +20")
    
    # Ensure score doesn't exceed 100
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
    
    if not resume_data.get("name"):
        missing.append("Name")
    
    contact = resume_data.get("contact", {})
    if not contact.get("email"):
        missing.append("Email address")
    if not contact.get("phone"):
        missing.append("Phone number")
    
    skills = resume_data.get("skills", {})
    if not any(skills.values()):
        missing.append("Skills section")
    
    experience = resume_data.get("experience", [])
    if not experience:
        missing.append("Experience details")
    
    projects = resume_data.get("projects", [])
    if not projects:
        missing.append("Projects section")
    
    return missing
