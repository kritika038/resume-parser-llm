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

if __name__ == "__main__":
    unittest.main()
