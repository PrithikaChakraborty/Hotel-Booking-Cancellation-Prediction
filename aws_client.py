"""
AWS client helper for secure credential management.
This module provides a secure way to create AWS clients using environment variables.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSClientManager:
    """Manages AWS client creation with secure credential handling."""
    
    def __init__(self):
        """Initialize the AWS client manager."""
        self._clients = {}
    
    def get_client(self, service_name: str, region_name: str = None):
        """
        Get an AWS client for the specified service.
        
        Args:
            service_name (str): The AWS service name (e.g., 's3', 'ec2', 'secretsmanager')
            region_name (str, optional): The AWS region. Defaults to configured region.
        
        Returns:
            boto3.client: The AWS client instance
            
        Raises:
            ValueError: If AWS credentials are not properly configured
            NoCredentialsError: If AWS credentials are invalid
        """
        if not Config.validate_aws_credentials():
            raise ValueError(
                "AWS credentials are not properly configured. "
                "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION "
                "in your .env file."
            )
        
        region = region_name or Config.AWS_DEFAULT_REGION
        client_key = f"{service_name}_{region}"
        
        if client_key not in self._clients:
            try:
                self._clients[client_key] = boto3.client(
                    service_name,
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=region
                )
                logger.info(f"Created AWS {service_name} client for region {region}")
            except NoCredentialsError:
                logger.error("AWS credentials are invalid or not found")
                raise
            except Exception as e:
                logger.error(f"Failed to create AWS {service_name} client: {str(e)}")
                raise
        
        return self._clients[client_key]
    
    def test_connection(self) -> bool:
        """
        Test the AWS connection by calling get_caller_identity.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            sts_client = self.get_client('sts')
            response = sts_client.get_caller_identity()
            logger.info(f"Successfully connected to AWS Account: {response.get('Account')}")
            logger.info(f"User ARN: {response.get('Arn')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to AWS: {str(e)}")
            return False

# Global instance
aws_client_manager = AWSClientManager()

# Convenience functions
def get_s3_client(region_name: str = None):
    """Get an S3 client."""
    return aws_client_manager.get_client('s3', region_name)

def get_ec2_client(region_name: str = None):
    """Get an EC2 client."""
    return aws_client_manager.get_client('ec2', region_name)

def get_secrets_manager_client(region_name: str = None):
    """Get a Secrets Manager client."""
    return aws_client_manager.get_client('secretsmanager', region_name)

def get_cloudformation_client(region_name: str = None):
    """Get a CloudFormation client."""
    return aws_client_manager.get_client('cloudformation', region_name)

def test_aws_connection() -> bool:
    """Test AWS connection."""
    return aws_client_manager.test_connection()
