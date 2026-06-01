#!/bin/bash

# Quick Start Script for Mobile Chat System
# Runs backend and mobile app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Mobile Chat System - Quick Start${NC}"
echo -e "${GREEN}========================================${NC}"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Flutter
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter not found. Please install Flutter${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Flutter found${NC}"

# Ask user what to run
echo -e "\n${YELLOW}What would you like to do?${NC}"
echo "1) Run Backend only"
echo "2) Run Mobile App only"
echo "3) Run Both (Backend + Mobile)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Starting Backend...${NC}"
        cd backend
        
        # Create venv if not exists
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}Creating virtual environment...${NC}"
            python3 -m venv venv
        fi
        
        # Activate venv
        source venv/bin/activate
        
        # Install dependencies
        pip install -q -r requirements.txt
        
        echo -e "${GREEN}✓ Dependencies installed${NC}"
        echo -e "${GREEN}Starting FastAPI server...${NC}"
        echo -e "${GREEN}Access at: http://localhost:8000${NC}"
        echo -e "${GREEN}API Docs at: http://localhost:8000/docs${NC}"
        
        uvicorn app.main:app --reload
        ;;
        
    2)
        echo -e "\n${YELLOW}Starting Mobile App...${NC}"
        cd mobile
        
        echo -e "${YELLOW}Installing dependencies...${NC}"
        flutter pub get -q
        
        echo -e "${GREEN}✓ Dependencies installed${NC}"
        echo -e "${YELLOW}Please ensure:${NC}"
        echo "1) Backend is running on http://localhost:8000"
        echo "2) Update API URL in lib/config.dart if needed"
        echo "3) Android emulator is running (flutter devices)"
        echo ""
        
        flutter run
        ;;
        
    3)
        echo -e "\n${YELLOW}Starting Backend and Mobile App...${NC}"
        
        # Start backend in background
        echo -e "${YELLOW}Starting Backend in background...${NC}"
        cd backend
        
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip install -q -r requirements.txt
        
        uvicorn app.main:app --reload &
        BACKEND_PID=$!
        
        echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
        sleep 2
        
        # Start mobile app
        echo -e "${YELLOW}Starting Mobile App...${NC}"
        cd ../mobile
        
        flutter pub get -q
        flutter run
        
        # Cleanup on exit
        echo -e "\n${YELLOW}Stopping backend...${NC}"
        kill $BACKEND_PID
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
