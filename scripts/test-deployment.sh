#!/bin/bash

# Hotel Booking Prediction - Deployment Test Script
# This script tests the deployed application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="us-east-1"
STACK_NAME="hotel-booking-infrastructure"

echo -e "${GREEN}Starting deployment tests...${NC}"

# Function to get load balancer DNS
get_alb_dns() {
    echo -e "${YELLOW}Getting load balancer DNS...${NC}"
    
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    if [ "$ALB_DNS" = "None" ] || [ -z "$ALB_DNS" ]; then
        echo -e "${RED}Could not retrieve load balancer DNS${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Load balancer DNS: $ALB_DNS${NC}"
    echo "$ALB_DNS"
}

# Function to test health endpoint
test_health_endpoint() {
    local ALB_DNS=$1
    echo -e "${YELLOW}Testing health endpoint...${NC}"
    
    if curl -f -s http://$ALB_DNS/ > /dev/null; then
        echo -e "${GREEN}Health endpoint test passed${NC}"
        return 0
    else
        echo -e "${RED}Health endpoint test failed${NC}"
        return 1
    fi
}

# Function to test prediction endpoint
test_prediction_endpoint() {
    local ALB_DNS=$1
    echo -e "${YELLOW}Testing prediction endpoint...${NC}"
    
    # Test data
    TEST_DATA='{
        "hotel": "Resort Hotel",
        "arrival_date_month": 7,
        "lead_time": 30,
        "adr": 100.0,
        "total_of_special_requests": 1
    }'
    
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA" \
        http://$ALB_DNS/predict)
    
    if echo "$RESPONSE" | grep -q "prediction_text"; then
        echo -e "${GREEN}Prediction endpoint test passed${NC}"
        echo -e "${YELLOW}Response: $RESPONSE${NC}"
        return 0
    else
        echo -e "${RED}Prediction endpoint test failed${NC}"
        echo -e "${RED}Response: $RESPONSE${NC}"
        return 1
    fi
}

# Function to test batch endpoint
test_batch_endpoint() {
    local ALB_DNS=$1
    echo -e "${YELLOW}Testing batch endpoint...${NC}"
    
    # Create a test CSV file
    TEST_CSV="test_data.csv"
    echo "hotel,arrival_date_month,lead_time,adr,total_of_special_requests" > $TEST_CSV
    echo "Resort Hotel,7,30,100.0,1" >> $TEST_CSV
    
    RESPONSE=$(curl -s -X POST \
        -F "file=@$TEST_CSV" \
        http://$ALB_DNS/batch)
    
    # Clean up test file
    rm -f $TEST_CSV
    
    if echo "$RESPONSE" | grep -q "Predicted Cancellation"; then
        echo -e "${GREEN}Batch endpoint test passed${NC}"
        return 0
    else
        echo -e "${RED}Batch endpoint test failed${NC}"
        echo -e "${RED}Response: $RESPONSE${NC}"
        return 1
    fi
}

# Function to check ECS service status
check_ecs_service() {
    echo -e "${YELLOW}Checking ECS service status...${NC}"
    
    SERVICE_STATUS=$(aws ecs describe-services \
        --cluster hotel-booking-cluster \
        --services hotel-booking-service \
        --region $AWS_REGION \
        --query 'services[0].status' \
        --output text)
    
    RUNNING_COUNT=$(aws ecs describe-services \
        --cluster hotel-booking-cluster \
        --services hotel-booking-service \
        --region $AWS_REGION \
        --query 'services[0].runningCount' \
        --output text)
    
    DESIRED_COUNT=$(aws ecs describe-services \
        --cluster hotel-booking-cluster \
        --services hotel-booking-service \
        --region $AWS_REGION \
        --query 'services[0].desiredCount' \
        --output text)
    
    echo -e "${YELLOW}Service Status: $SERVICE_STATUS${NC}"
    echo -e "${YELLOW}Running Tasks: $RUNNING_COUNT/$DESIRED_COUNT${NC}"
    
    if [ "$SERVICE_STATUS" = "ACTIVE" ] && [ "$RUNNING_COUNT" = "$DESIRED_COUNT" ]; then
        echo -e "${GREEN}ECS service is healthy${NC}"
        return 0
    else
        echo -e "${RED}ECS service is not healthy${NC}"
        return 1
    fi
}

# Function to run performance test
run_performance_test() {
    local ALB_DNS=$1
    echo -e "${YELLOW}Running performance test...${NC}"
    
    # Test with multiple concurrent requests
    for i in {1..10}; do
        curl -s http://$ALB_DNS/ > /dev/null &
    done
    
    wait
    echo -e "${GREEN}Performance test completed${NC}"
}

# Main test function
main() {
    echo -e "${GREEN}=== Hotel Booking Prediction Deployment Tests ===${NC}"
    
    # Get load balancer DNS
    ALB_DNS=$(get_alb_dns)
    
    # Wait for service to be ready
    echo -e "${YELLOW}Waiting for service to be ready...${NC}"
    sleep 60
    
    # Run tests
    TESTS_PASSED=0
    TOTAL_TESTS=5
    
    # Test 1: Health endpoint
    if test_health_endpoint "$ALB_DNS"; then
        ((TESTS_PASSED++))
    fi
    
    # Test 2: Prediction endpoint
    if test_prediction_endpoint "$ALB_DNS"; then
        ((TESTS_PASSED++))
    fi
    
    # Test 3: Batch endpoint
    if test_batch_endpoint "$ALB_DNS"; then
        ((TESTS_PASSED++))
    fi
    
    # Test 4: ECS service status
    if check_ecs_service; then
        ((TESTS_PASSED++))
    fi
    
    # Test 5: Performance test
    run_performance_test "$ALB_DNS"
    ((TESTS_PASSED++))
    
    # Summary
    echo -e "${GREEN}=== Test Results ===${NC}"
    echo -e "${YELLOW}Tests Passed: $TESTS_PASSED/$TOTAL_TESTS${NC}"
    
    if [ $TESTS_PASSED -eq $TOTAL_TESTS ]; then
        echo -e "${GREEN}All tests passed! Deployment is successful.${NC}"
        echo -e "${GREEN}Application URL: http://$ALB_DNS${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed. Please check the deployment.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
