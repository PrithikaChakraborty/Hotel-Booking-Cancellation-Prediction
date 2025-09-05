# 🔐 Secure Setup Guide

This guide explains how to set up the Hotel Booking Cancellation Prediction application with secure credential management.

## 🚨 Important Security Notice

**Your AWS credentials have been exposed in the git history!** Please follow these steps immediately:

1. **Rotate your AWS credentials** in the AWS console
2. **Never commit credentials to git** again
3. **Use environment variables** for all sensitive data

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

Run the complete setup script:

```bash
python setup_secure_environment.py
```

This script will:
- ✅ Check Python version compatibility
- ✅ Install all dependencies
- ✅ Create .env file from template
- ✅ Validate your configuration
- ✅ Test AWS connection
- ✅ Configure AWS CLI

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env file with your credentials:**
   ```bash
   # AWS Configuration
   AWS_ACCESS_KEY_ID=your_actual_access_key_here
   AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
   AWS_DEFAULT_REGION=us-east-1
   AWS_ACCOUNT_ID=your_account_id_here
   ```

4. **Test the setup:**
   ```bash
   python setup_environment.py
   ```

## 🏃‍♂️ Running the Application

### Secure Startup

Use the secure startup script:

```bash
python run_app.py
```

This script will:
- ✅ Load environment variables
- ✅ Validate configuration
- ✅ Test AWS connection
- ✅ Start the Flask application

### Manual Startup

```bash
# Load environment variables
source .env

# Start the application
cd Backend
python app.py
```

## 🔧 Configuration Files

### .env File
Contains your sensitive credentials (never commit to git):
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
FLASK_ENV=development
FLASK_DEBUG=True
```

### config.py
Secure configuration management:
- Loads environment variables
- Validates AWS credentials
- Provides configuration classes

### aws_client.py
Secure AWS client management:
- Creates AWS clients with environment variables
- Tests connections
- Manages client instances

## 🛠️ Available Scripts

| Script | Purpose |
|--------|---------|
| `setup_secure_environment.py` | Complete automated setup |
| `setup_environment.py` | Basic environment setup |
| `configure_aws_cli.py` | Configure AWS CLI |
| `run_app.py` | Secure application startup |

## 🔒 Security Features

### Environment Variables
- All credentials stored in `.env` file
- Never committed to git
- Loaded securely at runtime

### AWS Client Management
- Secure credential handling
- Connection testing
- Error handling

### Configuration Validation
- Validates required variables
- Tests AWS connections
- Provides helpful error messages

## 🚨 Troubleshooting

### Common Issues

1. **"AWS credentials not configured"**
   ```bash
   # Check your .env file
   cat .env
   
   # Make sure variables are set
   source .env
   echo $AWS_ACCESS_KEY_ID
   ```

2. **"Connection failed"**
   ```bash
   # Test AWS connection
   python -c "from aws_client import test_aws_connection; test_aws_connection()"
   ```

3. **"Import errors"**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   ```

### Getting Help

1. Run the setup script: `python setup_secure_environment.py`
2. Check the logs for detailed error messages
3. Verify your AWS credentials in the AWS console

## 📚 Next Steps

1. **Rotate your AWS credentials** immediately
2. **Set up your .env file** with new credentials
3. **Test the connection** using the setup scripts
4. **Deploy your application** using the secure configuration

## 🔗 Related Files

- `SECURE-DEPLOYMENT-GUIDE.md` - Detailed deployment guide
- `config.py` - Configuration management
- `aws_client.py` - AWS client management
- `.env.example` - Environment template
- `.gitignore` - Git ignore rules

## ⚠️ Security Reminders

- **Never commit .env to git**
- **Rotate credentials regularly**
- **Use IAM roles when possible**
- **Monitor AWS access with CloudTrail**
- **Follow least privilege principle**
