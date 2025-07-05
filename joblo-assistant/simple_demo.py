#!/usr/bin/env python3
"""
Simple demo that works without sklearn dependencies
Shows basic functionality of JobLo system
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def demo_basic_functionality():
    """Demo basic functionality that doesn't require sklearn"""
    print("="*60)
    print(" JOBLO BASIC FUNCTIONALITY DEMO ")
    print("="*60)
    
    # Test data models
    print("\n1. Testing Data Models...")
    try:
        from models.job import Job
        from models.resume import Resume
        
        # Create a sample job
        sample_job = Job(
            title="Python Developer",
            company="Tech Corp",
            location="Bangalore",
            experience="3-5 years",
            skills=["Python", "Django", "REST API"],
            job_description="Looking for a Python developer with Django experience",
            url="https://example.com/job/123",
            source="naukri"
        )
        
        print(f"✓ Created job: {sample_job.title} at {sample_job.company}")
        
        # Create a sample resume
        sample_resume = Resume(
            name="John Doe",
            email="john@email.com",
            skills=["Python", "Django", "JavaScript"],
            experience_years=4.0,
            education=["B.Tech Computer Science"],
            work_experience=[{"company": "Previous Corp"}],
            preferred_locations=["Bangalore", "Mumbai"],
            preferred_job_types=["Full-time"],
            raw_text="John Doe, Python developer with 4 years experience..."
        )
        
        print(f"✓ Created resume for: {sample_resume.name}")
        
    except Exception as e:
        print(f"✗ Data models test failed: {e}")
        return False
    
    # Test database connection
    print("\n2. Testing Database Connection...")
    try:
        from utils.database import DatabaseManager
        db = DatabaseManager()
        
        # Try to connect (this will fail if MongoDB is not running, but import should work)
        print("✓ Database manager created successfully")
        print("  Note: Actual MongoDB connection requires MongoDB to be running")
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False
    
    # Test resume parser (text only)
    print("\n3. Testing Resume Parser...")
    try:
        from scoring.resume_parser import ResumeParser
        parser = ResumeParser()
        
        # Test with our sample resume text file
        sample_resume_path = "sample_resume.txt"
        if Path(sample_resume_path).exists():
            resume = parser.parse_resume(sample_resume_path)
            print(f"✓ Parsed resume for: {resume.name}")
            print(f"  Skills found: {', '.join(resume.skills[:5])}...")
            print(f"  Experience: {resume.experience_years} years")
        else:
            print("  Sample resume file not found, skipping file parsing test")
            
    except Exception as e:
        print(f"✗ Resume parser test failed: {e}")
        return False
    
    # Test scraper components (import only)
    print("\n4. Testing Scraper Components...")
    try:
        from scrapers.naukri_scraper import NaukriScraper
        from scrapers.linkedin_scraper import LinkedInScraper
        from scrapers.scraper_manager import ScraperManager
        
        print("✓ Scraper components imported successfully")
        print("  Note: Actual scraping requires ChromeDriver and internet connection")
        
    except Exception as e:
        print(f"✗ Scraper test failed: {e}")
        return False
    
    return True

def demo_ai_components():
    """Demo AI components if available"""
    print("\n5. Testing AI Components...")
    try:
        from agents.job_agent import JobAgent
        print("✓ AI agent imported successfully")
        print("  Note: AI functionality requires OpenAI API key")
        return True
    except Exception as e:
        print(f"✗ AI components test failed: {e}")
        return False

def show_next_steps():
    """Show next steps for full setup"""
    print("\n" + "="*60)
    print(" NEXT STEPS FOR FULL FUNCTIONALITY ")
    print("="*60)
    
    print("\n1. Fix NumPy/SciPy compatibility:")
    print("   pip uninstall numpy scipy scikit-learn -y")
    print("   pip install numpy<2.0 scipy<1.12 scikit-learn<1.4")
    
    print("\n2. Install optional dependencies:")
    print("   pip install pdfplumber python-docx rich")
    
    print("\n3. Set up MongoDB:")
    print("   - Install MongoDB locally OR use MongoDB Atlas")
    print("   - Start MongoDB: mongod")
    
    print("\n4. Configure environment:")
    print("   - Copy .env.example to .env")
    print("   - Add your OpenAI API key to .env")
    
    print("\n5. Install ChromeDriver for web scraping:")
    print("   - Download from https://chromedriver.chromium.org/")
    print("   - Add to PATH or specify path in .env")
    
    print("\n6. Run the full demo:")
    print("   python demo.py")

if __name__ == "__main__":
    print("JobLo Assistant - Basic Demo")
    print("This demo tests core functionality without sklearn dependencies\n")
    
    # Test basic functionality
    basic_ok = demo_basic_functionality()
    
    # Test AI components
    ai_ok = demo_ai_components()
    
    # Show results
    print("\n" + "="*60)
    print(" DEMO RESULTS ")
    print("="*60)
    
    if basic_ok and ai_ok:
        print("✅ All basic components working!")
        print("✅ AI components ready!")
        print("\nYour JobLo system is ready for basic use.")
        print("For full ML functionality, fix the NumPy compatibility issue.")
    elif basic_ok:
        print("✅ Basic components working!")
        print("⚠️  AI components need setup (see next steps)")
    else:
        print("❌ Some basic components failed")
        print("Please check your Python environment")
    
    show_next_steps()