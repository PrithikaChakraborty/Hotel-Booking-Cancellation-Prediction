#!/bin/bash

# Hotel Booking Cancellation Prediction - Infrastructure Setup Script
# This script sets up the complete AWS infrastructure for the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_DEFAULT_REGION:-us-east-1}
STACK_NAME="hotel-booking-infrastructure"
ECR_REPOSITORY="hotel-booking-prediction"
ECS_CLUSTER="hotel-booking-cluster"
ECS_SERVICE="hotel-booking-service"

echo -e "${BLUE}🚀 Setting up AWS Infrastructure for Hotel Booking Cancellation Prediction${NC}"
echo -e "${BLUE}================================================================${NC}"

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ AWS CLI is installed${NC}"
}

# Function to check AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials are not configured or invalid${NC}"
        echo -e "${YELLOW}Please configure AWS credentials using:${NC}"
        echo -e "${YELLOW}  aws configure${NC}"
        echo -e "${YELLOW}  or set environment variables:${NC}"
        echo -e "${YELLOW}  export AWS_ACCESS_KEY_ID=your_key${NC}"
        echo -e "${YELLOW}  export AWS_SECRET_ACCESS_KEY=your_secret${NC}"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${GREEN}✅ AWS credentials are valid${NC}"
    echo -e "${GREEN}✅ AWS Account ID: ${ACCOUNT_ID}${NC}"
    echo -e "${GREEN}✅ AWS Region: ${AWS_REGION}${NC}"
}

# Function to create ECR repository
create_ecr_repository() {
    echo -e "${YELLOW}Creating ECR repository...${NC}"
    
    if aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null; then
        echo -e "${YELLOW}ECR repository already exists${NC}"
    else
        aws ecr create-repository \
            --repository-name $ECR_REPOSITORY \
            --region $AWS_REGION \
            --image-scanning-configuration scanOnPush=true
        echo -e "${GREEN}✅ ECR repository created${NC}"
    fi
}

# Function to create secrets in AWS Secrets Manager
create_secrets() {
    echo -e "${YELLOW}Creating secrets in AWS Secrets Manager...${NC}"
    
    # Check if environment variables are set
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        echo -e "${RED}Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set${NC}"
        echo -e "${YELLOW}Please run: source .env${NC}"
        exit 1
    fi
    
    SECRET_NAME="hotel-booking/aws-credentials"
    SECRET_VALUE="{\"access_key_id\":\"$AWS_ACCESS_KEY_ID\",\"secret_access_key\":\"$AWS_SECRET_ACCESS_KEY\"}"
    
    # Check if secret already exists
    if aws secretsmanager describe-secret --secret-id $SECRET_NAME --region $AWS_REGION &> /dev/null; then
        echo -e "${YELLOW}Secret already exists, updating...${NC}"
        aws secretsmanager update-secret \
            --secret-id $SECRET_NAME \
            --secret-string "$SECRET_VALUE" \
            --region $AWS_REGION
    else
        aws secretsmanager create-secret \
            --name $SECRET_NAME \
            --description "AWS credentials for Hotel Booking application" \
            --secret-string "$SECRET_VALUE" \
            --region $AWS_REGION
    fi
    echo -e "${GREEN}✅ Secrets created/updated in AWS Secrets Manager${NC}"
}

# Function to deploy CloudFormation stack
deploy_cloudformation() {
    echo -e "${YELLOW}Deploying CloudFormation stack...${NC}"
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &> /dev/null; then
        echo -e "${YELLOW}Stack exists, updating...${NC}"
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://.aws/cloudformation-infrastructure.yml \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
    else
        echo -e "${YELLOW}Creating new stack...${NC}"
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://.aws/cloudformation-infrastructure.yml \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION
    fi
    
    echo -e "${YELLOW}Waiting for stack deployment to complete...${NC}"
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION || \
    aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $AWS_REGION
    
    echo -e "${GREEN}✅ CloudFormation stack deployed successfully${NC}"
}

# Function to get stack outputs
get_stack_outputs() {
    echo -e "${YELLOW}Getting stack outputs...${NC}"
    
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs' \
        --output table)
    
    echo -e "${GREEN}Stack Outputs:${NC}"
    echo "$OUTPUTS"
}

# Function to create ECS cluster
create_ecs_cluster() {
    echo -e "${YELLOW}Creating ECS cluster...${NC}"
    
    if aws ecs describe-clusters --clusters $ECS_CLUSTER --region $AWS_REGION &> /dev/null; then
        echo -e "${YELLOW}ECS cluster already exists${NC}"
    else
        aws ecs create-cluster \
            --cluster-name $ECS_CLUSTER \
            --region $AWS_REGION
        echo -e "${GREEN}✅ ECS cluster created${NC}"
    fi
}

# Function to register task definition
register_task_definition() {
    echo -e "${YELLOW}Registering ECS task definition...${NC}"
    
    aws ecs register-task-definition \
        --cli-input-json file://.aws/task-definition.json \
        --region $AWS_REGION
    
    echo -e "${GREEN}✅ ECS task definition registered${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting infrastructure setup...${NC}"
    
    # Pre-flight checks
    check_aws_cli
    check_aws_credentials
    
    # Infrastructure setup
    create_ecr_repository
    create_secrets
    deploy_cloudformation
    create_ecs_cluster
    register_task_definition
    get_stack_outputs
    
    echo -e "${GREEN}🎉 Infrastructure setup completed successfully!${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "${YELLOW}1. Configure GitHub Secrets in your repository${NC}"
    echo -e "${YELLOW}2. Push your code to trigger the CI/CD pipeline${NC}"
    echo -e "${YELLOW}3. Monitor the deployment in GitHub Actions${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

# Run main function
main "$@"