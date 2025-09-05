#!/bin/bash

# Hotel Booking Prediction - Cleanup Script
# This script cleans up AWS resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="hotel-booking-infrastructure"
AWS_REGION="us-east-1"
ECR_REPOSITORY="hotel-booking-prediction"

echo -e "${GREEN}Starting cleanup process...${NC}"

# Function to confirm deletion
confirm_deletion() {
    echo -e "${RED}WARNING: This will delete all AWS resources for the hotel booking application.${NC}"
    echo -e "${YELLOW}Are you sure you want to continue? (yes/no)${NC}"
    read -r response
    if [ "$response" != "yes" ]; then
        echo -e "${YELLOW}Cleanup cancelled.${NC}"
        exit 0
    fi
}

# Function to delete CloudFormation stack
delete_cloudformation_stack() {
    echo -e "${YELLOW}Deleting CloudFormation stack...${NC}"
    
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &> /dev/null; then
        aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION
        echo -e "${YELLOW}Waiting for stack deletion to complete...${NC}"
        aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $AWS_REGION
        echo -e "${GREEN}CloudFormation stack deleted${NC}"
    else
        echo -e "${YELLOW}CloudFormation stack not found${NC}"
    fi
}

# Function to delete ECR repository
delete_ecr_repository() {
    echo -e "${YELLOW}Deleting ECR repository...${NC}"
    
    if aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &> /dev/null; then
        # Delete all images first
        IMAGES=$(aws ecr list-images --repository-name $ECR_REPOSITORY --region $AWS_REGION --query 'imageIds[*]' --output json)
        if [ "$IMAGES" != "[]" ]; then
            aws ecr batch-delete-image --repository-name $ECR_REPOSITORY --image-ids "$IMAGES" --region $AWS_REGION
        fi
        
        # Delete the repository
        aws ecr delete-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION --force
        echo -e "${GREEN}ECR repository deleted${NC}"
    else
        echo -e "${YELLOW}ECR repository not found${NC}"
    fi
}

# Function to delete secrets
delete_secrets() {
    echo -e "${YELLOW}Deleting secrets...${NC}"
    
    SECRET_NAME="hotel-booking/aws-credentials"
    if aws secretsmanager describe-secret --secret-id $SECRET_NAME --region $AWS_REGION &> /dev/null; then
        aws secretsmanager delete-secret --secret-id $SECRET_NAME --region $AWS_REGION --force-delete-without-recovery
        echo -e "${GREEN}Secrets deleted${NC}"
    else
        echo -e "${YELLOW}Secrets not found${NC}"
    fi
}

# Function to delete CloudWatch log groups
delete_log_groups() {
    echo -e "${YELLOW}Deleting CloudWatch log groups...${NC}"
    
    LOG_GROUPS=$(aws logs describe-log-groups --log-group-name-prefix "/ecs/hotel-booking" --region $AWS_REGION --query 'logGroups[*].logGroupName' --output text)
    
    if [ -n "$LOG_GROUPS" ]; then
        for log_group in $LOG_GROUPS; do
            aws logs delete-log-group --log-group-name "$log_group" --region $AWS_REGION
            echo -e "${GREEN}Deleted log group: $log_group${NC}"
        done
    else
        echo -e "${YELLOW}No log groups found${NC}"
    fi
}

# Main cleanup function
main() {
    echo -e "${GREEN}=== Hotel Booking Prediction Cleanup ===${NC}"
    
    # Confirm deletion
    confirm_deletion
    
    # Delete resources in order
    delete_cloudformation_stack
    delete_ecr_repository
    delete_secrets
    delete_log_groups
    
    echo -e "${GREEN}=== Cleanup completed successfully! ===${NC}"
    echo -e "${YELLOW}Note: Some resources may take a few minutes to be fully deleted.${NC}"
}

# Run main function
main "$@"
