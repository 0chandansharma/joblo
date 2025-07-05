from typing import List, Dict, Any
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_scraper import BaseScraper
from models.job import Job
import logging
import re

logger = logging.getLogger(__name__)


class NaukriScraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.base_url = "https://www.naukri.com"
        
    def scrape_jobs(self, search_query: str = "software engineer", location: str = "bangalore", num_jobs: int = 100) -> List[Job]:
        """Scrape jobs from Naukri"""
        jobs = []
        try:
            search_url = f"{self.base_url}/{search_query.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}"
            logger.info(f"Scraping Naukri: {search_url}")
            self.driver.get(search_url)
            
            wait = WebDriverWait(self.driver, 10)
            
            page = 1
            while len(jobs) < num_jobs:
                try:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "srp-jobtuple-wrapper")))
                    
                    job_elements = self.driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
                    
                    for element in job_elements:
                        if len(jobs) >= num_jobs:
                            break
                        try:
                            job_data = self.parse_job_details(element)
                            if job_data:
                                job = Job(**job_data, source="naukri")
                                jobs.append(job)
                                logger.info(f"Scraped job: {job.title} at {job.company}")
                        except Exception as e:
                            logger.error(f"Error parsing job: {e}")
                            continue
                    
                    try:
                        next_button = self.driver.find_element(By.XPATH, "//a[@class='fright fs14 btn-secondary br2']")
                        if "disabled" in next_button.get_attribute("class"):
                            break
                        next_button.click()
                        page += 1
                        wait.until(EC.staleness_of(job_elements[0]))
                    except NoSuchElementException:
                        logger.info("No more pages available")
                        break
                        
                except TimeoutException:
                    logger.error("Timeout waiting for jobs to load")
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping Naukri: {e}")
            
        return jobs
    
    def parse_job_details(self, job_element) -> Dict[str, Any]:
        """Parse individual job details from Naukri"""
        try:
            title = job_element.find_element(By.CLASS_NAME, "title").text.strip()
            
            company = job_element.find_element(By.CLASS_NAME, "comp-name").text.strip()
            
            try:
                experience = job_element.find_element(By.CLASS_NAME, "exp-wrap").text.strip()
            except:
                experience = "Not specified"
            
            try:
                salary = job_element.find_element(By.CLASS_NAME, "sal-wrap").text.strip()
            except:
                salary = None
            
            try:
                location = job_element.find_element(By.CLASS_NAME, "locWdth").text.strip()
            except:
                location = "Not specified"
            
            try:
                description = job_element.find_element(By.CLASS_NAME, "job-desc").text.strip()
            except:
                description = ""
            
            try:
                skills_elements = job_element.find_elements(By.CLASS_NAME, "tag-li")
                skills = [skill.text.strip() for skill in skills_elements]
            except:
                skills = []
            
            try:
                posted_text = job_element.find_element(By.CLASS_NAME, "job-post-day").text.strip()
                posted_date = self._parse_posted_date(posted_text)
            except:
                posted_date = None
            
            try:
                url_element = job_element.find_element(By.CLASS_NAME, "title")
                url = url_element.get_attribute("href")
            except:
                url = ""
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "experience": experience,
                "skills": skills,
                "job_description": description,
                "posted_date": posted_date,
                "url": url,
                "salary": salary
            }
            
        except Exception as e:
            logger.error(f"Error parsing job details: {e}")
            return None
    
    def _parse_posted_date(self, posted_text: str) -> datetime:
        """Parse posted date from text like 'Posted 2 days ago'"""
        try:
            if "today" in posted_text.lower():
                return datetime.now()
            elif "yesterday" in posted_text.lower():
                return datetime.now() - timedelta(days=1)
            else:
                match = re.search(r'(\d+)\s*days?\s*ago', posted_text.lower())
                if match:
                    days_ago = int(match.group(1))
                    return datetime.now() - timedelta(days=days_ago)
                    
                match = re.search(r'(\d+)\s*months?\s*ago', posted_text.lower())
                if match:
                    months_ago = int(match.group(1))
                    return datetime.now() - timedelta(days=months_ago * 30)
                    
            return datetime.now()
        except:
            return datetime.now()