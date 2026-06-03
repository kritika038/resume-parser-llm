import unittest
import os
from services.ats_scorer import calculate_ats_score, get_ats_interpretation
from services.jd_matcher import combined_match_score, identify_skill_gaps
from services.llm_providers import get_llm_provider, OllamaProvider, GroqProvider
from utils.validators import validate_resume_schema

# ========== SAMPLE TEST DATA ==========
SAMPLE_RESUME = {
    "name": "Jane Developer",
    "contact": {
        "email": "jane@example.com",
        "phone": "+1-555-0100"
    },
    "education": [
        {
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "institution": "University",
            "year": "2020"
        }
    ],
    "skills": {
        "languages": ["Python", "SQL"],
        "frameworks": ["FastAPI", "React"],
        "tools": ["Docker", "Git"]
    },
    "experience": [
        {
            "role": "Software Engineer",
            "company": "Tech Corp",
            "duration": "2 years",
            "responsibilities": ["Developed backend APIs", "Managed databases"]
        }
    ],
    "projects": [
        {
            "name": "AI Search Engine",
            "tech_stack": ["Python", "FastAPI"],
            "summary": "Built semantic search features",
            "impact": "Boosted query latency by 40%"
        }
    ]
}

class TestResumeIntelligenceServices(unittest.TestCase):
    
    # ========== ATS SCORER TESTS ==========
    def test_calculate_ats_score(self):
        """Verify that ATS Scorer calculates scores correctly based on section completeness."""
        score = calculate_ats_score(SAMPLE_RESUME)
        self.assertTrue(score >= 80)  # Complete contact, experience, skills, projects, and education

    def test_ats_interpretation(self):
        """Verify ATS score descriptions fall into correct bands."""
        self.assertIn("Excellent", get_ats_interpretation(95))
        self.assertIn("Good", get_ats_interpretation(85))
        self.assertIn("Fair", get_ats_interpretation(50))

    # ========== JD MATCHER & SKILLS GAP TESTS ==========
    def test_skill_gaps(self):
        """Verify matching and missing skill gap categories are parsed case-insensitively."""
        jd_text = "Looking for a developer skilled in Python, Docker, Kubernetes, and Java."
        missing = identify_skill_gaps(SAMPLE_RESUME["skills"], jd_text)
        
        missing_lower = [m.lower() for m in missing]
        
        self.assertIn("kubernetes", missing_lower)
        self.assertIn("java", missing_lower)
        self.assertNotIn("python", missing_lower)
        self.assertNotIn("docker", missing_lower)

    def test_combined_match_score(self):
        """Verify combined Jaccard and Semantic scores fall in the [0, 100] boundary."""
        jd_text = "Python developer with FastAPI experience."
        resume_text = "Jane Developer is a software engineer with Python, FastAPI, and Docker experience."
        score, matched, details = combined_match_score(
            SAMPLE_RESUME["skills"],
            resume_text,
            jd_text
        )
        self.assertTrue(0 <= score <= 100)

    # ========== LLM PROVIDERS REGISTRY TESTS ==========
    def test_provider_resolver_default(self):
        """Verify resolver falls back to local Ollama when LLM_PROVIDER is unset."""
        if "LLM_PROVIDER" in os.environ:
            del os.environ["LLM_PROVIDER"]
        provider = get_llm_provider()
        self.assertTrue(isinstance(provider, OllamaProvider))

    def test_provider_resolver_groq(self):
        """Verify resolver returns GroqProvider when LLM_PROVIDER is set to groq."""
        os.environ["LLM_PROVIDER"] = "groq"
        os.environ["GROQ_API_KEY"] = "gsk_test_key"
        provider = get_llm_provider()
        self.assertTrue(isinstance(provider, GroqProvider))

    # ========== SELF HEALING SCHEMA TESTS ==========
    def test_schema_self_healing(self):
        """Verify that missing/malformed keys are successfully healed to default types."""
        malformed_resume = {
            "name": "Truncated Candidate",
            "skills": {
                "languages": "This should be a list, but it's a string!"
            }
        }
        
        success = validate_resume_schema(malformed_resume)
        
        self.assertTrue(success)
        self.assertEqual(malformed_resume["name"], "Truncated Candidate")
        self.assertEqual(malformed_resume["contact"], {'email': '', 'phone': '', 'linkedin': '', 'github': ''})
        self.assertEqual(malformed_resume["education"], [])
        self.assertEqual(malformed_resume["experience"], [])
        self.assertEqual(malformed_resume["projects"], [])
        self.assertEqual(malformed_resume["certifications"], [])
        self.assertEqual(malformed_resume["strengths"], [])
        self.assertEqual(malformed_resume["skills"]["languages"], [])

    # ========== FACTUAL VALIDATION LAYER TESTS ==========
    def test_clean_and_validate_resume(self):
        """Verify factual validation layer: deduplication, technology filtering, and N/A conversion."""
        from utils.validators import clean_and_validate_resume
        
        raw_resume_text = "Jane Developer has experience with Python, FastAPI, and Git. She worked at Tech Corp as a Software Engineer."
        parsed_data = {
            "name": "Jane Developer",
            "email": "jane@example.com",
            "phone": None, # Missing value
            "location": "   ", # Empty location
            "skills": ["Python", "FastAPI", "Python", "Kubernetes"], # Duplicated and inferred
            "employment": [
                {"role": "Software Engineer", "company": "Tech Corp", "duration": "2 years", "responsibilities": ["Coding"]},
                {"role": None, "company": None, "duration": None, "responsibilities": []} # Empty record
            ],
            "projects": []
        }
        
        cleaned = clean_and_validate_resume(parsed_data, raw_resume_text)
        
        # 1. Deduplication & Inferred filtering
        # Python and FastAPI are in the text, Kubernetes is not. Python is deduplicated.
        self.assertIn("Python", cleaned["skills"])
        self.assertIn("FastAPI", cleaned["skills"])
        self.assertNotIn("Kubernetes", cleaned["skills"])
        self.assertEqual(cleaned["skills"].count("Python"), 1)
        
        # 2. Convert missing/empty values to N/A
        self.assertEqual(cleaned["phone"], "N/A")
        self.assertEqual(cleaned["location"], "N/A")
        self.assertEqual(cleaned["github"], "N/A")
        
        # 3. Clean empty records
        self.assertEqual(len(cleaned["employment"]), 1)
        self.assertEqual(cleaned["employment"][0]["role"], "Software Engineer")

    # ========== NEW ATS SCORING METRICS TESTS ==========
    def test_ats_scoring_exact_components(self):
        """Verify the exact score calculation matches the 7 components weights."""
        parsed_data = {
            "name": "Jane",
            "email": "jane@example.com",
            "phone": "N/A",
            "skills": ["Python"], # 20 pts
            "education": [{"degree": "BS"}], # 15 pts
            "employment": [{"role": "Developer"}], # 20 pts
            "projects": [], # 0 pts
            "certifications": [],
            "languages": [],
            "experience_years": "N/A"
        }
        
        # Contact points: name (not in contact score, but in structure), email is present (+5 pts), phone is N/A (+0 pts) -> 5 pts
        # Skills: 20 pts
        # Education: 15 pts
        # Experience: 20 pts
        # Projects: 0 pts
        # Structure score: name, email, skills, education, employment are present (5 sections out of 6). score = int(5/6 * 10) = 8 pts
        # Keyword Coverage: 1 skill -> 1 pt
        # Total: 5 (contact) + 20 (skills) + 15 (education) + 20 (experience) + 0 (projects) + 8 (structure) + 1 (coverage) = 69 pts
        score = calculate_ats_score(parsed_data)
        self.assertEqual(score, 69)

if __name__ == "__main__":
    unittest.main()
