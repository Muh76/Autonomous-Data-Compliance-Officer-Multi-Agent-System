#!/bin/bash
set -e

echo "🚀 Downloading and Installing Google Cloud SDK..."

# Use the official installer with prompts disabled for automation
curl https://sdk.cloud.google.com | bash -s -- --disable-prompts

echo "✅ Google Cloud SDK installed successfully!"
echo "----------------------------------------------------------------"
echo "⚠️  CRITICAL STEP REQUIRED:"
echo "1. You MUST restart your terminal (close and reopen) or run:"
echo "   source ~/.zshrc  (or ~/.bash_profile)"
echo "2. Then run: gcloud init"
echo "----------------------------------------------------------------"
