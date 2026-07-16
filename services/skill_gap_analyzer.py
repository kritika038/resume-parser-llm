"""
Semantic Skill Gap Analyzer Service.
Uses SentenceTransformers to evaluate candidates' skill alignment against Job Descriptions.
Features skill normalization, semantic similarity mapping, and customized learning recommendations.
Keywords: Semantic Search, Embeddings, Vector Search, Cosine Similarity, Skill Gap Analysis.
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from services.llm_parser import call_llm

logger = logging.getLogger(__name__)

# Lazy-loaded SentenceTransformer model
_model = None

# Comprehensive Tech Skill Synonyms & Normalization Registry
SKILL_SYNONYMS = {
    # Programming Languages
    "py": "Python",
    "python": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "golang": "Go",
    "go lang": "Go",
    "go": "Go",
    "cpp": "C++",
    "c++": "C++",
    "csharp": "C#",
    "c#": "C#",
    "rb": "Ruby",
    "ruby": "Ruby",
    "php": "PHP",
    
    # Frontend Frameworks
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    
    # Backend Frameworks / Runtimes
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    
    # Cloud Providers & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Microsoft Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "cicd": "CI/CD",
    "ci/cd": "CI/CD",
    
    # Databases & Caching
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sql": "SQL",
    "nosql": "NoSQL",
    
    # AI/ML & Data Engineering
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit": "Scikit-Learn",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "spark": "Apache Spark",
    "hadoop": "Apache Hadoop",
    "llm": "LLMs",
    "llms": "LLMs",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
}

# High-quality study paths and learning recommendations for key technology gaps
LEARNING_RESOURCES = {
    "Python": {
        "doc": "https://docs.python.org/3/tutorial/",
        "path": "Complete the 'Python for Beginners' track. Practice list comprehensions, decorators, and basic standard libraries."
    },
    "JavaScript": {
        "doc": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "path": "Master modern ES6+ features (promises, async/await, arrow functions, modules) on MDN Web Docs."
    },
    "TypeScript": {
        "doc": "https://www.typescriptlang.org/docs/handbook/intro.html",
        "path": "Learn interfaces, types, interfaces vs types, generics, and compiler options in TypeScript Handbook."
    },
    "React.js": {
        "doc": "https://react.dev/learn",
        "path": "Build simple interactive apps focusing on functional components, state hooks (useState, useEffect, useContext), and clean prop-drilling solutions."
    },
    "Node.js": {
        "doc": "https://nodejs.org/en/docs/guides/",
        "path": "Learn asynchronous event loops, package management with npm/yarn, and build basic HTTP REST servers using Express.js."
    },
    "Go": {
        "doc": "https://go.dev/doc/tutorial/getting-started",
        "path": "Go through 'A Tour of Go' covering basic syntax, structures, interfaces, and concurrency primitives (goroutines and channels)."
    },
    "Kubernetes": {
        "doc": "https://kubernetes.io/docs/tutorials/",
        "path": "Study core K8s objects (Pods, Deployments, Services, ConfigMaps). Practice local deployments using Minikube or k3s."
    },
    "Docker": {
        "doc": "https://docs.docker.com/get-started/",
        "path": "Learn how to write high-efficiency multi-stage Dockerfiles, understand image layering, container networking, and Docker Compose."
    },
    "AWS": {
        "doc": "https://aws.amazon.com/getting-started/hands-on/",
        "path": "Gain fundamental familiarity with core services: compute (EC2, Lambda), storage (S3), database (RDS, DynamoDB), and networking (VPC, IAM)."
    },
    "GCP": {
        "doc": "https://cloud.google.com/docs",
        "path": "Learn compute instances, Google Kubernetes Engine (GKE), BigQuery, Cloud Storage, and Google Cloud Identity & Access Management."
    },
    "PostgreSQL": {
        "doc": "https://www.postgresql.org/docs/online-resources/",
        "path": "Study indexing strategies, query execution plans (EXPLAIN), connection pooling, and normalization/denormalization trade-offs."
    },
    "MongoDB": {
        "doc": "https://learn.mongodb.com/",
        "path": "Understand document structures, aggregation pipelines, schema design for sub-documents, and indexing strategies in NoSQL."
    },
    "Django": {
        "doc": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
        "path": "Build basic CRUD applications focusing on Django ORM, Admin Panel, template structures, and secure forms."
    },
    "FastAPI": {
        "doc": "https://fastapi.tiangolo.com/tutorial/",
        "path": "Learn asynchronous route definition, schema validation using Pydantic, dependency injection, and automatic OpenAPI generation."
    },
    "PyTorch": {
        "doc": "https://pytorch.org/tutorials/",
        "path": "Study tensor manipulation, dynamic computation graphs, writing custom Dataset classes, and training loops."
    },
    "TensorFlow": {
        "doc": "https://www.tensorflow.org/tutorials",
        "path": "Learn the Keras API, dataset pipelines using tf.data, model serialization, and TensorBoard debugging."
    },
    "Machine Learning": {
        "doc": "https://scikit-learn.org/stable/tutorial/index.html",
        "path": "Master classical algorithms (regression, SVMs, decision trees, random forests) and feature engineering using Scikit-Learn."
    },
    "CI/CD": {
        "doc": "https://docs.github.com/en/actions",
        "path": "Build automated pipelines (GitHub Actions, GitLab CI, or Jenkins) that run unit tests, check linting, and deploy packages."
    }
}


def _get_model():
    """
    Lazy load SentenceTransformer model.
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model in SkillGapAnalyzer (all-MiniLM-L6-v2)...")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully in SkillGapAnalyzer")
        except ImportError:
            logger.warning("sentence-transformers not installed. SkillGapAnalyzer falling back.")
            return None
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            return None
    return _model


