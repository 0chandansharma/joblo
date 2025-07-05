from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from config.settings import MONGODB_URI, MONGODB_DB_NAME
from models.job import Job
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB_NAME]
        self.jobs_collection = self.db.jobs
        self.resumes_collection = self.db.resumes
        
    def insert_job(self, job: Job) -> str:
        """Insert a single job into the database"""
        try:
            result = self.jobs_collection.insert_one(job.dict())
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting job: {e}")
            raise
    
    def insert_jobs(self, jobs: List[Job]) -> List[str]:
        """Insert multiple jobs into the database"""
        try:
            result = self.jobs_collection.insert_many([job.dict() for job in jobs])
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Error inserting jobs: {e}")
            raise
    
    def find_jobs(self, query: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find jobs based on query"""
        cursor = self.jobs_collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    def find_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find a single job by ID"""
        from bson import ObjectId
        return self.jobs_collection.find_one({"_id": ObjectId(job_id)})
    
    def update_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a job"""
        from bson import ObjectId
        result = self.jobs_collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs from the database"""
        return list(self.jobs_collection.find())
    
    def search_jobs(self, text: str) -> List[Dict[str, Any]]:
        """Search jobs using text search"""
        return list(self.jobs_collection.find(
            {"$text": {"$search": text}}
        ))
    
    def create_indexes(self):
        """Create necessary indexes for better performance"""
        self.jobs_collection.create_index([("title", "text"), ("job_description", "text"), ("skills", "text")])
        self.jobs_collection.create_index("source")
        self.jobs_collection.create_index("posted_date")
        
    def close(self):
        """Close database connection"""
        self.client.close()