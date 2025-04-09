# app/service/llm_service.py - Service for LLM integration

from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from app.config import Config

config = Config()

class LLMService:
    """Service for initializing and managing different LLM models"""
    
    def __init__(self):
        """Initialize LLM service"""
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        llm_type = config.LLM_TYPE
        
        if llm_type == "LOCAL_OLLAMA":
            self.llm = self._initialize_ollama()
        elif llm_type == "OPENAI":
            self.llm = self._initialize_openai()
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}. Must be 'LOCAL_OLLAMA' or 'OPENAI'")
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM"""
        return Ollama(
            base_url=config.OLLAMA_SERVER_URL,
            model=config.OLLAMA_MODEL_NAME
        )
    
    def _initialize_openai(self):
        """Initialize OpenAI LLM"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        return ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL_NAME
        )
    
    def get_llm(self):
        """Get the initialized LLM"""
        if not self.llm:
            self._initialize_llm()
        
        return self.llm