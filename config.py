"""
Secure configuration management for the Hotel Booking Cancellation Prediction application.
This module handles environment variables and provides secure access to configuration.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION: str = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    AWS_ACCOUNT_ID: Optional[str] = os.getenv('AWS_ACCOUNT_ID')
    
    # Flask Configuration
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv('DATABASE_URL')
    
    @classmethod
    def validate_aws_credentials(cls) -> bool:
        """Validate that AWS credentials are properly configured."""
        return all([
            cls.AWS_ACCESS_KEY_ID,
            cls.AWS_SECRET_ACCESS_KEY,
            cls.AWS_DEFAULT_REGION
        ])
    
    @classmethod
    def get_aws_credentials(cls) -> dict:
        """Get AWS credentials as a dictionary."""
        if not cls.validate_aws_credentials():
            raise ValueError("AWS credentials are not properly configured. Please check your .env file.")
        
        return {
            'aws_access_key_id': cls.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': cls.AWS_SECRET_ACCESS_KEY,
            'region_name': cls.AWS_DEFAULT_REGION
        }

# Development configuration
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

# Production configuration
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
