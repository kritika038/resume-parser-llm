"""
Job Description (JD) Matcher & Semantic Ranker.
Leverages SentenceTransformers (all-MiniLM-L6-v2) for vector encoding and cosine similarity computation.
Performs semantic vector search matching alongside traditional keyword matching.
Keywords: Semantic Search, Embeddings, Vector Search, Cosine Similarity, ATS, Resume Screening, RAG.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Lazy load SentenceTransformer to avoid loading on import
_model = None


def _get_model():
    """
    Lazy load SentenceTransformer model.
    
    Returns:
        SentenceTransformer: Pre-trained model for generating embeddings
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
            return None
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            return None
    return _model


def semantic_similarity_score(resume_text: str, jd_text: str) -> Tuple[float, str]:
    """
    Calculate semantic similarity between resume and job description using embeddings.
    
    Uses pre-trained SentenceTransformer model to generate embeddings for both texts,
    then calculates cosine similarity between them.
    
    Args:
        resume_text: Plain text from the resume
        jd_text: Job description text
        
    Returns:
        tuple: (similarity_score: float 0-1, interpretation: str)
        
    Examples:
        >>> resume = "Python developer with 5 years experience..."
        >>> jd = "Looking for Python engineer..."
        >>> score, interp = semantic_similarity_score(resume, jd)
        >>> print(f"Semantic Match: {score:.2%}")
    """
    if not resume_text or not jd_text:
        logger.warning("Empty resume or JD text provided")
        return 0.0, "Cannot calculate - missing text"
    
    model = _get_model()
    if model is None:
        logger.warning("SentenceTransformer model not available, falling back to keyword matching")
        return 0.0, "Model unavailable"
    
    try:
        # Generate embeddings
        logger.info("Generating embeddings for resume and job description...")
        resume_embedding = model.encode(resume_text, convert_to_tensor=False)
        jd_embedding = model.encode(jd_text, convert_to_tensor=False)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            [resume_embedding],
            [jd_embedding]
        )[0][0]
        
        # Ensure score is between 0 and 1
        similarity = float(np.clip(similarity, 0.0, 1.0))
        
        logger.info(f"Semantic similarity score: {similarity:.4f}")
        
        return similarity, _get_semantic_interpretation(similarity)
        
    except Exception as e:
        logger.error(f"Error calculating semantic similarity: {e}")
        return 0.0, f"Error: {str(e)}"


def _get_semantic_interpretation(score: float) -> str:
    """
    Provides interpretation of semantic similarity score.
    
    Args:
        score: Similarity score 0.0-1.0
        
    Returns:
        str: Interpretation text
    """
    if score >= 0.8:
        return "Excellent semantic match - Very strong alignment"
    elif score >= 0.6:
        return "Good semantic match - Strong alignment"
    elif score >= 0.4:
        return "Moderate semantic match - Reasonable alignment"
    elif score >= 0.2:
        return "Weak semantic match - Limited alignment"
    else:
        return "Poor semantic match - Minimal alignment"


