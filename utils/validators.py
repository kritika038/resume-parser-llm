"""
Validation and cleaning utilities for resume data and JSON output.
Handles JSON validation, sanitization, and error recovery.
"""

import json
import re
from typing import Optional, Dict, Any


def clean_json(raw_output: str) -> Optional[Dict[str, Any]]:
    """
    Validates and cleans LLM JSON output.
    
    Handles common LLM output issues:
    - Markdown code fences (```json, ```)
    - Trailing commas in JSON
    - Smart quotes vs standard quotes
    - Numeric indices (0:, 1:)
    
    Args:
        raw_output: Raw string from LLM (may contain artifacts)
        
    Returns:
        dict: Valid JSON object on success
        None: If parsing fails
        
    Raises:
        None: Returns None on error instead of raising
    """
    try:
        if not raw_output:
            return None

        # Remove numeric index patterns (0:, 1:)
        cleaned = re.sub(r'\b\d+\s*:', '', raw_output)

        # Remove markdown code fences
        cleaned = cleaned.replace("```json", "").replace("```", "")

        # Find JSON boundaries
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1

        if start == -1 or end == 0:
            return None

        json_str = cleaned[start:end]

        # Fix trailing commas before } or ]
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # Try parsing
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Attempted to parse: {raw_output[:200]}...")
        return None
    except Exception as e:
        print(f"Unexpected error in clean_json: {e}")
        return None


def validate_resume_schema(data: Dict[str, Any]) -> bool:
    """
    Validates and self-heals parsed resume data to ensure schema compliance.
    
    Injects default values for missing or structurally incorrect keys
    to guarantee that downstream processing never raises exceptions.
    Supports both old and new schema variants for robust compatibility.
    """
    if not isinstance(data, dict):
        return False
        
    defaults = {
        "name": "N/A",
        "email": "N/A",
        "phone": "N/A",
        "location": "N/A",
        "linkedin": "N/A",
        "github": "N/A",
        "contact": {},
        "skills": [],
        "education": [],
        "internships": [],
        "employment": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "experience_years": "N/A",
        "summary": "N/A",
        "strengths": []
    }
    
    for key, default_val in defaults.items():
        if key not in data:
            data[key] = default_val
            
    # Enforce type correctness for root keys
    for str_key in ["name", "email", "phone", "location", "linkedin", "github", "summary", "experience_years"]:
        if data[str_key] is None or not isinstance(data[str_key], (str, int, float)):
            data[str_key] = "N/A"
        else:
            data[str_key] = str(data[str_key]).strip()
            if data[str_key].lower() in ["null", "none", ""]:
                data[str_key] = "N/A"
                
    # Sub-heal nested contact keys for backward compatibility
    contact = data["contact"]
    if not isinstance(contact, dict):
        data["contact"] = {}
        contact = data["contact"]
    
    for contact_key in ["email", "phone", "linkedin", "github"]:
        if contact_key not in contact or not isinstance(contact[contact_key], str):
            contact[contact_key] = ""
            
    # Sync contact keys between root and sub-dict
    for contact_key in ["email", "phone", "linkedin", "github"]:
        if (not contact[contact_key] or contact[contact_key].lower() == "n/a") and data.get(contact_key) and data.get(contact_key) != "N/A":
            contact[contact_key] = str(data[contact_key])
        if (data.get(contact_key) == "N/A" or not data.get(contact_key)) and contact[contact_key]:
            data[contact_key] = contact[contact_key]
            
    # Handle skills compatibility (list vs dict)
    skills = data["skills"]
    if isinstance(skills, dict):
        for skill_cat, skill_list in list(skills.items()):
            if not isinstance(skill_list, list):
                skills[skill_cat] = []
            else:
                skills[skill_cat] = [str(s) for s in skill_list if s is not None]
    elif isinstance(skills, list):
        data["skills"] = [str(s).strip() for s in skills if s is not None]
    else:
        data["skills"] = []
        
    # Ensure nested objects are lists
    for list_key in ["education", "internships", "employment", "experience", "projects", "certifications", "languages", "strengths"]:
        if not isinstance(data[list_key], list):
            data[list_key] = []
            
    # Sync experience (old) and employment (new)
    experience = data["experience"]
    employment = data["employment"]
    if isinstance(experience, list) and len(experience) > 0 and (not isinstance(employment, list) or len(employment) == 0):
        data["employment"] = experience
    elif isinstance(employment, list) and len(employment) > 0 and (not isinstance(experience, list) or len(experience) == 0):
        data["experience"] = employment
        
    return True


def is_skill_in_resume(skill: str, resume_text: str) -> bool:
    """
    Verifies if a given skill is present in the raw resume text.
    Uses substring checks, word presence, and synonyms registry mapping.
    """
    if not skill or not resume_text:
        return False
    resume_lower = resume_text.lower()
    skill_lower = skill.lower().strip()
    
    # Direct substring check
    if skill_lower in resume_lower:
        return True
        
    # Check individual alphanumeric words of length >= 3
    words = re.findall(r'[a-zA-Z0-9#\+\-]+', skill_lower)
    for w in words:
        if len(w) >= 3 and w in resume_lower:
            return True
            
    # Check skill synonyms registry mapping
    try:
        from services.skill_gap_analyzer import SKILL_SYNONYMS
        for syn, canonical in SKILL_SYNONYMS.items():
            if canonical.lower() == skill_lower:
                if syn.lower() in resume_lower:
                    return True
    except Exception:
        pass
        
    return False


