#!/usr/bin/env python3
"""
Test script to verify the secure setup is working correctly.
"""

import os
import sys
from pathlib import Path

def test_environment_file():
    """Test if .env file exists and has required variables."""
    print("🧪 Testing environment file...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    # Check if it has placeholder values
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_' in content:
            print("⚠️  .env file contains placeholder values")
            print("📋 Please update .env file with your actual credentials")
            return False
    
    print("✅ .env file appears to be configured")
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from config import Config
        print("✅ config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from aws_client import aws_client_manager
        print("✅ aws_client module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import aws_client: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading."""
    print("🧪 Testing configuration...")
    
    try:
        from config import Config
        
        # Test if configuration can be loaded
        print(f"✅ AWS Region: {Config.AWS_DEFAULT_REGION}")
        print(f"✅ Flask Environment: {Config.FLASK_ENV}")
        
        # Test credential validation (without actually connecting)
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            print("✅ AWS credentials are configured")
        else:
            print("⚠️  AWS credentials not configured")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_git_status():
    """Test git status and check for sensitive files."""
    print("🧪 Testing git status...")
    
    try:
        import subprocess
        
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("📋 Git status shows uncommitted changes:")
            print(result.stdout)
        else:
            print("✅ No uncommitted changes")
        
        # Check if .env is in gitignore
        gitignore_file = Path('.gitignore')
        if gitignore_file.exists():
            with open(gitignore_file, 'r') as f:
                content = f.read()
                if '.env' in content:
                    print("✅ .env file is in .gitignore")
                else:
                    print("⚠️  .env file is not in .gitignore")
        
        return True
    except Exception as e:
        print(f"❌ Git status test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing Secure Setup")
    print("=" * 40)
    
    tests = [
        test_environment_file,
        test_imports,
        test_configuration,
        test_git_status
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your secure setup is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