def normalize_skill(skill: str) -> str:
    """
    Normalizes a skill name by looking it up in the synonyms registry.
    
    Args:
        skill: Raw skill string (e.g. "aws")
        
    Returns:
        str: Normalized skill name (e.g. "AWS")
    """
    clean_skill = skill.strip().lower()
    
    # Check exact match in synonyms registry
    if clean_skill in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[clean_skill]
        
    # Check substring matches for standard technologies
    for key, canonical in SKILL_SYNONYMS.items():
        # Match boundaries to avoid matching "go" inside "django"
        if len(key) > 2 and key in clean_skill:
            return canonical
            
    # Capitalize first letter of each word if not in registry
    return skill.strip().title()


def extract_skills_from_jd(jd_text: str) -> List[str]:
    """
    Extracts explicit required technical skills from Job Description using LLM,
    falling back to a comprehensive regex catalog if offline.
    
    Args:
        jd_text: Plain text job description
        
    Returns:
        list: Extracted required skill strings
    """
    if not jd_text or not jd_text.strip():
        return []
        
    # Try LLM Extraction
    prompt = f"""
    You are a professional recruiting analyzer.
    Extract all key technical skills, programming languages, software frameworks, databases, cloud platforms, and developer tools explicitly mentioned as requirements in the following Job Description.
    
    STRICT RULES:
    - Output ONLY a flat JSON list under the key "skills".
    - Do NOT include soft skills like "leadership", "communication", or "agile". Focus purely on hard tech.
    - Start with {{ and end with }}
    - Do not include markdown code blocks or explanations.
    
    Job Description:
    {jd_text}
    """
    
    logger.info("Attempting LLM extraction of skills from JD...")
    raw_json = call_llm(prompt)
    
    if raw_json:
        try:
            # Simple JSON cleanup in case markdown artifacts are present
            clean_str = raw_json.strip()
            if "```json" in clean_str:
                clean_str = clean_str.split("```json")[1].split("```")[0]
            elif "```" in clean_str:
                clean_str = clean_str.split("```")[1].split("```")[0]
                
            import json
            data = json.loads(clean_str)
            skills = data.get("skills", [])
            if skills and isinstance(skills, list):
                logger.info(f"LLM successfully extracted {len(skills)} skills from JD")
                return list(dict.fromkeys([normalize_skill(s) for s in skills if s]))
        except Exception as e:
            logger.warning(f"Failed to parse LLM JD skill extraction output: {e}")
            
    # Fallback to Regex Catalog Extraction
    logger.info("Using robust regex catalog for JD skill extraction...")
    found_skills = []
    jd_lower = jd_text.lower()
    
    # Gather all keys from synonym dictionary and common list
    candidate_keys = set(SKILL_SYNONYMS.keys())
    
    for key in candidate_keys:
        # Match using word boundaries to avoid partial matching (e.g. 'go' in 'good')
        # Support special characters in patterns like C++ and C#
        pattern_key = re.escape(key)
        if key == "c++":
            pattern = r'\bc\+\+'
        elif key == "c#":
            pattern = r'\bc\#'
        elif key == "go":
            pattern = r'\bgo\b'
        elif len(key) <= 2:
            pattern = rf'\b{pattern_key}\b'
        else:
            pattern = rf'\b{pattern_key}'
            
        if re.search(pattern, jd_lower):
            found_skills.append(SKILL_SYNONYMS[key])
            
    # Remove duplicates while preserving order
    skills = list(dict.fromkeys(found_skills))
    logger.info(f"Regex catalog extracted {len(skills)} skills from JD")
    return skills


