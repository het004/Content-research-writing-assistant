# For Configuration management
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Groq Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    
    # Web Search APIs
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # Optional APIs
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    
    # Project Settings
    CONTENT_TYPE = os.getenv("CONTENT_TYPE", "blog")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate that required API keys are set"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in .env file")
        if not (cls.TAVILY_API_KEY or cls.SERPER_API_KEY):
            raise ValueError("At least one of TAVILY_API_KEY or SERPER_API_KEY must be set")
        print("✓ All required API keys validated successfully")

settings = Settings()