def clean_and_validate_resume(data: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
    """
    Cleans resume data strictly based on factual resume text.
    - Removes duplicated skills.
    - Removes inferred/hallucinated technologies not found in raw text.
    - Removes empty records.
    - Converts missing values to N/A.
    """
    if not isinstance(data, dict):
        return {}
        
    # Verify basic schema properties
    validate_resume_schema(data)
    
    # 1. Deduplicate and filter inferred technologies for skills
    skills = data.get("skills", [])
    if isinstance(skills, list):
        cleaned_skills = []
        seen = set()
        for s in skills:
            if not s or not isinstance(s, str):
                continue
            s_clean = s.strip()
            s_lower = s_clean.lower()
            if s_lower not in seen and s_lower != "null" and s_lower != "none":
                if is_skill_in_resume(s_clean, resume_text):
                    seen.add(s_lower)
                    cleaned_skills.append(s_clean)
        data["skills"] = cleaned_skills
    elif isinstance(skills, dict):
        for cat, s_list in list(skills.items()):
            if isinstance(s_list, list):
                cleaned_cat_skills = []
                seen = set()
                for s in s_list:
                    if not s or not isinstance(s, str):
                        continue
                    s_clean = s.strip()
                    s_lower = s_clean.lower()
                    if s_lower not in seen and s_lower != "null" and s_lower != "none":
                        if is_skill_in_resume(s_clean, resume_text):
                            seen.add(s_lower)
                            cleaned_cat_skills.append(s_clean)
                skills[cat] = cleaned_cat_skills
                
    # Deduplicate languages and certifications
    for list_key in ["languages", "certifications"]:
        lst = data.get(list_key, [])
        if isinstance(lst, list):
            cleaned_lst = []
            seen = set()
            for x in lst:
                if x and isinstance(x, str):
                    x_clean = x.strip()
                    x_lower = x_clean.lower()
                    if x_lower not in seen and x_lower != "null" and x_lower != "none":
                        seen.add(x_lower)
                        cleaned_lst.append(x_clean)
            data[list_key] = cleaned_lst
            
    # 2. Remove empty/blank records
    data["education"] = clean_empty_records(data.get("education", []), ["degree", "field", "institution", "year"])
    data["internships"] = clean_empty_records(data.get("internships", []), ["role", "company", "duration", "responsibilities"])
    data["employment"] = clean_empty_records(data.get("employment", []), ["role", "company", "duration", "responsibilities"])
    data["experience"] = clean_empty_records(data.get("experience", []), ["role", "company", "duration", "responsibilities"])
    data["projects"] = clean_empty_records(data.get("projects", []), ["name", "tech_stack", "summary", "impact"])
    
    # 3. Convert all missing values, None, empty strings, "null", "none" to "N/A"
    for k, v in list(data.items()):
        if k in ["skills", "languages", "certifications", "education", "internships", "employment", "experience", "projects", "contact"]:
            if isinstance(v, list):
                for idx, item in enumerate(v):
                    if isinstance(item, dict):
                        v[idx] = {key: convert_nulls_to_na(val) for key, val in item.items()}
            elif isinstance(v, dict):
                data[k] = {key: convert_nulls_to_na(val) for key, val in v.items()}
        else:
            data[k] = convert_nulls_to_na(v)
            
    return data


def clean_empty_records(records: list, required_keys: list) -> list:
    if not isinstance(records, list):
        return []
    cleaned = []
    for r in records:
        if not isinstance(r, dict):
            continue
        has_val = False
        for k in required_keys:
            val = r.get(k)
            if isinstance(val, list):
                if len(val) > 0 and not all(str(x).strip().lower() in ["null", "none", "n/a", ""] for x in val):
                    has_val = True
                    break
            elif val and str(val).strip() and str(val).strip().lower() not in ["null", "none", "n/a"]:
                has_val = True
                break
        if has_val:
            cleaned.append(r)
    return cleaned


def convert_nulls_to_na(val):
    if val is None:
        return "N/A"
    if isinstance(val, str):
        val_stripped = val.strip()
        if not val_stripped or val_stripped.lower() in ["null", "none", "n/a"]:
            return "N/A"
        return val_stripped
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, dict):
        return {k: convert_nulls_to_na(v) for k, v in val.items()}
    if isinstance(val, list):
        return [convert_nulls_to_na(x) for x in val]
    return val


def sanitize_text(text: str) -> str:
    """
    Sanitizes input text before processing.
    
    Args:
        text: Raw input text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters that might break JSON
    text = text.replace('"', '"').replace('"', '"')  # Fix smart quotes
    
    return text


def extract_json_from_mixed_output(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to extract valid JSON from mixed text output.
    
    Useful when LLM outputs JSON embedded in explanatory text.
    
    Args:
        text: Mixed text that may contain JSON
        
    Returns:
        dict: Extracted JSON, or None if not found
    """
    # Try to find JSON block
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    
    if not json_match:
        return None
    
    return clean_json(json_match.group(0))

