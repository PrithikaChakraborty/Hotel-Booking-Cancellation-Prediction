# 🔐 Secure Deployment Guide

This guide explains how to securely deploy the Hotel Booking Cancellation Prediction application using environment variables instead of hardcoded credentials.

## 🚨 Security First

**NEVER commit credentials to git!** This guide shows you how to manage credentials securely.

## 📋 Prerequisites

1. AWS Account with appropriate permissions
2. Python 3.8+ installed
3. AWS CLI installed and configured (optional, we'll use environment variables)

## 🛠️ Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file with your actual credentials:**
   ```bash
   # AWS Configuration
   AWS_ACCESS_KEY_ID=your_actual_access_key_here
   AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
   AWS_DEFAULT_REGION=us-east-1
   AWS_ACCOUNT_ID=your_account_id_here
   
   # Application Configuration
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

3. **Run the setup script to validate your configuration:**
   ```bash
   python setup_environment.py
   ```

### Step 3: Test AWS Connection

```bash
python -c "from aws_client import test_aws_connection; test_aws_connection()"
```

### Step 4: Deploy Infrastructure

```bash
# Load environment variables
source .env

# Run the deployment script
./scripts/setup-infrastructure.sh
```

## 🔧 Using the Secure Configuration

### In Python Code

```python
from config import Config
from aws_client import get_s3_client, test_aws_connection

# Test connection
if test_aws_connection():
    print("Connected to AWS successfully!")

# Get AWS clients
s3_client = get_s3_client()
ec2_client = get_ec2_client()
```

### In Shell Scripts

```bash
# Load environment variables
source .env

# Use environment variables
aws s3 ls --region $AWS_DEFAULT_REGION
```

## 🚀 Deployment Options

### Option 1: Local Development

1. Set up environment variables as shown above
2. Run the application locally:
   ```bash
   python app.py
   ```

### Option 2: AWS EC2 Deployment

1. Launch an EC2 instance
2. Install dependencies on the instance
3. Set environment variables on the instance
4. Deploy your application

### Option 3: AWS Lambda Deployment

1. Package your application
2. Set environment variables in Lambda configuration
3. Deploy using AWS CLI or console

## 🔒 Security Best Practices

1. **Environment Variables**: Always use environment variables for credentials
2. **IAM Roles**: Use IAM roles when possible instead of access keys
3. **Least Privilege**: Grant only necessary permissions
4. **Rotate Credentials**: Regularly rotate your AWS credentials
5. **Monitor Access**: Enable CloudTrail to monitor AWS API calls
6. **Secure Storage**: Use AWS Secrets Manager for sensitive data

## 🆘 Troubleshooting

### Common Issues

1. **"AWS credentials not configured"**
   - Check that your .env file exists and has the correct values
   - Run `source .env` to load environment variables

2. **"Access denied"**
   - Verify your AWS credentials have the necessary permissions
   - Check the AWS region configuration

3. **"Connection failed"**
   - Verify your internet connection
   - Check AWS service status

### Getting Help

1. Run the setup script: `python setup_environment.py`
2. Check the logs for detailed error messages
3. Verify your AWS credentials in the AWS console

## 📚 Additional Resources

- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [Environment Variables in Python](https://docs.python.org/3/library/os.html#os.environ)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
