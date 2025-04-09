# app/config.py - Application configuration

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    
    # LLM Configuration
    LLM_TYPE = os.getenv("LLM_TYPE", "LOCAL_OLLAMA")
    
    # Ollama Configuration
    OLLAMA_SERVER_URL = os.getenv("OLLAMA_SERVER_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "mistral")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    
    # OCR Configuration (optional)
    OCR_API_ENDPOINT = os.getenv("OCR_API_ENDPOINT", "")
    
    # Data directory
    DATADIR = os.getenv("DATADIR", "../data")
    
    # Enable LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
    os.environ["LANGCHAIN_PROJECT"] = "rule-agent-langgraph"
    
    @staticmethod
    def get_config():
        """Returns a singleton instance of the Config class"""
        return Config()