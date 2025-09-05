#!/usr/bin/env python3
"""
Environment setup script for Hotel Booking Cancellation Prediction application.
This script helps you set up the environment variables securely.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Copy .env.example to .env
    with open(env_example, 'r') as src, open(env_file, 'w') as dst:
        dst.write(src.read())
    
    print("✅ Created .env file from .env.example")
    print("📝 Please edit .env file with your actual credentials")
    return True

def validate_env_file():
    """Validate that .env file has required variables."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION'
    ]
    
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=your_" in content or f"{var}=your_" in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Please update these variables in .env file: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file appears to be configured")
    return True

def test_aws_connection():
    """Test AWS connection using the configured credentials."""
    try:
        from aws_client import test_aws_connection
        if test_aws_connection():
            print("✅ AWS connection successful")
            return True
        else:
            print("❌ AWS connection failed")
            return False
    except ImportError:
        print("❌ Could not import aws_client module")
        return False
    except Exception as e:
        print(f"❌ AWS connection test failed: {str(e)}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up environment for Hotel Booking Cancellation Prediction")
    print("=" * 60)
    
    # Step 1: Create .env file
    print("\n1. Creating .env file...")
    if not create_env_file():
        sys.exit(1)
    
    # Step 2: Validate .env file
    print("\n2. Validating .env file...")
    if not validate_env_file():
        print("\n📋 Next steps:")
        print("   1. Edit .env file with your actual AWS credentials")
        print("   2. Run this script again to test the connection")
        sys.exit(1)
    
    # Step 3: Test AWS connection
    print("\n3. Testing AWS connection...")
    if test_aws_connection():
        print("\n🎉 Environment setup completed successfully!")
        print("✅ You can now run your application with secure credential management")
    else:
        print("\n❌ Environment setup incomplete")
        print("📋 Please check your AWS credentials in the .env file")

if __name__ == "__main__":
    main()
