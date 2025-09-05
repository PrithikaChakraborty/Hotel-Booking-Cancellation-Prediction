#!/usr/bin/env python3
"""
Complete Secure Environment Setup Script
This script sets up the entire secure environment for the Hotel Booking Cancellation Prediction application.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"\n{step_num}. {description}")

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("📋 Please install Python 3.8 or higher")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt", check=False)
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        print(f"Error: {stderr}")
        return False

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
            if f"{var}=your_" in content:
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

def configure_aws_cli():
    """Configure AWS CLI with credentials from environment variables."""
    # Check if AWS CLI is installed
    success, stdout, stderr = run_command("aws --version", check=False)
    if not success:
        print("⚠️  AWS CLI is not installed")
        print("📋 You can install it from: https://aws.amazon.com/cli/")
        return True  # Not critical for the application to work
    
    print("🔧 Configuring AWS CLI...")
    
    # Load environment variables
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Configure AWS CLI
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    if access_key and secret_key:
        commands = [
            f'aws configure set aws_access_key_id "{access_key}"',
            f'aws configure set aws_secret_access_key "{secret_key}"',
            f'aws configure set default.region "{region}"',
            'aws configure set default.output "json"'
        ]
        
        for command in commands:
            success, stdout, stderr = run_command(command, check=False)
            if not success:
                print(f"❌ Failed to configure AWS CLI: {command}")
                return False
        
        print("✅ AWS CLI configured successfully")
        return True
    else:
        print("❌ AWS credentials not found in environment variables")
        return False

def main():
    """Main setup function."""
    print_header("Hotel Booking Cancellation Prediction - Secure Environment Setup")
    
    print("🚀 This script will set up a secure environment for your application")
    print("🔐 All credentials will be managed through environment variables")
    
    # Step 1: Check Python version
    print_step("1", "Checking Python version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print_step("2", "Installing dependencies")
    if not install_dependencies():
        sys.exit(1)
    
    # Step 3: Create .env file
    print_step("3", "Setting up environment variables")
    if not create_env_file():
        sys.exit(1)
    
    # Step 4: Validate .env file
    print_step("4", "Validating environment configuration")
    if not validate_env_file():
        print("\n📋 Next steps:")
        print("   1. Edit .env file with your actual AWS credentials")
        print("   2. Run this script again to complete the setup")
        sys.exit(1)
    
    # Step 5: Test AWS connection
    print_step("5", "Testing AWS connection")
    if not test_aws_connection():
        print("\n❌ AWS connection failed")
        print("📋 Please check your credentials in the .env file")
        sys.exit(1)
    
    # Step 6: Configure AWS CLI
    print_step("6", "Configuring AWS CLI")
    configure_aws_cli()  # Not critical if it fails
    
    # Success message
    print_header("Setup Complete!")
    print("🎉 Your secure environment is ready!")
    print("\n✅ What's been set up:")
    print("   • Environment variables configured")
    print("   • AWS connection tested")
    print("   • Dependencies installed")
    print("   • AWS CLI configured (if available)")
    
    print("\n🚀 Next steps:")
    print("   1. Run your application: python app.py")
    print("   2. Deploy infrastructure: ./scripts/setup-infrastructure.sh")
    print("   3. Check the SECURE-DEPLOYMENT-GUIDE.md for more details")
    
    print("\n🔒 Security reminders:")
    print("   • Never commit .env file to git")
    print("   • Rotate your AWS credentials regularly")
    print("   • Use IAM roles when possible")

if __name__ == "__main__":
    main()
