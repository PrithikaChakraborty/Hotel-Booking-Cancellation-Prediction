#!/usr/bin/env python3
"""
Secure Application Startup Script
This script loads environment variables and starts the Flask application securely.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    
    if env_file.exists():
        load_dotenv()
        print("✅ Environment variables loaded from .env file")
        return True
    else:
        print("❌ .env file not found")
        print("📋 Please create .env file with your AWS credentials")
        return False

def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_aws_connection():
    """Test AWS connection before starting the application."""
    try:
        from aws_client import test_aws_connection
        if test_aws_connection():
            print("✅ AWS connection successful")
            return True
        else:
            print("❌ AWS connection failed")
            return False
    except Exception as e:
        print(f"❌ AWS connection test failed: {str(e)}")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting Hotel Booking Cancellation Prediction Application")
    print("=" * 60)
    
    # Step 1: Load environment variables
    print("\n1. Loading environment variables...")
    if not load_environment():
        sys.exit(1)
    
    # Step 2: Validate environment
    print("\n2. Validating environment...")
    if not validate_environment():
        sys.exit(1)
    
    # Step 3: Test AWS connection
    print("\n3. Testing AWS connection...")
    if not test_aws_connection():
        print("⚠️  AWS connection failed, but continuing...")
        print("📋 The application may not work properly without AWS access")
    
    # Step 4: Start the application
    print("\n4. Starting Flask application...")
    try:
        # Import and run the app
        sys.path.append('Backend')
        from app import app
        
        print("✅ Application started successfully!")
        print("🌐 Access the application at: http://localhost:5000")
        print("📋 Press Ctrl+C to stop the application")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        )
    except ImportError as e:
        print(f"❌ Failed to import application: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
