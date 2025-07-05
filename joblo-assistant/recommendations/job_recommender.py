from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from utils.database import DatabaseManager
from models.resume import Resume
from scoring.job_scorer import JobScorer
import logging

logger = logging.getLogger(__name__)


class JobRecommender:
    def __init__(self):
        self.db = DatabaseManager()
        self.scorer = JobScorer()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    def get_similar_jobs(self, job_id: str, num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get similar jobs based on a given job"""
        try:
            # Get the reference job
            reference_job = self.db.find_job_by_id(job_id)
            if not reference_job:
                logger.error(f"Job not found: {job_id}")
                return []
            
            # Get all jobs
            all_jobs = self.db.get_all_jobs()
            
            # Filter out the reference job
            other_jobs = [job for job in all_jobs if str(job['_id']) != job_id]
            
            if not other_jobs:
                return []
            
            # Create text representations for all jobs
            reference_text = self._create_job_text(reference_job)
            job_texts = [self._create_job_text(job) for job in other_jobs]
            
            # Fit and transform
            all_texts = [reference_text] + job_texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            # Get top similar jobs
            top_indices = np.argsort(similarities)[::-1][:num_recommendations]
            
            recommendations = []
            for idx in top_indices:
                job = other_jobs[idx]
                similarity_score = similarities[idx]
                
                recommendation = {
                    "job": job,
                    "similarity_score": round(float(similarity_score), 3),
                    "reasoning": self._generate_similarity_reasoning(reference_job, job, similarity_score)
                }
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting similar jobs: {e}")
            return []
    
    def get_better_matches(self, job_id: str, resume: Resume, num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get jobs that are better matches for the resume than the current job"""
        try:
            # Get the reference job
            reference_job = self.db.find_job_by_id(job_id)
            if not reference_job:
                return []
            
            # Score the reference job
            reference_score = self.scorer._calculate_job_score(resume, reference_job)
            
            # Get all jobs and score them
            all_jobs = self.db.get_all_jobs()
            scored_jobs = []
            
            for job in all_jobs:
                if str(job['_id']) != job_id:
                    score_data = self.scorer._calculate_job_score(resume, job)
                    # Only include jobs with better scores
                    if score_data['score'] > reference_score['score']:
                        scored_jobs.append({
                            "job": job,
                            "score_details": score_data,
                            "improvement": round(score_data['score'] - reference_score['score'], 2)
                        })
            
            # Sort by score descending
            scored_jobs.sort(key=lambda x: x['score_details']['score'], reverse=True)
            
            return scored_jobs[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting better matches: {e}")
            return []
    
    def recommend_jobs_for_profile(self, job_id: str, resume_path: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive job recommendations based on current job and optional resume"""
        recommendations = {
            "similar_jobs": [],
            "better_matches": []
        }
        
        # Get similar jobs
        similar_jobs = self.get_similar_jobs(job_id, num_recommendations=5)
        recommendations["similar_jobs"] = similar_jobs
        
        # If resume is provided, get better matches
        if resume_path:
            from scoring.resume_parser import ResumeParser
            parser = ResumeParser()
            resume = parser.parse_resume(resume_path)
            
            better_matches = self.get_better_matches(job_id, resume, num_recommendations=5)
            recommendations["better_matches"] = better_matches
        
        return recommendations
    
    def _create_job_text(self, job: Dict[str, Any]) -> str:
        """Create text representation of a job for similarity calculation"""
        parts = [
            job.get('title', ''),
            job.get('company', ''),
            job.get('location', ''),
            job.get('job_description', ''),
            ' '.join(job.get('skills', [])),
            job.get('experience', '')
        ]
        return ' '.join(filter(None, parts))
    
    def _generate_similarity_reasoning(self, reference_job: Dict[str, Any], 
                                     similar_job: Dict[str, Any], 
                                     similarity_score: float) -> str:
        """Generate reasoning for why jobs are similar"""
        reasons = []
        
        # Compare titles
        if reference_job.get('title', '').lower() == similar_job.get('title', '').lower():
            reasons.append("Same job title")
        elif any(word in similar_job.get('title', '').lower() 
                for word in reference_job.get('title', '').lower().split()):
            reasons.append("Similar job title")
        
        # Compare skills
        ref_skills = set(skill.lower() for skill in reference_job.get('skills', []))
        sim_skills = set(skill.lower() for skill in similar_job.get('skills', []))
        common_skills = ref_skills & sim_skills
        
        if common_skills:
            reasons.append(f"Common skills: {', '.join(list(common_skills)[:3])}")
        
        # Compare location
        if reference_job.get('location', '').lower() == similar_job.get('location', '').lower():
            reasons.append("Same location")
        
        # Compare experience
        if reference_job.get('experience', '') == similar_job.get('experience', ''):
            reasons.append("Same experience level")
        
        # Similarity score
        if similarity_score > 0.7:
            reasons.append("Very high content similarity")
        elif similarity_score > 0.5:
            reasons.append("High content similarity")
        else:
            reasons.append("Moderate content similarity")
        
        return " | ".join(reasons) if reasons else "Similar based on job content"