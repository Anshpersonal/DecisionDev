# app/service/llm_service.py - Service for LLM integration

from langchain_community.llms import Ollama
from langchain_ibm import ChatWatsonx
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames
from genai.extensions.langchain import LangChainChatInterface
from genai.schema import TextGenerationParameters
from genai import Client, Credentials
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
        elif llm_type == "WATSONX":
            self.llm = self._initialize_watsonx()
        elif llm_type == "BAM":
            self.llm = self._initialize_bam()
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM"""
        return Ollama(
            base_url=config.OLLAMA_SERVER_URL,
            model=config.OLLAMA_MODEL_NAME
        )
    
    def _initialize_watsonx(self):
        """Initialize WatsonX LLM"""
        if not config.WATSONX_APIKEY:
            raise ValueError("WATSONX_APIKEY environment variable is not set")
        if not config.WATSONX_URL:
            raise ValueError("WATSONX_URL environment variable is not set")
        if not config.WATSONX_PROJECT_ID:
            raise ValueError("WATSONX_PROJECT_ID environment variable is not set")
        
        parameters = {
            GenTextParamsMetaNames.DECODING_METHOD: "greedy",
            GenTextParamsMetaNames.MAX_NEW_TOKENS: 400
        }
        
        return ChatWatsonx(
            model_id=config.WATSONX_MODEL_NAME,
            url=config.WATSONX_URL,
            api_key=config.WATSONX_APIKEY,
            project_id=config.WATSONX_PROJECT_ID,
            params=parameters
        )
    
    def _initialize_bam(self):
        """Initialize IBM BAM LLM"""
        if not config.BAM_APIKEY:
            raise ValueError("BAM_APIKEY environment variable is not set")
        if not config.BAM_URL:
            raise ValueError("BAM_URL environment variable is not set")
        
        creds = Credentials(config.BAM_APIKEY, api_endpoint=config.BAM_URL)
        params = TextGenerationParameters(decoding_method="greedy", max_new_tokens=400)
        client = Client(credentials=creds)
        
        return LangChainChatInterface(
            client=client,
            model_id=config.WATSONX_MODEL_NAME,
            parameters=params
        )
    
    def get_llm(self):
        """Get the initialized LLM"""
        if not self.llm:
            self._initialize_llm()
        
        return self.llm