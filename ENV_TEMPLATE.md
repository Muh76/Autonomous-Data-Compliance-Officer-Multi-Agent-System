# Environment Variables Template

Create a `.env` file in the project root with the following variables:

```bash
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
API_SECRET_KEY=your_secret_key_here_change_in_production

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
```

## Setup Instructions

1. Copy this template to create your `.env` file:
   ```bash
   cp ENV_TEMPLATE.md .env
   # Then edit .env with your actual values
   ```

2. Or create `.env` manually and add the variables above with your actual values.

3. **Important**: Never commit `.env` to version control. It's already in `.gitignore`.

## Required Variables

Minimum required variables for basic functionality:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (at least one LLM provider)
- `LLM_PROVIDER` (openai or anthropic)

All other variables have defaults and are optional.




