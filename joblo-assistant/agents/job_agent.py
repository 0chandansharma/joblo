from typing import List, Dict, Any, Optional, Type
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import json
from utils.database import DatabaseManager
from config.settings import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)


class JobSearchInput(BaseModel):
    query: str = Field(description="The search query for jobs")
    location: Optional[str] = Field(default=None, description="Location filter")
    skills: Optional[List[str]] = Field(default=None, description="Skills filter")
    experience: Optional[str] = Field(default=None, description="Experience level filter")


class JobSearchTool(BaseTool):
    name: str = "job_search"
    description: str = "Search for jobs based on query, location, skills, and experience"
    args_schema: Type[BaseModel] = JobSearchInput
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
    
    def _run(self, query: str, location: Optional[str] = None, 
             skills: Optional[List[str]] = None, experience: Optional[str] = None) -> str:
        """Execute job search"""
        try:
            search_filter = {}
            
            if query:
                search_filter["$text"] = {"$search": query}
            
            if location:
                search_filter["location"] = {"$regex": location, "$options": "i"}
            
            if skills:
                search_filter["skills"] = {"$in": skills}
            
            if experience:
                search_filter["experience"] = {"$regex": experience, "$options": "i"}
            
            jobs = self.db.find_jobs(search_filter, limit=10)
            
            if not jobs:
                return "No jobs found matching your criteria."
            
            results = []
            for job in jobs[:5]:  # Return top 5 results
                result = f"**{job['title']}** at {job['company']}\n"
                result += f"Location: {job['location']}\n"
                result += f"Experience: {job['experience']}\n"
                if job.get('skills'):
                    result += f"Skills: {', '.join(job['skills'][:5])}\n"
                if job.get('salary'):
                    result += f"Salary: {job['salary']}\n"
                result += f"URL: {job['url']}\n"
                results.append(result)
            
            return "\n---\n".join(results)
            
        except Exception as e:
            logger.error(f"Error in job search: {e}")
            return f"Error searching for jobs: {str(e)}"


class JobAgent:
    def __init__(self):
        self.db = DatabaseManager()
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-3.5-turbo",
            openai_api_key=OPENAI_API_KEY
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.vector_store = None
        self.qa_chain = None
        self.agent_executor = None
        
        self._setup_vector_store()
        self._setup_agent()
    
    def _setup_vector_store(self):
        """Setup vector store with job data"""
        try:
            jobs = self.db.get_all_jobs()
            
            if not jobs:
                logger.warning("No jobs found in database for vector store")
                return
            
            documents = []
            for job in jobs:
                content = f"Job Title: {job['title']}\n"
                content += f"Company: {job['company']}\n"
                content += f"Location: {job['location']}\n"
                content += f"Experience: {job['experience']}\n"
                content += f"Skills: {', '.join(job.get('skills', []))}\n"
                content += f"Description: {job['job_description']}\n"
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "job_id": str(job['_id']),
                        "title": job['title'],
                        "company": job['company'],
                        "source": job['source']
                    }
                )
                documents.append(doc)
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            logger.info(f"Vector store created with {len(splits)} documents")
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {e}")
    
    def _setup_agent(self):
        """Setup the agent with tools"""
        tools = [
            JobSearchTool(db_manager=self.db),
            Tool(
                name="job_count",
                func=lambda x: f"Total jobs in database: {len(self.db.get_all_jobs())}",
                description="Get the total number of jobs in the database"
            ),
        ]
        
        prompt = PromptTemplate(
            template="""You are JobLo Assistant, an intelligent job search assistant. You help users find relevant jobs based on their queries.

You have access to the following tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}""",
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"]
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def chat(self, message: str) -> str:
        """Chat with the agent"""
        try:
            if self.agent_executor:
                response = self.agent_executor.run(message)
                return response
            else:
                return "Agent not properly initialized. Please check the setup."
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I encountered an error: {str(e)}. Please try rephrasing your question."
    
    def get_similar_jobs(self, job_description: str, k: int = 5) -> List[Dict[str, Any]]:
        """Get similar jobs using vector similarity"""
        if not self.vector_store:
            return []
        
        try:
            similar_docs = self.vector_store.similarity_search(job_description, k=k)
            
            similar_jobs = []
            for doc in similar_docs:
                job_id = doc.metadata.get('job_id')
                if job_id:
                    job = self.db.find_job_by_id(job_id)
                    if job:
                        similar_jobs.append(job)
            
            return similar_jobs
            
        except Exception as e:
            logger.error(f"Error finding similar jobs: {e}")
            return []