def analyze_skill_gaps(
    resume_skills: Any,
    jd_text: str,
    similarity_threshold: float = 0.70
) -> Dict[str, Any]:
    """
    Performs dense semantic skill gap analysis between resume skills and a job description.
    Uses SentenceTransformers to perform conceptual matching rather than strict text overlap.
    
    Args:
        resume_skills: Dictionary of parsed resume skills (by category) OR list of flat strings
        jd_text: Job Description plain text
        similarity_threshold: Cosine similarity cutoff to count as a match (0.0 to 1.0)
        
    Returns:
        dict: A comprehensive dictionary containing:
            - matched_skills: List of dicts with matching details
            - missing_skills: List of missing required technologies
            - recommended_skills: Detailed list of recommended resources/pathways
            - match_percentage: Refined matching index
    """
    # 1. Flatten and normalize candidate skills
    candidate_skills_raw = []
    if isinstance(resume_skills, dict):
        for s_list in resume_skills.values():
            if isinstance(s_list, list):
                candidate_skills_raw.extend(s_list)
    elif isinstance(resume_skills, list):
        candidate_skills_raw = resume_skills
        
    candidate_skills = list(dict.fromkeys([normalize_skill(s) for s in candidate_skills_raw if s]))
    
    # 2. Extract required skills from JD
    required_skills = extract_skills_from_jd(jd_text)
    
    if not required_skills:
        logger.warning("No technical requirements extracted from JD")
        return {
            "matched_skills": [],
            "missing_skills": [],
            "recommended_skills": [],
            "match_percentage": 0
        }
        
    if not candidate_skills:
        logger.warning("No skills extracted from candidate resume")
        # All required skills are missing
        recommendations = generate_recommendations(required_skills)
        return {
            "matched_skills": [],
            "missing_skills": required_skills,
            "recommended_skills": recommendations,
            "match_percentage": 0
        }

    # 3. Load SentenceTransformer model
    model = _get_model()
    
    # Fallback to basic string comparison if model is unavailable
    if model is None:
        logger.warning("SentenceTransformer not available in Analyzer, falling back to basic matching")
        matched = []
        missing = []
        
        candidate_lower = [c.lower() for c in candidate_skills]
        for req in required_skills:
            if req.lower() in candidate_lower:
                matched.append({
                    "jd_skill": req,
                    "candidate_skill": req,
                    "similarity": 1.0
                })
            else:
                missing.append(req)
                
        match_pct = int((len(matched) / len(required_skills)) * 100) if required_skills else 0
        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "recommended_skills": generate_recommendations(missing),
            "match_percentage": match_pct
        }

    try:
        # 4. Generate Embeddings
        logger.info(f"Generating semantic embeddings for {len(required_skills)} JD requirements and {len(candidate_skills)} candidate skills...")
        req_embeddings = model.encode(required_skills, convert_to_tensor=False)
        cand_embeddings = model.encode(candidate_skills, convert_to_tensor=False)
        
        # Calculate Cosine Similarity Matrix
        # Rows = Required Skills, Columns = Candidate Skills
        sim_matrix = cosine_similarity(req_embeddings, cand_embeddings)
        
        matched = []
        missing = []
        
        # 5. Classify Matched vs Missing
        for r_idx, req in enumerate(required_skills):
            # Find candidate skill with highest similarity to this requirement
            c_idx = np.argmax(sim_matrix[r_idx])
            best_sim = float(sim_matrix[r_idx][c_idx])
            best_cand = candidate_skills[c_idx]
            
            logger.debug(f"Matching Requirement '{req}' -> Candidate '{best_cand}' (similarity = {best_sim:.4f})")
            
            if best_sim >= similarity_threshold:
                matched.append({
                    "jd_skill": req,
                    "candidate_skill": best_cand,
                    "similarity": best_sim
                })
            else:
                missing.append(req)
                
        # Calculate Match Percentage
        total_reqs = len(required_skills)
        match_pct = int((len(matched) / total_reqs) * 100) if total_reqs > 0 else 0
        
        # 6. Generate Recommendations for Missing Skills
        recommendations = generate_recommendations(missing)
        
        logger.info(f"Semantic Skill Gap analysis complete: Match={match_pct}%, Matched={len(matched)}, Gaps={len(missing)}")
        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "recommended_skills": recommendations,
            "match_percentage": match_pct
        }
        
    except Exception as e:
        logger.error(f"Error executing semantic skill gap analysis: {e}")
        # Basic fallback in case of matrix/vector operations failure
        matched = []
        missing = []
        candidate_lower = [c.lower() for c in candidate_skills]
        for req in required_skills:
            if req.lower() in candidate_lower:
                matched.append({"jd_skill": req, "candidate_skill": req, "similarity": 1.0})
            else:
                missing.append(req)
        match_pct = int((len(matched) / len(required_skills)) * 100) if required_skills else 0
        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "recommended_skills": generate_recommendations(missing),
            "match_percentage": match_pct
        }


def generate_recommendations(missing_skills: List[str]) -> List[Dict[str, str]]:
    """
    Builds a list of learning recommendations and pathways for missing technologies.
    
    Args:
        missing_skills: List of missing technologies
        
    Returns:
        list: Detailed list of dict objects containing learning resources and pathways
    """
    recommendations = []
    
    for skill in missing_skills:
        rec = {
            "skill": skill,
            "resource_url": "https://www.google.com/search?q=" + "+".join(skill.split()) + "+documentation",
            "pathway": f"Familiarize yourself with the core syntax, constructs, and common use cases of {skill}."
        }
        
        # Check if we have pre-defined high-quality pathways for this technology
        for canonical, resource in LEARNING_RESOURCES.items():
            if skill.lower() == canonical.lower() or canonical.lower() in skill.lower():
                rec["resource_url"] = resource["doc"]
                rec["pathway"] = resource["path"]
                break
                
        recommendations.append(rec)
        
    return recommendations
