#!/usr/bin/env python3
"""
AWS CLI Configuration Script
This script helps you configure AWS CLI with your credentials securely.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_aws_cli_installed():
    """Check if AWS CLI is installed."""
    success, stdout, stderr = run_command("aws --version", check=False)
    if success:
        print(f"✅ AWS CLI is installed: {stdout.strip()}")
        return True
    else:
        print("❌ AWS CLI is not installed")
        print("📋 Please install AWS CLI from: https://aws.amazon.com/cli/")
        return False

def configure_aws_cli():
    """Configure AWS CLI with credentials from environment variables."""
    # Check if environment variables are set
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    if not access_key or not secret_key:
        print("❌ AWS credentials not found in environment variables")
        print("📋 Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file")
        return False
    
    print("🔧 Configuring AWS CLI...")
    
    # Configure AWS CLI
    commands = [
        f'aws configure set aws_access_key_id "{access_key}"',
        f'aws configure set aws_secret_access_key "{secret_key}"',
        f'aws configure set default.region "{region}"',
        'aws configure set default.output "json"'
    ]
    
    for command in commands:
        success, stdout, stderr = run_command(command, check=False)
        if not success:
            print(f"❌ Failed to run: {command}")
            print(f"Error: {stderr}")
            return False
    
    print("✅ AWS CLI configured successfully")
    return True

def test_aws_connection():
    """Test AWS connection using AWS CLI."""
    print("🧪 Testing AWS connection...")
    
    success, stdout, stderr = run_command("aws sts get-caller-identity", check=False)
    if success:
        print("✅ AWS connection successful!")
        print(f"Response: {stdout.strip()}")
        return True
    else:
        print("❌ AWS connection failed")
        print(f"Error: {stderr}")
        return False

def main():
    """Main configuration function."""
    print("🚀 AWS CLI Configuration Script")
    print("=" * 40)
    
    # Step 1: Check if AWS CLI is installed
    print("\n1. Checking AWS CLI installation...")
    if not check_aws_cli_installed():
        sys.exit(1)
    
    # Step 2: Load environment variables
    print("\n2. Loading environment variables...")
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Found .env file")
        # Load environment variables
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("❌ .env file not found")
        print("📋 Please create .env file with your AWS credentials")
        sys.exit(1)
    
    # Step 3: Configure AWS CLI
    print("\n3. Configuring AWS CLI...")
    if not configure_aws_cli():
        sys.exit(1)
    
    # Step 4: Test connection
    print("\n4. Testing AWS connection...")
    if test_aws_connection():
        print("\n🎉 AWS CLI configuration completed successfully!")
        print("✅ You can now use AWS CLI commands")
    else:
        print("\n❌ AWS CLI configuration failed")
        print("📋 Please check your credentials and try again")

if __name__ == "__main__":
    main()
