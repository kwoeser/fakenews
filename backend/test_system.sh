#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' 

echo "Starting system tests (excluding model training)..."

# Initialize API_PID for the trap
API_PID=""

# Trap to ensure API server is killed on exit, interrupt, or termination signal.
# It checks if API_PID is set and corresponds to a running process before attempting to kill.
trap 'if [ -n "$API_PID" ] && ps -p "$API_PID" > /dev/null 2>&1; then echo "EXIT trap: Stopping API server (PID: $API_PID)..."; kill "$API_PID"; fi' EXIT SIGINT SIGTERM

# Change to backend directory
cd "$(dirname "$0")" || exit 1

# Activate virtual environment
echo -e "\n${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Model training is now expected to be done via train_model.sh
# Test 1: Test prediction system
echo -e "\n${GREEN}Test 1: Testing prediction system...${NC}"
python -m app.predict
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Prediction system test completed successfully${NC}"
else
    echo -e "${RED}Prediction system test failed${NC}"
    exit 1
fi

# Test 2: Test scraper
echo -e "\n${GREEN}Test 2: Testing article scraper...${NC}"
python -m app.scraper
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Scraper test completed successfully${NC}"
else
    echo -e "${RED}Scraper test failed (Note: This might be due to the test URL in scraper.py)${NC}"
    exit 1 
fi

# Test 3: Test API endpoints
echo -e "\n${GREEN}Test 3: Testing API endpoints...${NC}"
  
# Start the API server in the background
echo "Starting API server..."
python -m uvicorn app.main:app --reload &
API_PID=$! # Capture PID of the backgrounded server

# Wait for the server to start
echo "Waiting for API server to start (PID: $API_PID)..."
sleep 5 

# Check if the server actually started by checking its PID
if ! ps -p "$API_PID" > /dev/null 2>&1; then
    echo -e "${RED}API server failed to start (PID $API_PID not found or server exited prematurely).${NC}"
    API_PID="" # Clear API_PID as it's not valid, so trap doesn't try to kill a non-existent/wrong PID
    exit 1
fi
echo -e "${GREEN}API server started successfully (PID: $API_PID).${NC}"

# Test the root endpoint
echo "Testing root endpoint..."
curl -s http://localhost:8000/ | grep -q "Welcome"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Root endpoint test passed${NC}"
else
    echo -e "${RED}Root endpoint test failed${NC}"
    exit 1 # Trap will handle killing the server
fi
  
# Test the predict endpoint
echo "Testing predict endpoint..."
curl -s -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "This is a test article that needs to be at least 50 characters long to be processed by our fake news detection system."}' \
     | grep -q "prediction"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Predict endpoint test passed${NC}"
else
    echo -e "${RED}Predict endpoint test failed${NC}"
    exit 1 # Trap will handle killing the server
fi
  
# Test the analyze-url endpoint
echo "Testing analyze-url endpoint..."
TEST_ARTICLE_URL="https://apnews.com/article/vaccines-fda-kennedy-covid-shots-rfk-trump-bb4de15b6ff955d6cd0b406aaec3cdc5"
  
curl -s -X POST "http://localhost:8000/analyze-url" \
     -H "Content-Type: application/json" \
     -d "{\"url\": \"$TEST_ARTICLE_URL\"}" \
     | grep -q "analyzed_url"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Analyze-url endpoint test passed (basic check)${NC}"
else
    echo -e "${RED}Analyze-url endpoint test failed or URL could not be scraped${NC}"
    echo -e "${RED}Ensure TEST_ARTICLE_URL in test_system.sh is a valid, scrapable news article URL.${NC}"
    exit 1 # Trap will handle killing the server
fi
  
echo -e "\n${GREEN}All tests completed successfully!${NC}"
echo "System is working as expected."

# The EXIT trap will automatically run here, attempting to kill $API_PID if set and running. 