def combined_match_score(
    skills_dict: Dict[str, Any],
    resume_text: str,
    jd_text: Optional[str],
    keyword_weight: float = 0.4,
    semantic_weight: float = 0.6
) -> Tuple[int, List[str], Dict[str, Any]]:
    """
    Calculate combined match score using both keyword and semantic similarity.
    
    Combines two approaches:
    1. Keyword-based matching (skill extraction and JD keywords)
    2. Semantic similarity (deep learning embeddings)
    
    Final score = (keyword_score * keyword_weight) + (semantic_score * semantic_weight)
    
    Args:
        skills_dict: Skills object from parsed resume
        resume_text: Full resume text for semantic analysis
        jd_text: Job description text
        keyword_weight: Weight for keyword matching (0.0-1.0)
        semantic_weight: Weight for semantic matching (0.0-1.0)
        
    Returns:
        tuple: (combined_score: int 0-100, matched_skills: list, details: dict)
        
    Examples:
        >>> skills = {"languages": ["Python"], "tools": ["AWS"]}
        >>> resume_text = "Python developer with AWS expertise..."
        >>> jd_text = "Looking for cloud engineer with Python skills..."
        >>> score, matched, details = combined_match_score(skills, resume_text, jd_text)
        >>> print(f"Combined Score: {score}%")
    """
    if not jd_text or not jd_text.strip():
        logger.info("No job description provided")
        return 0, [], {
            "keyword_score": 0,
            "semantic_score": 0.0,
            "combined_score": 0,
            "approach": "No JD provided"
        }
    
    # 1. Get keyword-based score
    keyword_score, matched_skills = match_with_jd(skills_dict, jd_text)
    
    # 2. Get semantic similarity score
    semantic_sim, _ = semantic_similarity_score(resume_text, jd_text)
    semantic_score = int(semantic_sim * 100)  # Convert to 0-100 scale
    
    # Normalize weights
    total_weight = keyword_weight + semantic_weight
    keyword_weight = keyword_weight / total_weight
    semantic_weight = semantic_weight / total_weight
    
    # 3. Calculate combined score
    combined_score = int(
        (keyword_score * keyword_weight) + (semantic_score * semantic_weight)
    )
    
    logger.info(
        f"Combined match: Keyword={keyword_score}% (w={keyword_weight:.1%}), "
        f"Semantic={semantic_score}% (w={semantic_weight:.1%}), "
        f"Combined={combined_score}%"
    )
    
    details = {
        "keyword_score": keyword_score,
        "semantic_score": semantic_score,
        "semantic_similarity": semantic_sim,
        "combined_score": combined_score,
        "keyword_weight": keyword_weight,
        "semantic_weight": semantic_weight,
        "matched_skills": matched_skills,
        "approach": "Hybrid (Keyword + Semantic)"
    }
    
    return combined_score, matched_skills, details


def match_with_jd(skills_dict: Dict[str, Any], jd_text: Optional[str]) -> Tuple[int, List[str]]:
    """
    Matches resume skills against job description requirements using keyword matching.
    
    Algorithm:
    1. Extract all skills from resume (flatten skill categories)
    2. Parse JD for keywords
    3. Case-insensitive matching
    4. Calculate overlap percentage
    
    Args:
        skills_dict: Skills object from parsed resume
        jd_text: Job description text (optional)
        
    Returns:
        tuple: (match_score: int 0-100, matched_skills: list[str])
        
    Examples:
        >>> skills = {"languages": ["Python"], "tools": ["AWS"]}
        >>> jd = "We need Python and AWS skills"
        >>> score, matched = match_with_jd(skills, jd)
        >>> print(f"Match: {score}%")  # "Match: 100%"
        >>> print(matched)  # ["Python", "AWS"]
    """
    # Handle invalid inputs
    if not jd_text or not jd_text.strip():
        logger.info("No job description provided, skipping JD matching")
        return 0, []
    
    if not skills_dict:
        return 0, []
        
    # Aggregate all skills depending on structure
    all_skills = []
    if isinstance(skills_dict, dict):
        for category, skill_list in skills_dict.items():
            if isinstance(skill_list, list):
                all_skills.extend(skill_list)
    elif isinstance(skills_dict, list):
        all_skills = skills_dict
    else:
        logger.warning(f"Invalid skills format: {type(skills_dict)}")
        return 0, []
        
    if not all_skills:
        logger.info("No skills found in resume")
        return 0, []
    
    # Normalize JD text
    jd_normalized = jd_text.lower()
    
    # Extract words from JD (alphanumeric sequences)
    jd_words = set(re.findall(r'\b[a-z0-9]+\b', jd_normalized))
    
    # Match skills (case-insensitive)
    matched_skills = []
    for skill in all_skills:
        skill_normalized = skill.lower()
        
        # Exact word match
        if skill_normalized in jd_words:
            matched_skills.append(skill)
        # Substring match (for technologies like "C++" or "Node.js")
        elif skill_normalized in jd_normalized:
            matched_skills.append(skill)
    
    # Calculate match score
    total_skills = len(all_skills)
    matched_count = len(matched_skills)
    
    if total_skills == 0:
        match_score = 0
    else:
        match_score = int((matched_count / total_skills) * 100)
    
    logger.info(f"Keyword JD Match: {matched_count}/{total_skills} skills = {match_score}%")
    
    # Remove duplicates while preserving order
    matched_skills = list(dict.fromkeys(matched_skills))
    
    return match_score, matched_skills


