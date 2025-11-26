#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting ADCO Cloud Run Deployment...${NC}"

# 🔧 FIX: Manually add gcloud to PATH to ensure it is found
export PATH=$PATH:/Users/javadbeni/google-cloud-sdk/bin

# Check for gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Get Project ID
echo -e "${BLUE}📋 Configuration${NC}"
current_project=$(gcloud config get-value project 2>/dev/null)
read -p "Enter Google Cloud Project ID [${current_project}]: " PROJECT_ID
PROJECT_ID=${PROJECT_ID:-$current_project}

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Project ID is required.${NC}"
    exit 1
fi

# 🛡️ Validation: Check if input is all digits (Project Number vs ID)
if [[ "$PROJECT_ID" =~ ^[0-9]+$ ]]; then
    echo -e "\n${RED}⚠️  WARNING: You entered a Project Number ($PROJECT_ID).${NC}"
    echo -e "${RED}   Google Cloud requires the PROJECT ID (e.g., 'arched-catwalk-123').${NC}"
    echo -e "${BLUE}   The detected default was: ${current_project}${NC}"
    read -p "   Do you want to use '${current_project}' instead? (y/n) " use_default
    if [[ "$use_default" == "y" || "$use_default" == "Y" ]]; then
        PROJECT_ID=$current_project
    fi
fi

echo -e "${GREEN}✅ Using Project: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable APIs
echo -e "\n${BLUE}🔌 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com
echo -e "${GREEN}✅ APIs enabled${NC}"

# Build and Submit
echo -e "\n${BLUE}🔨 Building container image...${NC}"
IMAGE_URL="gcr.io/$PROJECT_ID/adco-agent:latest"
gcloud builds submit --tag $IMAGE_URL --project $PROJECT_ID .

# Deploy
echo -e "\n${BLUE}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy adco-agent \
    --image $IMAGE_URL \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 8Gi \
    --cpu 4 \
    --timeout 300 \
    --port 8000 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,LLM_PROVIDER=vertex,LLM_MODEL=gemini-pro,LOG_LEVEL=DEBUG,PYTHONUNBUFFERED=1"

echo -e "\n${GREEN}✨ DEPLOYMENT COMPLETE! ✨${NC}"
echo -e "Your agent is now live. Check the URL above."
