from typing import List, Dict, Any, Tuple
from models.job import Job, JobScore
from models.resume import Resume
from utils.database import DatabaseManager
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


class JobScorer:
    def __init__(self):
        self.db = DatabaseManager()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    def score_jobs(self, resume: Resume, jobs: List[Dict[str, Any]], top_k: int = 5) -> List[JobScore]:
        """Score all jobs against a resume and return top matches"""
        scores = []
        
        for job in jobs:
            score_data = self._calculate_job_score(resume, job)
            job_score = JobScore(
                job_id=str(job.get('_id', '')),
                resume_id="",  # Can be set if resume is stored
                **score_data
            )
            scores.append(job_score)
        
        # Sort by score descending
        scores.sort(key=lambda x: x.score, reverse=True)
        
        return scores[:top_k]
    
    def _calculate_job_score(self, resume: Resume, job: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate score for a single job against resume"""
        
        # Skill matching
        job_skills = [skill.lower() for skill in job.get('skills', [])]
        resume_skills = [skill.lower() for skill in resume.skills]
        
        matching_skills = list(set(resume_skills) & set(job_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))
        
        skill_score = (len(matching_skills) / max(len(job_skills), 1)) * 40
        
        # Experience matching
        experience_score = self._calculate_experience_score(resume, job)
        
        # Location matching
        location_match = self._check_location_match(resume, job)
        location_score = 10 if location_match else 0
        
        # Text similarity between resume and job description
        similarity_score = self._calculate_text_similarity(resume, job) * 30
        
        # Calculate total score
        total_score = skill_score + experience_score + location_score + similarity_score
        total_score = min(100, max(0, total_score))  # Ensure score is between 0-100
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            matching_skills, missing_skills, experience_score, 
            location_match, similarity_score, job
        )
        
        return {
            "score": round(total_score, 2),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills[:5],  # Top 5 missing skills
            "experience_match": experience_score > 10,
            "location_match": location_match,
            "reasoning": reasoning
        }
    
    def _calculate_experience_score(self, resume: Resume, job: Dict[str, Any]) -> float:
        """Calculate experience matching score (0-20 points)"""
        job_exp = job.get('experience', '')
        resume_exp = resume.experience_years or 0
        
        # Extract years from job requirement
        import re
        years_pattern = r'(\d+)[-\s]*(?:to|-)[-\s]*(\d+)'
        match = re.search(years_pattern, job_exp)
        
        if match:
            min_years = int(match.group(1))
            max_years = int(match.group(2))
            
            if min_years <= resume_exp <= max_years:
                return 20  # Perfect match
            elif resume_exp < min_years:
                # Under-qualified
                gap = min_years - resume_exp
                return max(0, 20 - (gap * 5))
            else:
                # Over-qualified
                gap = resume_exp - max_years
                return max(10, 20 - (gap * 2))
        else:
            # Try to extract single year requirement
            single_year = re.search(r'(\d+)\+?\s*years?', job_exp)
            if single_year:
                required_years = int(single_year.group(1))
                if resume_exp >= required_years:
                    return 20
                else:
                    gap = required_years - resume_exp
                    return max(0, 20 - (gap * 5))
        
        # No clear experience requirement
        return 10
    
    def _check_location_match(self, resume: Resume, job: Dict[str, Any]) -> bool:
        """Check if job location matches resume preferences"""
        job_location = job.get('location', '').lower()
        
        # Check for remote/work from home
        if any(term in job_location for term in ['remote', 'work from home', 'wfh']):
            return True
        
        # Check against preferred locations
        for pref_loc in resume.preferred_locations:
            if pref_loc.lower() in job_location:
                return True
        
        return False
    
    def _calculate_text_similarity(self, resume: Resume, job: Dict[str, Any]) -> float:
        """Calculate text similarity between resume and job description"""
        try:
            resume_text = resume.raw_text
            job_text = f"{job.get('title', '')} {job.get('job_description', '')} {' '.join(job.get('skills', []))}"
            
            # Fit and transform the texts
            tfidf_matrix = self.vectorizer.fit_transform([resume_text, job_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0
    
    def _generate_reasoning(self, matching_skills: List[str], missing_skills: List[str],
                          experience_score: float, location_match: bool, 
                          similarity_score: float, job: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the score"""
        reasons = []
        
        # Skills analysis
        if matching_skills:
            reasons.append(f"Strong skill match with {len(matching_skills)} relevant skills: {', '.join(matching_skills[:5])}")
        else:
            reasons.append("Limited skill overlap with job requirements")
        
        if missing_skills:
            reasons.append(f"Missing skills: {', '.join(missing_skills[:3])}")
        
        # Experience analysis
        if experience_score >= 15:
            reasons.append("Experience level aligns well with requirements")
        elif experience_score >= 10:
            reasons.append("Experience level is acceptable for this role")
        else:
            reasons.append("Experience level may not fully meet requirements")
        
        # Location analysis
        if location_match:
            reasons.append(f"Location preference matches ({job.get('location', 'Not specified')})")
        else:
            reasons.append("Location may require relocation or remote work")
        
        # Overall fit
        if similarity_score > 0.5:
            reasons.append("Strong overall profile match based on job description")
        elif similarity_score > 0.3:
            reasons.append("Moderate profile match with job requirements")
        
        return " | ".join(reasons)
    
    def get_top_job_matches(self, resume_path: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top job matches for a resume file"""
        from .resume_parser import ResumeParser
        
        # Parse resume
        parser = ResumeParser()
        resume = parser.parse_resume(resume_path)
        
        # Get all jobs from database
        jobs = self.db.get_all_jobs()
        
        if not jobs:
            logger.warning("No jobs found in database")
            return []
        
        # Score all jobs
        scored_jobs = self.score_jobs(resume, jobs, top_k=limit)
        
        # Enrich with job details
        results = []
        for job_score in scored_jobs:
            job = self.db.find_job_by_id(job_score.job_id)
            if job:
                results.append({
                    "job": job,
                    "score_details": job_score.dict()
                })
        
        return results