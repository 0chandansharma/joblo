from typing import List, Dict, Any
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_scraper import BaseScraper
from models.job import Job
import logging
import time
import re

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.base_url = "https://www.linkedin.com/jobs/search"
        
    def scrape_jobs(self, search_query: str = "software engineer", location: str = "Bangalore", num_jobs: int = 100) -> List[Job]:
        """Scrape jobs from LinkedIn (public jobs page - no login required)"""
        jobs = []
        try:
            search_url = f"{self.base_url}?keywords={search_query.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
            logger.info(f"Scraping LinkedIn: {search_url}")
            self.driver.get(search_url)
            
            wait = WebDriverWait(self.driver, 10)
            
            scroll_attempts = 0
            max_scrolls = 10
            
            while len(jobs) < num_jobs and scroll_attempts < max_scrolls:
                try:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list")))
                    
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.base-card")
                    
                    for element in job_elements:
                        if len(jobs) >= num_jobs:
                            break
                        try:
                            job_data = self.parse_job_details(element)
                            if job_data:
                                job = Job(**job_data, source="linkedin")
                                jobs.append(job)
                                logger.info(f"Scraped job: {job.title} at {job.company}")
                        except Exception as e:
                            logger.error(f"Error parsing job: {e}")
                            continue
                    
                    self.scroll_page(pause_time=3)
                    scroll_attempts += 1
                    
                    try:
                        see_more_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'See more jobs')]")
                        see_more_button.click()
                        time.sleep(2)
                    except NoSuchElementException:
                        pass
                        
                except TimeoutException:
                    logger.error("Timeout waiting for jobs to load")
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
            
        return jobs
    
    def parse_job_details(self, job_element) -> Dict[str, Any]:
        """Parse individual job details from LinkedIn"""
        try:
            title_element = job_element.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
            title = title_element.text.strip()
            
            company_element = job_element.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
            company = company_element.text.strip()
            
            location_element = job_element.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
            location = location_element.text.strip()
            
            try:
                time_element = job_element.find_element(By.CSS_SELECTOR, "time")
                posted_text = time_element.get_attribute("datetime")
                posted_date = datetime.fromisoformat(posted_text.replace('Z', '+00:00'))
            except:
                posted_date = None
            
            url_element = job_element.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
            url = url_element.get_attribute("href")
            
            try:
                list_elements = job_element.find_elements(By.CSS_SELECTOR, "li.job-search-card__list-item")
                job_info = [elem.text.strip() for elem in list_elements]
                
                experience = "Not specified"
                job_type = None
                for info in job_info:
                    if "years" in info.lower() or "entry" in info.lower() or "senior" in info.lower():
                        experience = info
                    elif any(t in info.lower() for t in ["full-time", "part-time", "contract", "internship"]):
                        job_type = info
            except:
                experience = "Not specified"
                job_type = None
            
            job_description = f"{title} position at {company} in {location}"
            
            skills = []
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "experience": experience,
                "skills": skills,
                "job_description": job_description,
                "posted_date": posted_date,
                "url": url,
                "job_type": job_type
            }
            
        except Exception as e:
            logger.error(f"Error parsing LinkedIn job details: {e}")
            return None