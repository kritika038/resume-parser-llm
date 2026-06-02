"""
Candidate Comparator Service.
Analyzes and ranks multiple resumes against a single job description.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
import json

from services.pdf_extractor import extract_pdf
from services.llm_parser import parse_resume
from services.ats_scorer import calculate_ats_score
from services.jd_matcher import (
    combined_match_score,
    match_with_jd,
    semantic_similarity_score,
    identify_skill_gaps
)

logger = logging.getLogger(__name__)


@dataclass
class CandidateScore:
    """Represents a candidate's scoring against a job description."""
    
    candidate_id: str
    name: str
    email: str
    ats_score: int
    keyword_match: int
    semantic_match: float
    combined_jd_match: int
    total_skills: int
    matched_skills: List[str] = field(default_factory=list)
    skill_gaps: List[str] = field(default_factory=list)
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def overall_score(self) -> float:
        """
        Calculate overall candidate score.
        Weights: 30% ATS, 40% JD Match, 30% Semantic Similarity
        
        Returns:
            float: Weighted overall score (0-100)
        """
        ats_weight = 0.30
        jd_weight = 0.40
        semantic_weight = 0.30
        
        semantic_percent = int(self.semantic_match * 100)
        
        overall = (
            (self.ats_score * ats_weight) +
            (self.combined_jd_match * jd_weight) +
            (semantic_percent * semantic_weight)
        )
        
        return overall


