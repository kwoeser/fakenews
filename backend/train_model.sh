#!/bin/bash

# Script to train the fake news detection model
# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' 

echo "Starting model training script..."

# Ensure we are in the backend directory
cd "$(dirname "$0")" || exit 1

# Activate virtual environment
echo -e "\n${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Train the model
echo -e "\n${GREEN}Training the model...${NC}"
python -m app.model 

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Model training completed successfully.${NC}"
else
    echo -e "\n${RED}Model training failed.${NC}"
    deactivate 
    exit 1
fi

# Deactivate virtual environment
echo -e "\n${GREEN}Deactivating virtual environment...${NC}"
deactivate

echo "Model training script finished." 