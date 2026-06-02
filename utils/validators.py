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
    
    Args:
        data: Parsed resume dictionary (mutated in-place to self-heal)
        
    Returns:
        bool: True if data is a dictionary and is successfully healed.
    """
    if not isinstance(data, dict):
        return False
        
    # Critical keys & default types
    defaults = {
        "name": ("The Candidate", str),
        "contact": ({}, dict),
        "education": ([], list),
        "skills": ({}, dict),
        "experience": ([], list),
        "projects": ([], list),
        "certifications": ([], list),
        "strengths": ([], list)
    }
    
    for key, (default_val, expected_type) in defaults.items():
        if key not in data or not isinstance(data[key], expected_type):
            data[key] = default_val
            
    # Sub-heal nested contact keys
    contact = data["contact"]
    if not isinstance(contact, dict):
        data["contact"] = {}
        contact = data["contact"]
    
    for contact_key in ["email", "phone", "linkedin", "github"]:
        if contact_key not in contact or not isinstance(contact[contact_key], str):
            contact[contact_key] = ""
            
    # Sub-heal skills dictionary values (must be list of strings)
    skills = data["skills"]
    if not isinstance(skills, dict):
        data["skills"] = {}
        skills = data["skills"]
        
    for skill_cat, skill_list in list(skills.items()):
        if not isinstance(skill_list, list):
            skills[skill_cat] = []
        else:
            # Ensure elements are strings
            skills[skill_cat] = [str(s) for s in skill_list if s is not None]
            
    return True


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