class CandidateComparator:
    """Compares and ranks multiple resumes against a job description."""
    
    def __init__(self):
        """Initialize the comparator."""
        self.candidates: List[CandidateScore] = []
        self.jd_text: Optional[str] = None
        
    def add_resume_text(
        self,
        candidate_id: str,
        resume_text: str,
        jd_text: str,
        candidate_name: Optional[str] = None
    ) -> CandidateScore:
        """
        Process a single resume and score against JD.
        
        Args:
            candidate_id: Unique identifier for candidate
            resume_text: Full resume text
            jd_text: Job description text
            candidate_name: Optional candidate name (extracted if not provided)
            
        Returns:
            CandidateScore: Scored candidate data
            
        Raises:
            ValueError: If resume parsing fails
        """
        try:
            logger.info(f"Processing candidate {candidate_id}")
            
            # Parse resume
            parsed_data = parse_resume(resume_text)
            if not parsed_data:
                logger.error(f"Failed to parse resume for {candidate_id}")
                raise ValueError(f"Failed to parse resume for {candidate_id}")
            
            # Extract basic info
            name = candidate_name or parsed_data.get("name", f"Candidate {candidate_id}")
            email = parsed_data.get("email", "Not found")
            
            # Calculate scores
            ats_score = calculate_ats_score(parsed_data)
            
            combined_score, matched_skills, match_details = combined_match_score(
                parsed_data.get("skills", {}),
                resume_text,
                jd_text,
                keyword_weight=0.4,
                semantic_weight=0.6
            )
            
            keyword_match = match_details.get("keyword_score", 0)
            semantic_match = match_details.get("semantic_similarity", 0.0)
            
            skill_gaps = identify_skill_gaps(parsed_data.get("skills", {}), jd_text)
            
            total_skills = sum(
                len(v) if isinstance(v, list) else 0
                for v in parsed_data.get("skills", {}).values()
            )
            
            # Create candidate score
            candidate = CandidateScore(
                candidate_id=candidate_id,
                name=name,
                email=email,
                ats_score=ats_score,
                keyword_match=keyword_match,
                semantic_match=semantic_match,
                combined_jd_match=combined_score,
                total_skills=total_skills,
                matched_skills=matched_skills,
                skill_gaps=skill_gaps,
                parsed_data=parsed_data
            )
            
            self.candidates.append(candidate)
            self.jd_text = jd_text
            
            logger.info(
                f"Scored {candidate_id}: "
                f"ATS={ats_score}, Keyword={keyword_match}%, "
                f"Semantic={semantic_match:.2%}, Combined={combined_score}%"
            )
            
            return candidate
            
        except Exception as e:
            logger.error(f"Error processing candidate {candidate_id}: {e}")
            raise
    
    def add_pdf_resume(
        self,
        candidate_id: str,
        pdf_bytes: bytes,
        jd_text: str,
        candidate_name: Optional[str] = None
    ) -> CandidateScore:
        """
        Process a PDF resume.
        
        Args:
            candidate_id: Unique identifier for candidate
            pdf_bytes: PDF file bytes
            jd_text: Job description text
            candidate_name: Optional candidate name
            
        Returns:
            CandidateScore: Scored candidate data
        """
        logger.info(f"Extracting PDF for candidate {candidate_id}")
        
        resume_text = extract_pdf_from_bytes(pdf_bytes)
        if not resume_text:
            logger.error(f"Failed to extract PDF for {candidate_id}")
            raise ValueError(f"Failed to extract PDF for {candidate_id}")
        
        return self.add_resume_text(
            candidate_id,
            resume_text,
            jd_text,
            candidate_name
        )
    
    def get_ranked_candidates(
        self,
        sort_by: str = "overall"
    ) -> List[CandidateScore]:
        """
        Get candidates ranked by specified metric.
        
        Args:
            sort_by: Sorting criterion
                - "overall": Overall score (default)
                - "ats": ATS score
                - "jd_match": JD match score
                - "semantic": Semantic similarity
                - "name": Candidate name (A-Z)
        
        Returns:
            list: Sorted list of CandidateScore objects
        """
        if not self.candidates:
            logger.warning("No candidates to rank")
            return []
        
        reverse = sort_by != "name"  # Sort names A-Z, scores high-low
        
        if sort_by == "overall":
            sorted_candidates = sorted(
                self.candidates,
                key=lambda c: c.overall_score,
                reverse=reverse
            )
        elif sort_by == "ats":
            sorted_candidates = sorted(
                self.candidates,
                key=lambda c: c.ats_score,
                reverse=reverse
            )
        elif sort_by == "jd_match":
            sorted_candidates = sorted(
                self.candidates,
                key=lambda c: c.combined_jd_match,
                reverse=reverse
            )
        elif sort_by == "semantic":
            sorted_candidates = sorted(
                self.candidates,
                key=lambda c: c.semantic_match,
                reverse=reverse
            )
        elif sort_by == "name":
            sorted_candidates = sorted(
                self.candidates,
                key=lambda c: c.name,
                reverse=reverse
            )
        else:
            logger.warning(f"Unknown sort_by: {sort_by}, using overall")
            sorted_candidates = sorted(
                self.candidates,
                key=lambda c: c.overall_score,
                reverse=True
            )
        
        logger.info(f"Ranked {len(sorted_candidates)} candidates by {sort_by}")
        return sorted_candidates
    
    def get_summary_table(self, sort_by: str = "overall") -> Dict[str, Any]:
        """
        Get summary table data for display.
        
        Args:
            sort_by: Sorting criterion (see get_ranked_candidates)
        
        Returns:
            dict: Table data with columns and rows
        """
        ranked = self.get_ranked_candidates(sort_by)
        
        rows = []
        for rank, candidate in enumerate(ranked, 1):
            rows.append({
                "Rank": rank,
                "Name": candidate.name,
                "Email": candidate.email,
                "Overall Score": f"{candidate.overall_score:.1f}",
                "ATS Score": f"{candidate.ats_score}/100",
                "Keyword Match": f"{candidate.keyword_match}%",
                "Semantic Match": f"{int(candidate.semantic_match * 100)}%",
                "JD Match": f"{candidate.combined_jd_match}%",
                "Total Skills": candidate.total_skills,
                "Matched Skills": len(candidate.matched_skills),
                "Skill Gaps": len(candidate.skill_gaps)
            })
        
        return {
            "total_candidates": len(self.candidates),
            "rows": rows,
            "columns": [
                "Rank", "Name", "Email", "Overall Score",
                "ATS Score", "Keyword Match", "Semantic Match",
                "JD Match", "Total Skills", "Matched Skills", "Skill Gaps"
            ]
        }
    
    def get_detailed_comparison(self) -> List[Dict[str, Any]]:
        """
        Get detailed comparison of all candidates.
        
        Returns:
            list: List of detailed candidate information
        """
        ranked = self.get_ranked_candidates()
        
        detailed = []
        for rank, candidate in enumerate(ranked, 1):
            detailed.append({
                "rank": rank,
                "candidate_id": candidate.candidate_id,
                "name": candidate.name,
                "email": candidate.email,
                "overall_score": candidate.overall_score,
                "ats_score": candidate.ats_score,
                "keyword_match": candidate.keyword_match,
                "semantic_match": candidate.semantic_match,
                "combined_jd_match": candidate.combined_jd_match,
                "total_skills": candidate.total_skills,
                "matched_skills": candidate.matched_skills,
                "skill_gaps": candidate.skill_gaps,
                "parsed_resume": candidate.parsed_data
            })
        
        return detailed
    
    def get_top_candidates(self, top_n: int = 5) -> List[CandidateScore]:
        """
        Get top N candidates by overall score.
        
        Args:
            top_n: Number of top candidates to return
        
        Returns:
            list: Top candidates
        """
        ranked = self.get_ranked_candidates("overall")
        return ranked[:top_n]
    
    def export_results(self, format: str = "json") -> str:
        """
        Export comparison results.
        
        Args:
            format: Export format ("json" or "csv")
        
        Returns:
            str: Formatted export data
        """
        if format == "json":
            detailed = self.get_detailed_comparison()
            return json.dumps(detailed, indent=2)
        
        elif format == "csv":
            if not self.candidates:
                return ""
            
            summary = self.get_summary_table()
            lines = []
            
            # Header
            lines.append(",".join(summary["columns"]))
            
            # Rows
            for row in summary["rows"]:
                values = [str(row.get(col, "")) for col in summary["columns"]]
                lines.append(",".join(values))
            
            return "\n".join(lines)
        
        else:
            logger.warning(f"Unknown export format: {format}")
            return ""
    
    def clear(self):
        """Clear all candidates and data."""
        self.candidates = []
        self.jd_text = None
        logger.info("Cleared all candidates")


def extract_pdf_from_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes.
    
    Args:
        pdf_bytes: PDF file content as bytes
    
    Returns:
        str: Extracted text
    """
    from io import BytesIO
    from PyPDF2 import PdfReader
    
    try:
        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        return ""
