#!/bin/bash

# Phase 1.1: Project Structure Setup Script
# This script sets up the development environment for ADCO project

set -e  # Exit on error

echo "=========================================="
echo "ADCO Project - Phase 1.1 Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python: $PYTHON_VERSION"

# Check if Python 3.10+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10 or higher is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "WARNING: requirements.txt not found"
fi

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p data/reports
mkdir -p data/logs
mkdir -p data/regulations
mkdir -p data/chroma_db
mkdir -p adk/jobs
echo "✓ Directories created"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    if [ -f "ENV_TEMPLATE.md" ]; then
        # Extract env variables from template
        cat > .env << 'EOF'
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
        echo "✓ .env file created"
        echo "  ⚠️  Please edit .env file with your actual API keys and configuration"
    else
        echo "WARNING: ENV_TEMPLATE.md not found, skipping .env creation"
    fi
else
    echo "✓ .env file already exists"
fi

# Initialize Git if not already initialized
if [ ! -d ".git" ]; then
    echo ""
    echo "Initializing Git repository..."
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already initialized"
fi

# Verify structure
echo ""
echo "Verifying project structure..."
REQUIRED_DIRS=("adk" "adk/agents" "adk/core" "adk/models" "adk/rag" "adk/tools" "adk/jobs" "app" "app/api" "data" "docs" "tests")
MISSING_DIRS=()

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_DIRS[@]} -eq 0 ]; then
    echo "✓ All required directories exist"
else
    echo "WARNING: Missing directories:"
    for dir in "${MISSING_DIRS[@]}"; do
        echo "  - $dir"
    fi
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Verify setup: python -c 'import adk; print(\"Setup OK\")'"
echo ""
echo "To activate virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""







