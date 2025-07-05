from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Job(BaseModel):
    title: str
    company: str
    location: str
    experience: str
    skills: List[str]
    job_description: str
    posted_date: Optional[datetime] = None
    url: str
    source: str  # 'naukri' or 'linkedin'
    salary: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class JobScore(BaseModel):
    job_id: str
    resume_id: str
    score: float = Field(ge=0, le=100)
    matching_skills: List[str]
    missing_skills: List[str]
    experience_match: bool
    location_match: bool
    reasoning: str