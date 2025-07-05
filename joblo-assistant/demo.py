#!/usr/bin/env python3
"""
Demo script to showcase JobLo functionality
"""

import logging
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.scraper_manager import ScraperManager
from scoring.job_scorer import JobScorer
from recommendations.job_recommender import JobRecommender
from utils.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f" {title} ")
    print("="*60 + "\n")


def demo_scraping():
    """Demo job scraping functionality"""
    print_section("JOB SCRAPING DEMO")
    
    print("This demo will scrape a small number of jobs for demonstration.")
    print("In production, you can scrape 100+ jobs from each platform.")
    
    input("\nPress Enter to start scraping...")
    
    manager = ScraperManager()
    
    # Scrape only 5 jobs for demo
    print("\nScraping 5 jobs from each platform...")
    results = manager.run_scraping_job(
        search_query="python developer",
        location="Bangalore",
        num_jobs_per_platform=5,
        save_to_db=True,
        save_to_file=True
    )
    
    print(f"\n✓ Scraping completed!")
    print(f"Total jobs scraped: {results['total_jobs']}")
    for platform, count in results['jobs_by_platform'].items():
        print(f"  - {platform}: {count} jobs")


def demo_job_scoring():
    """Demo job scoring functionality"""
    print_section("JOB SCORING DEMO")
    
    print("This demo will score jobs against the sample resume.")
    
    input("\nPress Enter to start scoring...")
    
    scorer = JobScorer()
    resume_path = "sample_resume.txt"
    
    if not Path(resume_path).exists():
        print(f"Error: Sample resume not found at {resume_path}")
        return
    
    print(f"\nScoring jobs for resume: {resume_path}")
    results = scorer.get_top_job_matches(resume_path, limit=3)
    
    print("\n✓ Scoring completed!")
    print("\nTop 3 Job Matches:")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        job = result['job']
        score_details = result['score_details']
        
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Score: {score_details['score']}%")
        print(f"   Location: {job['location']}")
        print(f"   Matching Skills: {', '.join(score_details['matching_skills'][:3])}")
        print(f"   Reasoning: {score_details['reasoning'][:100]}...")


def demo_recommendations():
    """Demo job recommendation functionality"""
    print_section("JOB RECOMMENDATIONS DEMO")
    
    print("This demo will show job recommendations based on a selected job.")
    
    input("\nPress Enter to see recommendations...")
    
    db = DatabaseManager()
    recommender = JobRecommender()
    
    # Get a sample job
    jobs = db.get_all_jobs()
    if not jobs:
        print("No jobs found in database. Please run scraping first.")
        return
    
    sample_job = jobs[0]
    job_id = str(sample_job['_id'])
    
    print(f"\nSelected Job: {sample_job['title']} at {sample_job['company']}")
    print(f"Location: {sample_job['location']}")
    
    # Get similar jobs
    print("\n\nFinding similar jobs...")
    similar_jobs = recommender.get_similar_jobs(job_id, num_recommendations=3)
    
    print("\n✓ Similar Jobs Found:")
    for i, rec in enumerate(similar_jobs, 1):
        job = rec['job']
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Similarity: {rec['similarity_score']*100:.1f}%")
        print(f"   Why: {rec['reasoning']}")


def demo_chat_interface():
    """Demo chat interface info"""
    print_section("CHAT INTERFACE")
    
    print("The JobLo Assistant provides a natural language interface for job queries.")
    print("\nTo start the chat interface, run:")
    print("  python main.py chat")
    print("\nExample queries you can try:")
    print("  - 'Find remote Python developer jobs'")
    print("  - 'Show me data science positions in Mumbai'")
    print("  - 'What jobs require AWS experience?'")
    print("  - 'Find entry-level software engineer roles'")


def demo_web_app():
    """Demo web app info"""
    print_section("WEB APPLICATION")
    
    print("JobLo also provides a full-featured web interface built with Streamlit.")
    print("\nTo start the web app, run:")
    print("  python main.py web")
    print("\nFeatures include:")
    print("  - Visual job search and filtering")
    print("  - Resume upload and scoring")
    print("  - Interactive job recommendations")
    print("  - Chat assistant integration")


def main():
    """Run the complete demo"""
    print("\n" + "*"*60)
    print("*" + " "*58 + "*")
    print("*" + " "*20 + "JOBLO DEMO" + " "*28 + "*")
    print("*" + " "*58 + "*")
    print("*"*60)
    
    print("\nWelcome to the JobLo Intelligent Job Assistant Demo!")
    print("\nThis demo will showcase the main features of the system.")
    
    try:
        # Check MongoDB connection
        db = DatabaseManager()
        db.create_indexes()
        
        # Run demos
        demo_scraping()
        time.sleep(2)
        
        demo_job_scoring()
        time.sleep(2)
        
        demo_recommendations()
        time.sleep(2)
        
        demo_chat_interface()
        time.sleep(2)
        
        demo_web_app()
        
        print("\n" + "*"*60)
        print("\n✓ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Try the chat interface: python main.py chat")
        print("2. Launch the web app: python main.py web")
        print("3. Score your own resume: python main.py score your_resume.pdf")
        print("\n" + "*"*60)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("\nMake sure:")
        print("1. MongoDB is running")
        print("2. Environment variables are set (.env file)")
        print("3. All dependencies are installed")


if __name__ == "__main__":
    main()