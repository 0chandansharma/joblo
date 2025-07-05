#!/usr/bin/env python3
"""
JobLo - Intelligent Job Assistant & Recommendation System
Main entry point for the application
"""

import argparse
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.scraper_manager import ScraperManager
from agents.cli_interface import JobAssistantCLI
from scoring.job_scorer import JobScorer
from utils.database import DatabaseManager
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_jobs(args):
    """Run the job scraping process"""
    logger.info("Starting job scraping process...")
    
    manager = ScraperManager()
    results = manager.run_scraping_job(
        search_query=args.query,
        location=args.location,
        num_jobs_per_platform=args.num_jobs,
        save_to_db=True,
        save_to_file=True
    )
    
    logger.info(f"Scraping completed: {results}")
    print(f"\nScraping Summary:")
    print(f"Total jobs scraped: {results['total_jobs']}")
    for platform, count in results['jobs_by_platform'].items():
        print(f"  {platform}: {count} jobs")
    if 'json_file' in results:
        print(f"\nJobs saved to: {results['json_file']}")


def run_cli_chat(args):
    """Run the CLI chat interface"""
    logger.info("Starting JobLo CLI Assistant...")
    cli = JobAssistantCLI()
    cli.run()


def score_resume(args):
    """Score jobs against a resume"""
    logger.info(f"Scoring jobs for resume: {args.resume}")
    
    if not Path(args.resume).exists():
        print(f"Error: Resume file not found: {args.resume}")
        return
    
    scorer = JobScorer()
    results = scorer.get_top_job_matches(args.resume, limit=args.top_k)
    
    print(f"\nTop {args.top_k} Job Matches:")
    print("-" * 80)
    
    for i, result in enumerate(results, 1):
        job = result['job']
        score_details = result['score_details']
        
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Score: {score_details['score']}%")
        print(f"   Location: {job['location']}")
        print(f"   Experience: {job['experience']}")
        print(f"   Matching Skills: {', '.join(score_details['matching_skills'][:5])}")
        print(f"   Reasoning: {score_details['reasoning']}")
        print(f"   URL: {job['url']}")


def run_web_app(args):
    """Run the Streamlit web application"""
    logger.info("Starting JobLo Web Application...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "web_app.py"])


def setup_database(args):
    """Setup database indexes"""
    logger.info("Setting up database...")
    db = DatabaseManager()
    db.create_indexes()
    logger.info("Database setup completed")


def main():
    parser = argparse.ArgumentParser(description="JobLo - Intelligent Job Assistant")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape jobs from Naukri and LinkedIn')
    scrape_parser.add_argument('--query', default='software engineer', help='Job search query')
    scrape_parser.add_argument('--location', default='Bangalore', help='Job location')
    scrape_parser.add_argument('--num-jobs', type=int, default=100, help='Number of jobs per platform')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Run the CLI chat interface')
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Score jobs against a resume')
    score_parser.add_argument('resume', help='Path to resume file (PDF/DOCX/TXT)')
    score_parser.add_argument('--top-k', type=int, default=5, help='Number of top matches to show')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Run the web application')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup database')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'scrape':
        scrape_jobs(args)
    elif args.command == 'chat':
        run_cli_chat(args)
    elif args.command == 'score':
        score_resume(args)
    elif args.command == 'web':
        run_web_app(args)
    elif args.command == 'setup':
        setup_database(args)


if __name__ == "__main__":
    main()