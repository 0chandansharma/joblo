from typing import List, Optional
from pydantic import BaseModel


class Resume(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str]
    experience_years: Optional[float] = None
    education: List[str]
    work_experience: List[dict]
    preferred_locations: List[str]
    preferred_job_types: List[str]
    raw_text: str