"""
Configuration settings for BharatSignal application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # AWS Bedrock settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Bedrock model configuration
    BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'
    BEDROCK_MAX_TOKENS = 1000
    BEDROCK_TEMPERATURE = 0.7
    
    # CSV processing limits
    MAX_CSV_ROWS = 1000
    MAX_CONTEXT_LENGTH = 2000
    
    # Supported CSV columns
    REQUIRED_CSV_COLUMNS = ['date', 'item', 'quantity', 'price']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}