def identify_skill_gaps(skills_dict: Dict[str, Any], jd_text: Optional[str]) -> List[str]:
    """
    Identifies skills mentioned in JD but missing from resume.
    
    Args:
        skills_dict: Skills from resume
        jd_text: Job description text
        
    Returns:
        list: Skills mentioned in JD but not in resume
    """
    if not jd_text or not jd_text.strip():
        return []
    
    # Get all resume skills
    resume_skills = set()
    if isinstance(skills_dict, dict):
        for skill_list in skills_dict.values():
            if isinstance(skill_list, list):
                resume_skills.update(s.lower() for s in skill_list if s)
    elif isinstance(skills_dict, list):
        resume_skills.update(s.lower() for s in skills_dict if s)
    
    # Extract common tech keywords from JD
    tech_keywords = extract_tech_keywords(jd_text)
    
    # Find gaps
    gaps = [tech for tech in tech_keywords if tech.lower() not in resume_skills]
    
    logger.info(f"Identified {len(gaps)} skill gaps")
    return gaps


def extract_tech_keywords(text: str) -> List[str]:
    """
    Extracts potential technology keywords from text.
    
    Common tech stack indicators.
    
    Args:
        text: Text to search for keywords
        
    Returns:
        list: Identified technology keywords
    """
    # Common tech keywords to look for
    tech_patterns = [
        r'\bpython\b', r'\bjavascript\b', r'\bjava\b', r'\bc\+\+\b',
        r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bdjango\b',
        r'\bflask\b', r'\bfastapi\b', r'\bnode\.?js\b',
        r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b',
        r'\bkubernetes\b', r'\bgit\b', r'\bjenkins\b',
        r'\bpostgres\b', r'\bmongodb\b', r'\bsql\b',
        r'\btensorflow\b', r'\bpytorch\b', r'\bscikit-learn\b',
        r'\bapi\b', r'\brest\b', r'\bgraphql\b',
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for pattern in tech_patterns:
        if re.search(pattern, text_lower):
            # Extract the matched keyword
            match = re.search(pattern, text_lower)
            if match:
                keyword = match.group(0)
                found_keywords.append(keyword)
    
    return found_keywords


def get_jd_match_interpretation(score: int) -> str:
    """
    Provides interpretation of JD match score.
    
    Args:
        score: JD match percentage 0-100
        
    Returns:
        str: Interpretation text
    """
    if score >= 80:
        return "Excellent Fit - Strong candidate with required skills"
    elif score >= 60:
        return "Good Fit - Qualified with minor skill gaps"
    elif score >= 40:
        return "Moderate Fit - Core skills present; learning curve needed"
    elif score >= 20:
        return "Poor Fit - Significant skill gaps; may require training"
    else:
        return "Not Recommended - Limited skill alignment"

    """
    Matches resume skills against job description requirements.
    
    Algorithm:
    1. Extract all skills from resume (flatten skill categories)
    2. Parse JD for keywords
    3. Case-insensitive matching
    4. Calculate overlap percentage
    
    Args:
        skills_dict: Skills object from parsed resume
        jd_text: Job description text (optional)
        
    Returns:
        tuple: (match_score: int 0-100, matched_skills: list[str])
        
    Examples:
        >>> skills = {"languages": ["Python"], "tools": ["AWS"]}
        >>> jd = "We need Python and AWS skills"
        >>> score, matched = match_with_jd(skills, jd)
        >>> print(f"Match: {score}%")  # "Match: 100%"
        >>> print(matched)  # ["Python", "AWS"]
    """
    # Handle invalid inputs
    if not jd_text or not jd_text.strip():
        logger.info("No job description provided, skipping JD matching")
        return 0, []
    
    if not skills_dict or not isinstance(skills_dict, dict):
        logger.warning("Invalid skills dictionary")
        return 0, []
    
    # Aggregate all skills from all categories
    all_skills = []
    for category, skill_list in skills_dict.items():
        if isinstance(skill_list, list):
            all_skills.extend(skill_list)
    
    if not all_skills:
        logger.info("No skills found in resume")
        return 0, []
    
    # Normalize JD text
    jd_normalized = jd_text.lower()
    
    # Extract words from JD (alphanumeric sequences)
    jd_words = set(re.findall(r'\b[a-z0-9]+\b', jd_normalized))
    
    # Match skills (case-insensitive)
    matched_skills = []
    for skill in all_skills:
        skill_normalized = skill.lower()
        
        # Exact word match
        if skill_normalized in jd_words:
            matched_skills.append(skill)
        # Substring match (for technologies like "C++" or "Node.js")
        elif skill_normalized in jd_normalized:
            matched_skills.append(skill)
    
    # Calculate match score
    total_skills = len(all_skills)
    matched_count = len(matched_skills)
    
    if total_skills == 0:
        match_score = 0
    else:
        match_score = int((matched_count / total_skills) * 100)
    
    logger.info(f"JD Match: {matched_count}/{total_skills} skills = {match_score}%")
    
    # Remove duplicates while preserving order
    matched_skills = list(dict.fromkeys(matched_skills))
    
    return match_score, matched_skills


def identify_skill_gaps(skills_dict: Dict[str, Any], jd_text: Optional[str]) -> List[str]:
    """
    Identifies skills mentioned in JD but missing from resume.
    
    Args:
        skills_dict: Skills from resume
        jd_text: Job description text
        
    Returns:
        list: Skills mentioned in JD but not in resume
    """
    if not jd_text or not jd_text.strip():
        return []
    
    # Get all resume skills
    resume_skills = set()
    if isinstance(skills_dict, dict):
        for skill_list in skills_dict.values():
            if isinstance(skill_list, list):
                resume_skills.update(s.lower() for s in skill_list)
    
    # Extract common tech keywords from JD
    tech_keywords = extract_tech_keywords(jd_text)
    
    # Find gaps
    gaps = [tech for tech in tech_keywords if tech.lower() not in resume_skills]
    
    logger.info(f"Identified {len(gaps)} skill gaps")
    return gaps


def extract_tech_keywords(text: str) -> List[str]:
    """
    Extracts potential technology keywords from text.
    
    Common tech stack indicators.
    
    Args:
        text: Text to search for keywords
        
    Returns:
        list: Identified technology keywords
    """
    # Common tech keywords to look for
    tech_patterns = [
        r'\bpython\b', r'\bjavascript\b', r'\bjava\b', r'\bc\+\+\b',
        r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bdjango\b',
        r'\bflask\b', r'\bfastapi\b', r'\bnode\.?js\b',
        r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b',
        r'\bkubernetes\b', r'\bgit\b', r'\bjenkins\b',
        r'\bpostgres\b', r'\bmongodb\b', r'\bsql\b',
        r'\btensorflow\b', r'\bpytorch\b', r'\bscikit-learn\b',
        r'\bapi\b', r'\brest\b', r'\bgraphql\b',
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    for pattern in tech_patterns:
        if re.search(pattern, text_lower):
            # Extract the matched keyword
            match = re.search(pattern, text_lower)
            if match:
                keyword = match.group(0)
                found_keywords.append(keyword)
    
    return found_keywords


def get_jd_match_interpretation(score: int) -> str:
    """
    Provides interpretation of JD match score.
    
    Args:
        score: JD match percentage 0-100
        
    Returns:
        str: Interpretation text
    """
    if score >= 80:
        return "Excellent Fit - Strong candidate with required skills"
    elif score >= 60:
        return "Good Fit - Qualified with minor skill gaps"
    elif score >= 40:
        return "Moderate Fit - Core skills present; learning curve needed"
    elif score >= 20:
        return "Poor Fit - Significant skill gaps; may require training"
    else:
        return "Not Recommended - Limited skill alignment"
