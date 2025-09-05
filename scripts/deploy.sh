#!/bin/bash

# Hotel Booking Prediction - Deployment Script
# This script handles the complete deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="hotel-booking-prediction"
ECS_CLUSTER="hotel-booking-cluster"
ECS_SERVICE="hotel-booking-service"
TASK_DEFINITION="hotel-booking-task"

echo -e "${GREEN}Starting deployment process...${NC}"

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}AWS CLI found${NC}"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Docker found${NC}"
}

# Function to authenticate with ECR
ecr_login() {
    echo -e "${YELLOW}Logging into Amazon ECR...${NC}"
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    echo -e "${GREEN}ECR login successful${NC}"
}

# Function to build and push Docker image
build_and_push() {
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t $ECR_REPOSITORY:latest .
    
    echo -e "${YELLOW}Tagging image for ECR...${NC}"
    docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
    
    echo -e "${YELLOW}Pushing image to ECR...${NC}"
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
    echo -e "${GREEN}Image pushed successfully${NC}"
}

# Function to update ECS service
update_ecs_service() {
    echo -e "${YELLOW}Updating ECS service...${NC}"
    
    # Get the current task definition
    TASK_DEF_ARN=$(aws ecs describe-task-definition --task-definition $TASK_DEFINITION --query 'taskDefinition.taskDefinitionArn' --output text)
    
    # Update the service to force a new deployment
    aws ecs update-service \
        --cluster $ECS_CLUSTER \
        --service $ECS_SERVICE \
        --force-new-deployment
    
    echo -e "${GREEN}ECS service update initiated${NC}"
    
    # Wait for deployment to complete
    echo -e "${YELLOW}Waiting for deployment to complete...${NC}"
    aws ecs wait services-stable --cluster $ECS_CLUSTER --services $ECS_SERVICE
    echo -e "${GREEN}Deployment completed successfully${NC}"
}

# Function to run health check
health_check() {
    echo -e "${YELLOW}Running health check...${NC}"
    
    # Get the load balancer DNS name
    ALB_DNS=$(aws elbv2 describe-load-balancers --names hotel-booking-alb --query 'LoadBalancers[0].DNSName' --output text)
    
    if [ "$ALB_DNS" != "None" ] && [ "$ALB_DNS" != "" ]; then
        echo -e "${YELLOW}Testing endpoint: http://$ALB_DNS${NC}"
        
        # Wait a bit for the service to be ready
        sleep 30
        
        # Test the endpoint
        if curl -f http://$ALB_DNS/; then
            echo -e "${GREEN}Health check passed!${NC}"
            echo -e "${GREEN}Application is available at: http://$ALB_DNS${NC}"
        else
            echo -e "${RED}Health check failed${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Load balancer not found, skipping health check${NC}"
    fi
}

# Main deployment function
main() {
    echo -e "${GREEN}=== Hotel Booking Prediction Deployment ===${NC}"
    
    # Check prerequisites
    check_aws_cli
    check_docker
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${GREEN}AWS Account ID: $AWS_ACCOUNT_ID${NC}"
    
    # ECR operations
    ecr_login
    build_and_push
    
    # ECS operations
    update_ecs_service
    
    # Health check
    health_check
    
    echo -e "${GREEN}=== Deployment completed successfully! ===${NC}"
}

# Run main function
main "$@"
