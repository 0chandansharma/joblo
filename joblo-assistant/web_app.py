import streamlit as st
from typing import Optional
import pandas as pd
from utils.database import DatabaseManager
from recommendations.job_recommender import JobRecommender
from scoring.job_scorer import JobScorer
from scoring.resume_parser import ResumeParser
from agents.job_agent import JobAgent
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
@st.cache_resource
def init_components():
    db = DatabaseManager()
    recommender = JobRecommender()
    scorer = JobScorer()
    agent = JobAgent()
    return db, recommender, scorer, agent

def main():
    st.set_page_config(
        page_title="JobLo - Intelligent Job Assistant",
        page_icon="💼",
        layout="wide"
    )
    
    db, recommender, scorer, agent = init_components()
    
    # Sidebar
    with st.sidebar:
        st.title("JobLo Assistant 🤖")
        page = st.selectbox(
            "Navigation",
            ["Job Search", "Job Scoring", "Job Details", "Chat Assistant"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("JobLo is an intelligent job assistant that helps you find and match jobs based on your profile.")
    
    # Main content
    if page == "Job Search":
        show_job_search(db)
    elif page == "Job Scoring":
        show_job_scoring(db, scorer)
    elif page == "Job Details":
        show_job_details(db, recommender)
    elif page == "Chat Assistant":
        show_chat_assistant(agent)

def show_job_search(db):
    st.title("Job Search 🔍")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("Search Query", "software engineer")
    with col2:
        location = st.text_input("Location", "Bangalore")
    with col3:
        source_filter = st.selectbox("Source", ["All", "Naukri", "LinkedIn"])
    
    if st.button("Search Jobs"):
        with st.spinner("Searching jobs..."):
            query = {}
            if search_query:
                query["$text"] = {"$search": search_query}
            if location and location.lower() != "all":
                query["location"] = {"$regex": location, "$options": "i"}
            if source_filter != "All":
                query["source"] = source_filter.lower()
            
            jobs = db.find_jobs(query, limit=20)
            
            if jobs:
                st.success(f"Found {len(jobs)} jobs")
                
                for job in jobs:
                    with st.expander(f"{job['title']} at {job['company']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Location:** {job['location']}")
                            st.write(f"**Experience:** {job['experience']}")
                            st.write(f"**Source:** {job['source']}")
                        with col2:
                            if job.get('skills'):
                                st.write(f"**Skills:** {', '.join(job['skills'][:5])}")
                            if job.get('salary'):
                                st.write(f"**Salary:** {job['salary']}")
                        
                        st.write(f"**Description:** {job['job_description'][:200]}...")
                        st.write(f"[View Full Job]({job['url']})")
                        
                        if st.button(f"View Details", key=f"detail_{job['_id']}"):
                            st.session_state['selected_job_id'] = str(job['_id'])
                            st.rerun()
            else:
                st.warning("No jobs found matching your criteria")

def show_job_scoring(db, scorer):
    st.title("Job Scoring Engine 📊")
    
    uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        if st.button("Score Jobs"):
            with st.spinner("Analyzing resume and scoring jobs..."):
                try:
                    # Parse resume
                    parser = ResumeParser()
                    resume = parser.parse_resume(tmp_path)
                    
                    # Display resume summary
                    st.subheader("Resume Summary")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {resume.name or 'Not found'}")
                        st.write(f"**Email:** {resume.email or 'Not found'}")
                        st.write(f"**Experience:** {resume.experience_years or 'Not found'} years")
                    with col2:
                        st.write(f"**Skills:** {', '.join(resume.skills[:10])}")
                        if resume.preferred_locations:
                            st.write(f"**Preferred Locations:** {', '.join(resume.preferred_locations)}")
                    
                    # Get top job matches
                    results = scorer.get_top_job_matches(tmp_path, limit=5)
                    
                    st.subheader("Top Job Matches")
                    for i, result in enumerate(results, 1):
                        job = result['job']
                        score_details = result['score_details']
                        
                        with st.expander(f"{i}. {job['title']} at {job['company']} - Score: {score_details['score']}%"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Location:** {job['location']}")
                                st.write(f"**Experience:** {job['experience']}")
                                st.write(f"**Matching Skills:** {', '.join(score_details['matching_skills'])}")
                            with col2:
                                st.write(f"**Missing Skills:** {', '.join(score_details['missing_skills'])}")
                                st.write(f"**Experience Match:** {'✅' if score_details['experience_match'] else '❌'}")
                                st.write(f"**Location Match:** {'✅' if score_details['location_match'] else '❌'}")
                            
                            st.write(f"**Reasoning:** {score_details['reasoning']}")
                            st.write(f"[View Job]({job['url']})")
                    
                except Exception as e:
                    st.error(f"Error processing resume: {str(e)}")
        
        # Clean up temp file
        import os
        if 'tmp_path' in locals():
            os.unlink(tmp_path)

def show_job_details(db, recommender):
    st.title("Job Details & Recommendations 🎯")
    
    job_id = st.session_state.get('selected_job_id')
    
    if not job_id:
        st.info("Please select a job from the Job Search page first")
        return
    
    job = db.find_job_by_id(job_id)
    if not job:
        st.error("Job not found")
        return
    
    # Display job details
    st.subheader(f"{job['title']} at {job['company']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Location:** {job['location']}")
        st.write(f"**Experience:** {job['experience']}")
    with col2:
        st.write(f"**Source:** {job['source']}")
        if job.get('salary'):
            st.write(f"**Salary:** {job['salary']}")
    with col3:
        if job.get('posted_date'):
            st.write(f"**Posted:** {job['posted_date']}")
    
    if job.get('skills'):
        st.write(f"**Required Skills:** {', '.join(job['skills'])}")
    
    st.write(f"**Job Description:**")
    st.write(job['job_description'])
    
    st.write(f"[Apply on Original Site]({job['url']})")
    
    st.markdown("---")
    
    # Get recommendations
    st.subheader("Recommended Similar Jobs")
    
    with st.spinner("Finding similar jobs..."):
        similar_jobs = recommender.get_similar_jobs(job_id, num_recommendations=5)
        
        if similar_jobs:
            for rec in similar_jobs:
                sim_job = rec['job']
                with st.expander(f"{sim_job['title']} at {sim_job['company']} - Similarity: {rec['similarity_score']*100:.1f}%"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Location:** {sim_job['location']}")
                        st.write(f"**Experience:** {sim_job['experience']}")
                    with col2:
                        if sim_job.get('skills'):
                            st.write(f"**Skills:** {', '.join(sim_job['skills'][:5])}")
                    
                    st.write(f"**Why Similar:** {rec['reasoning']}")
                    st.write(f"[View Job]({sim_job['url']})")
        else:
            st.info("No similar jobs found")
    
    # Option to find better matches with resume
    st.markdown("---")
    st.subheader("Find Better Matches")
    
    uploaded_resume = st.file_uploader("Upload your resume to find better matches", type=['pdf', 'docx', 'txt'], key="resume_detail")
    
    if uploaded_resume and st.button("Find Better Matches"):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_resume.name) as tmp_file:
            tmp_file.write(uploaded_resume.getbuffer())
            tmp_path = tmp_file.name
        
        with st.spinner("Finding better matches..."):
            try:
                parser = ResumeParser()
                resume = parser.parse_resume(tmp_path)
                
                better_matches = recommender.get_better_matches(job_id, resume, num_recommendations=5)
                
                if better_matches:
                    st.success(f"Found {len(better_matches)} better matches!")
                    
                    for match in better_matches:
                        better_job = match['job']
                        score_details = match['score_details']
                        
                        with st.expander(f"{better_job['title']} at {better_job['company']} - Score: {score_details['score']}% (+{match['improvement']}%)"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Location:** {better_job['location']}")
                                st.write(f"**Matching Skills:** {', '.join(score_details['matching_skills'])}")
                            with col2:
                                st.write(f"**Score Improvement:** +{match['improvement']}%")
                                st.write(f"**Experience Match:** {'✅' if score_details['experience_match'] else '❌'}")
                            
                            st.write(f"**Why Better:** {score_details['reasoning']}")
                            st.write(f"[View Job]({better_job['url']})")
                else:
                    st.info("This job is already one of your best matches!")
                    
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
        
        # Clean up
        import os
        os.unlink(tmp_path)

def show_chat_assistant(agent):
    st.title("JobLo Chat Assistant 💬")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about jobs..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.chat(prompt)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()