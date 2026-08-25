"""
Configuration Module
Handles environment variables and application settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    API_HOST = "127.0.0.1"
    API_PORT = 8000
    RELOAD = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    RELOAD = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

config = config_map.get(ENVIRONMENT, DevelopmentConfig)

# API Keys
TOMTOM_API_KEY = os.getenv('TOMTOM_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
STADIA_MAPS_API_KEY = os.getenv('STADIA_MAPS_API_KEY')

# Agent Settings
AGENT_MAX_AREAS = int(os.getenv('AGENT_MAX_AREAS', '20'))
AGENT_TIMEOUT = int(os.getenv('AGENT_TIMEOUT', '60'))
