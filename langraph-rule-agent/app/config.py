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
    OLLAMA_SERVER_URL = os.getenv("OLLAMA_SERVER_URL", "http://localhost:11434")
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "mistral")
    
    # WatsonX AI Configuration
    WATSONX_APIKEY = os.getenv("WATSONX_APIKEY", "")
    WATSONX_URL = os.getenv("WATSONX_URL", "")
    WATSONX_MODEL_NAME = os.getenv("WATSONX_MODEL_NAME", "mistralai/mistral-7b-instruct-v0-2")
    WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
    
    # IBM BAM Configuration
    BAM_APIKEY = os.getenv("BAM_APIKEY", "")
    BAM_URL = os.getenv("BAM_URL", "")
    
    # Decision Service Configuration
    ODM_SERVER_URL = os.getenv("ODM_SERVER_URL", "http://localhost:9060")
    ODM_USERNAME = os.getenv("ODM_USERNAME", "odmAdmin")
    ODM_PASSWORD = os.getenv("ODM_PASSWORD", "odmAdmin")
    
    ADS_SERVER_URL = os.getenv("ADS_SERVER_URL", "")
    ADS_USER_ID = os.getenv("ADS_USER_ID", "")
    ADS_ZEN_APIKEY = os.getenv("ADS_ZEN_APIKEY", "")
    
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