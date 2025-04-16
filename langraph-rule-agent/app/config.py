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


    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")  # e.g., "pkc-xyz.region.kafka.com:9092"
    KAFKA_API_KEY = os.getenv("KAFKA_API_KEY") 
    KAFKA_API_SECRET = os.getenv("KAFKA_API_SECRET") 
    KAFKA_TOPIC =os.getenv("KAFKA_TOPIC") 
    KAFKA_CONSUMER_GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP_ID") 
    KFKA_CONSUMER_TOPIC_NAME= os.getenv("KFKA_CONSUMER_TOPIC_NAME") 

    aws_access_key_id=os.getenv("aws_access_key_id") 
    aws_secret_access_key=os.getenv("aws_secret_access_key") 
    region_name=os.getenv("region_name") 

    S3_BUCKET=os.getenv("S3_BUCKET")
    
    @staticmethod
    def get_config():
        """Returns a singleton instance of the Config class"""
        return Config()