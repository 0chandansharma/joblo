------------
# JobLo - Intelligent Job Assistant & Recommendation System

An AI-powered job intelligence system that scrapes job postings, provides intelligent recommendations, and matches jobs to user resumes.

## Features

1. **Job Scraper**: Extracts job postings from Naukri and LinkedIn
2. **AI Chat Assistant**: Natural language interface for job queries using LangChain
3. **Job Scoring Engine**: Scores and ranks jobs based on resume match
4. **Smart Recommendations**: Suggests similar and better-fit jobs
5. **Web & CLI Interfaces**: Both command-line and web-based interfaces

## Installation

### Quick Setup (Recommended)
```bash
git clone <repository-url>
cd joblo-assistant
./setup.sh
```

### Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd joblo-assistant
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations:
# - Add your OpenAI API key
# - Configure MongoDB connection (optional, defaults to localhost)
```

5. Install MongoDB (if not already installed):
```bash
# macOS
brew install mongodb-community

# Ubuntu
sudo apt-get install mongodb

# Start MongoDB
mongod
```

6. Setup the database:
```bash
python main.py setup
```

### Prerequisites
- Python 3.8+
- MongoDB (can be local or cloud)
- OpenAI API key
- Chrome browser (for web scraping)

## Usage

### 1. Scrape Jobs

Scrape jobs from Naukri and LinkedIn:

```bash
python main.py scrape --query "data scientist" --location "Mumbai" --num-jobs 50
```

Options:
- `--query`: Job search query (default: "software engineer")
- `--location`: Job location (default: "Bangalore")
- `--num-jobs`: Number of jobs per platform (default: 100)

### 2. CLI Chat Assistant

Launch the interactive chat interface:

```bash
python main.py chat
```

Example queries:
- "Find remote data scientist jobs in Bangalore"
- "Show me Python developer positions"
- "What jobs are available for freshers?"

### 3. Score Jobs Against Resume

Score and rank jobs based on your resume:

```bash
python main.py score path/to/resume.pdf --top-k 10
```

Options:
- `resume`: Path to resume file (PDF/DOCX/TXT)
- `--top-k`: Number of top matches to show (default: 5)

### 4. Web Application

Launch the Streamlit web interface:

```bash
python main.py web
```

Then open http://localhost:8501 in your browser.

## Web Application Features

### Job Search Page
- Search jobs by keyword, location, and source
- View job details and descriptions
- Direct links to apply

### Job Scoring Page
- Upload your resume
- Get top job matches with scores
- See matching/missing skills
- Detailed reasoning for each match

### Job Details Page
- View complete job information
- Get similar job recommendations
- Upload resume for better matches
- See why jobs are recommended

### Chat Assistant Page
- Natural language job queries
- Conversational interface
- Job search and filtering

## Architecture

### Project Structure
```
joblo-assistant/
   scrapers/          # Job scraping modules
   agents/            # LangChain AI agent
   scoring/           # Resume parsing and job scoring
   recommendations/   # Job recommendation engine
   utils/             # Database and utilities
   models/            # Data models
   config/            # Configuration
   main.py           # CLI entry point
   web_app.py        # Streamlit web app
```

### Technologies Used
- **Scraping**: Selenium, BeautifulSoup
- **AI/NLP**: LangChain, OpenAI GPT
- **ML**: scikit-learn (TF-IDF, cosine similarity)
- **Database**: MongoDB
- **Web**: Streamlit, FastAPI
- **Resume Parsing**: pdfplumber, python-docx

## Sample Input/Output

### Scraping Output
```json
{
  "naukri": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Company",
      "location": "Bangalore",
      "experience": "5-8 years",
      "skills": ["Python", "Django", "AWS"],
      "job_description": "...",
      "url": "https://..."
    }
  ]
}
```

### Scoring Output
```
Top 5 Job Matches:
1. Python Developer at ABC Corp
   Score: 85.5%
   Matching Skills: Python, Django, REST API
   Reasoning: Strong skill match | Experience level aligns well
```

## Assumptions & Limitations

1. **Scraping Limitations**:
   - LinkedIn has strict anti-scraping measures; uses public job pages only
   - Scraping may be rate-limited or blocked
   - Requires ChromeDriver for Selenium

2. **AI Agent**:
   - Requires OpenAI API key
   - Quality depends on scraped data availability
   - Uses GPT-3.5 by default (configurable)

3. **Resume Parsing**:
   - Best results with well-formatted resumes
   - Supports PDF, DOCX, and TXT formats
   - May not extract all information from complex layouts

4. **Database**:
   - Requires MongoDB running locally or configured connection
   - Creates indexes for text search functionality

## Future Enhancements

1. Add more job platforms (Indeed, Glassdoor, etc.)
2. Implement user authentication and profiles
3. Add email notifications for new matches
4. Enhance resume parsing with ML models
5. Add application tracking features
6. Implement real-time job alerts

## Troubleshooting

### Common Issues

1. **NumPy/SciPy Compatibility Error** (`numpy.core.multiarray failed to import`):
   ```bash
   # Solution: Downgrade NumPy to compatible version
   pip uninstall numpy scipy scikit-learn -y
   pip install "numpy>=1.21.6,<2.0" "scipy<1.12" "scikit-learn<1.4"
   ```

2. **Basic Functionality Test**: Run the simple demo first:
   ```bash
   python simple_demo.py
   ```

3. **Selenium Issues**: Install ChromeDriver and ensure it's in PATH

4. **MongoDB Connection**: Ensure MongoDB is running on default port 27017

5. **OpenAI API**: Verify API key is set correctly in .env

6. **Memory Issues**: Reduce number of jobs scraped if running out of memory

7. **LangChain Deprecation Warnings**: The code uses updated LangChain imports. If you see deprecation warnings, ensure you have the latest versions installed:
   ```bash
   pip install --upgrade langchain langchain-openai langchain-community
   ```

8. **Pydantic Errors**: If you encounter Pydantic field annotation errors, make sure you're using Python 3.8+ and have the latest versions of dependencies

### Installation Options

- **Minimal Installation** (basic functionality): `pip install -r requirements-minimal.txt`
- **Full Installation** (with ML features): `pip install -r requirements.txt`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is for demonstration purposes.
