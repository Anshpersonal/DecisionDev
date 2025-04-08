# app/config.py - Application configuration

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    OCR_API_ENDPOINT = os.getenv("OCR_API_ENDPOINT")

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


    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
    
    # Enable LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
    os.environ["LANGCHAIN_PROJECT"] = "form-validation-agent"
       
    @staticmethod
    def get_config():
        """Returns a singleton instance of the Config class"""
        return Config()