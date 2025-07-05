from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from config.settings import CHROME_DRIVER_PATH
import time

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self, headless: bool = True):
        self.driver = self._setup_driver(headless)
        
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """Setup Chrome driver with options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if CHROME_DRIVER_PATH:
            service = Service(CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    @abstractmethod
    def scrape_jobs(self, search_query: str, location: str, num_jobs: int = 100) -> List[Dict[str, Any]]:
        """Scrape jobs from the platform"""
        pass
    
    @abstractmethod
    def parse_job_details(self, job_element) -> Dict[str, Any]:
        """Parse individual job details"""
        pass
    
    def scroll_page(self, pause_time: float = 2):
        """Scroll down the page to load more content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()