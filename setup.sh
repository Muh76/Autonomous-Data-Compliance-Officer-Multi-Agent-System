#!/bin/bash

# Setup script for ADCO Multi-Agent System

echo "Setting up ADCO Multi-Agent System..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data/reports
mkdir -p data/logs
mkdir -p data/regulations
mkdir -p data/chroma_db

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cat > .env << EOF
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview

# Database Configuration
DATABASE_URL=sqlite:///./data/adco.db

# Vector Store Configuration
VECTOR_STORE_TYPE=chroma
CHROMA_PERSIST_DIR=./data/chroma_db

# Application Configuration
APP_NAME=ADCO Multi-Agent System
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=change-me-in-production

# Agent Configuration
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT=300
RETRY_ATTEMPTS=3

# Data Source Configuration
SCAN_INTERVAL=3600
MAX_SCAN_DEPTH=1000

# Report Configuration
REPORT_OUTPUT_DIR=./data/reports
REPORT_FORMATS=pdf,html,json
EOF
    echo "Please edit .env file with your API keys and configuration"
fi

echo "Setup complete!"
echo "To start the API server, run: python main.py"







