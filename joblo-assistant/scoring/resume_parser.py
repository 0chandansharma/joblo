import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from models.resume import Resume

# Optional imports with graceful fallback
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)


class ResumeParser:
    def __init__(self):
        self.skill_keywords = self._load_skill_keywords()
        
    def _load_skill_keywords(self) -> List[str]:
        """Load common skill keywords"""
        return [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "kotlin", "swift",
            "php", "scala", "r", "matlab", "perl", "objective-c", "dart", "lua", "julia", "fortran",
            
            # Web Technologies
            "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "spring",
            "asp.net", "rails", "laravel", "symfony", "jquery", "bootstrap", "tailwind", "sass", "webpack",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
            "oracle", "sql server", "firebase", "neo4j", "influxdb", "couchdb",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "ci/cd", "terraform",
            "ansible", "puppet", "chef", "circleci", "travis ci", "gitlab", "bitbucket",
            
            # Data Science & ML
            "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "keras",
            "pandas", "numpy", "matplotlib", "seaborn", "nlp", "computer vision", "opencv",
            
            # Other Technologies
            "rest api", "graphql", "microservices", "agile", "scrum", "jira", "linux", "unix",
            "security", "blockchain", "iot", "mobile development", "android", "ios", "react native",
            "flutter", "xamarin", "unity", "unreal engine"
        ]
    
    def parse_resume(self, file_path: str) -> Resume:
        """Parse resume from file path"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        if file_path.suffix.lower() == '.pdf':
            if not PDF_AVAILABLE:
                raise ImportError("pdfplumber not available. Please install: pip install pdfplumber")
            text = self._extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            if not DOCX_AVAILABLE:
                raise ImportError("python-docx not available. Please install: pip install python-docx")
            text = self._extract_text_from_docx(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        return self._parse_resume_text(text)
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
        return text
    
    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
        return text
    
    def _parse_resume_text(self, text: str) -> Resume:
        """Parse resume information from text"""
        resume_data = {
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(text),
            "experience_years": self._extract_experience_years(text),
            "education": self._extract_education(text),
            "work_experience": self._extract_work_experience(text),
            "preferred_locations": self._extract_locations(text),
            "preferred_job_types": [],
            "raw_text": text
        }
        
        return Resume(**resume_data)
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from resume text"""
        lines = text.strip().split('\n')
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
                if not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum', 'vitae']):
                    return line
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from resume text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume text"""
        phone_patterns = [
            r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            if skill.lower() in text_lower:
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    found_skills.append(skill)
        
        skill_section_pattern = r'(?:skills|technical skills|core competencies)[:\s]*([^\\n]+(?:\\n[^\\n]+)*)'
        skill_match = re.search(skill_section_pattern, text, re.IGNORECASE)
        
        if skill_match:
            skill_text = skill_match.group(1)
            additional_skills = re.findall(r'[A-Za-z+#.]+(?:\s+[A-Za-z+#.]+)*', skill_text)
            for skill in additional_skills:
                if len(skill) > 2 and skill.lower() not in [s.lower() for s in found_skills]:
                    found_skills.append(skill)
        
        return list(set(found_skills))
    
    def _extract_experience_years(self, text: str) -> Optional[float]:
        """Extract years of experience from resume text"""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\s*years?\s*(?:of\s*)?professional\s*experience'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            years = [int(y) for y in years]
            experience = max(years) - min(years)
            if 0 < experience < 50:
                return float(experience)
        
        return None
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information from resume text"""
        education = []
        
        degree_patterns = [
            r'(?:bachelor|b\.?s\.?|b\.?tech|b\.?e\.?)[^\\n]{0,50}',
            r'(?:master|m\.?s\.?|m\.?tech|m\.?e\.?|mba)[^\\n]{0,50}',
            r'(?:phd|ph\.?d\.?|doctorate)[^\\n]{0,50}',
            r'(?:diploma|certification|certificate)[^\\n]{0,50}'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)
        
        return list(set(education))
    
    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text"""
        work_experience = []
        
        company_patterns = [
            r'(?:at|@)\s+([A-Za-z0-9\s&.,]+?)(?:\s*[-|]|\s*\n)',
            r'(?:company|employer)[:\s]+([A-Za-z0-9\s&.,]+?)(?:\s*\n)',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 2:
                    work_experience.append({"company": match.strip()})
        
        return work_experience
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract location preferences from resume text"""
        indian_cities = [
            "bangalore", "bengaluru", "mumbai", "delhi", "ncr", "gurgaon", "gurugram", "noida",
            "hyderabad", "chennai", "pune", "kolkata", "ahmedabad", "jaipur", "surat",
            "lucknow", "kanpur", "nagpur", "indore", "thane", "bhopal", "patna",
            "vadodara", "ghaziabad", "ludhiana", "agra", "nashik", "faridabad",
            "meerut", "rajkot", "varanasi", "srinagar", "aurangabad", "dhanbad",
            "amritsar", "allahabad", "ranchi", "howrah", "coimbatore", "vijayawada",
            "jodhpur", "madurai", "raipur", "kota", "guwahati", "chandigarh"
        ]
        
        locations = []
        text_lower = text.lower()
        
        for city in indian_cities:
            if city in text_lower:
                locations.append(city.title())
        
        return list(set(locations))