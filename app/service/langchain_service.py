# app/services/langchain_service.py - Service for LangChain components

from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langsmith import Client
from app.model.vector_db import VectorDatabase


class LangChainService:
    """Service for initializing and managing LangChain components"""
    
    def __init__(self, config):
        """
        Initialize LangChain service
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.llm = None
        self.embeddings = None
        self.vector_db = None
        self.langsmith_client = None
        
    def initialize(self):
        """
        Initialize all LangChain components
        
        Returns:
            dict: Dictionary of initialized components
        """
        # Initialize LLM
        self.llm = ChatOpenAI( model="gpt-4o",
            # azure_deployment=self.config.AZURE_OPENAI_DEPLOYMENT,
            # openai_api_version=self.config.AZURE_OPENAI_API_VERSION,
            # azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
            api_key=self.config.AZURE_OPENAI_API_KEY,
            # temperature=0
        )
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize LangSmith client
        self.langsmith_client = Client()
        
        # Initialize vector database
        self.vector_db = VectorDatabase(self.embeddings)
        self.vector_db.initialize_db()
        
        return {
            "llm": self.llm,
            "embeddings": self.embeddings,
            "vector_db": self.vector_db,
            "langsmith_client": self.langsmith_client
        }
    
    def get_llm(self):
        """Get the LLM model"""
        if not self.llm:
            self.initialize()
        return self.llm
    
    def get_vector_db(self):
        """Get the vector database"""
        if not self.vector_db:
            self.initialize()
        return self.vector_db