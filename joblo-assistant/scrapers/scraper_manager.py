from typing import List, Dict, Any
from .naukri_scraper import NaukriScraper
from .linkedin_scraper import LinkedInScraper
from models.job import Job
from utils.database import DatabaseManager
import logging
import json
from datetime import datetime
from config.settings import RAW_DATA_DIR

logger = logging.getLogger(__name__)


class ScraperManager:
    def __init__(self):
        self.db = DatabaseManager()
        
    def scrape_all_platforms(self, search_query: str = "software engineer", 
                           location: str = "Bangalore", 
                           num_jobs_per_platform: int = 100) -> Dict[str, List[Job]]:
        """Scrape jobs from all platforms"""
        all_jobs = {
            "naukri": [],
            "linkedin": []
        }
        
        logger.info("Starting Naukri scraping...")
        naukri_scraper = NaukriScraper(headless=True)
        try:
            naukri_jobs = naukri_scraper.scrape_jobs(search_query, location, num_jobs_per_platform)
            all_jobs["naukri"] = naukri_jobs
            logger.info(f"Scraped {len(naukri_jobs)} jobs from Naukri")
        except Exception as e:
            logger.error(f"Error scraping Naukri: {e}")
        finally:
            naukri_scraper.close()
        
        logger.info("Starting LinkedIn scraping...")
        linkedin_scraper = LinkedInScraper(headless=True)
        try:
            linkedin_jobs = linkedin_scraper.scrape_jobs(search_query, location, num_jobs_per_platform)
            all_jobs["linkedin"] = linkedin_jobs
            logger.info(f"Scraped {len(linkedin_jobs)} jobs from LinkedIn")
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        finally:
            linkedin_scraper.close()
        
        return all_jobs
    
    def save_to_database(self, jobs: Dict[str, List[Job]]) -> Dict[str, int]:
        """Save scraped jobs to MongoDB"""
        saved_counts = {}
        
        for platform, job_list in jobs.items():
            if job_list:
                try:
                    self.db.insert_jobs(job_list)
                    saved_counts[platform] = len(job_list)
                    logger.info(f"Saved {len(job_list)} jobs from {platform} to database")
                except Exception as e:
                    logger.error(f"Error saving {platform} jobs to database: {e}")
                    saved_counts[platform] = 0
            else:
                saved_counts[platform] = 0
                
        return saved_counts
    
    def save_to_json(self, jobs: Dict[str, List[Job]], filename: str = None) -> str:
        """Save scraped jobs to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_{timestamp}.json"
            
        filepath = RAW_DATA_DIR / filename
        
        jobs_dict = {}
        for platform, job_list in jobs.items():
            jobs_dict[platform] = [job.dict() for job in job_list]
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs_dict, f, indent=2, default=str)
            
        logger.info(f"Saved jobs to {filepath}")
        return str(filepath)
    
    def run_scraping_job(self, search_query: str = "software engineer", 
                        location: str = "Bangalore", 
                        num_jobs_per_platform: int = 100,
                        save_to_db: bool = True,
                        save_to_file: bool = True) -> Dict[str, Any]:
        """Run complete scraping job"""
        logger.info(f"Starting scraping job: query='{search_query}', location='{location}'")
        
        jobs = self.scrape_all_platforms(search_query, location, num_jobs_per_platform)
        
        total_jobs = sum(len(job_list) for job_list in jobs.values())
        logger.info(f"Total jobs scraped: {total_jobs}")
        
        results = {
            "total_jobs": total_jobs,
            "jobs_by_platform": {platform: len(job_list) for platform, job_list in jobs.items()}
        }
        
        if save_to_db:
            saved_counts = self.save_to_database(jobs)
            results["saved_to_db"] = saved_counts
            
        if save_to_file:
            json_path = self.save_to_json(jobs)
            results["json_file"] = json_path
            
        return results