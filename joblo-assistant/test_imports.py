#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

def test_core_imports():
    """Test basic imports that don't require sklearn"""
    try:
        from utils.database import DatabaseManager
        print("✓ Database utilities imported successfully")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False
    
    try:
        from models.job import Job
        from models.resume import Resume
        print("✓ Data models imported successfully")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    try:
        from scrapers.naukri_scraper import NaukriScraper
        from scrapers.linkedin_scraper import LinkedInScraper
        print("✓ Scrapers imported successfully")
    except Exception as e:
        print(f"✗ Scrapers import failed: {e}")
        return False
    
    try:
        from scoring.resume_parser import ResumeParser
        print("✓ Resume parser imported successfully")
    except Exception as e:
        print(f"✗ Resume parser import failed: {e}")
        return False
    
    return True

def test_sklearn_imports():
    """Test sklearn-dependent imports"""
    try:
        from scoring.job_scorer import JobScorer
        print("✓ Job scorer imported successfully")
    except Exception as e:
        print(f"✗ Job scorer import failed: {e}")
        return False
    
    try:
        from recommendations.job_recommender import JobRecommender
        print("✓ Job recommender imported successfully")
    except Exception as e:
        print(f"✗ Job recommender import failed: {e}")
        return False
    
    return True

def test_ai_imports():
    """Test AI-related imports"""
    try:
        from agents.job_agent import JobAgent
        print("✓ AI agent imported successfully")
    except Exception as e:
        print(f"✗ AI agent import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing JobLo Assistant imports...\n")
    
    print("=== Core Components ===")
    core_ok = test_core_imports()
    
    print("\n=== AI Components ===")
    ai_ok = test_ai_imports()
    
    print("\n=== ML Components (sklearn) ===")
    ml_ok = test_sklearn_imports()
    
    print("\n=== Summary ===")
    if core_ok and ai_ok and ml_ok:
        print("✓ All imports successful! System is ready to use.")
    elif core_ok and ai_ok:
        print("⚠ Core and AI components work, but ML components need numpy/sklearn fix")
        print("  Run: pip install --upgrade numpy scipy scikit-learn")
    else:
        print("✗ Some critical components failed to import")
        print("  Please check your environment and dependencies")