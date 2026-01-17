import os
from dotenv import load_dotenv

# Load the environment variables once
load_dotenv()

class Config:
    # AI Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Database Credentials
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    # Vector DB Table Name
    TABLE_NAME = os.getenv("TABLE_NAME")
    EMBED_DIM = 768

    @classmethod
    def validate(cls):
        """Simple check to ensure critical keys are present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("Missing GOOGLE_API_KEY in .env file")