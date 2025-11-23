# Setup Guide for ADCO

## Prerequisites

- **Python**: 3.11 or higher
- **Git**: For cloning the repository
- **Google Cloud Account**: For Vertex AI access (optional for local testing)
- **8GB RAM**: Minimum for running ChromaDB and agents

---

## Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/Muh76/Autonomous-Data-Compliance-Officer-Multi-Agent-System.git
cd adco_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Google Cloud (for Vertex AI)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Optional: Google Search API
GOOGLE_SEARCH_API_KEY=your-api-key
GOOGLE_SEARCH_ENGINE_ID=your-engine-id
```

### 5. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific demos
python tests/test_multi_turn.py
python examples/parallel_retrieval_demo.py
python evaluation/evaluate_agents.py
```

### 6. Start API Server
```bash
python -m app.api.main
```

API will be available at `http://localhost:8000`

### 7. Start Dashboard (Optional)
```bash
streamlit run dashboard.py
```

Dashboard will be available at `http://localhost:8501`

---

## Detailed Setup

### Google Cloud Setup

#### 1. Create Google Cloud Project
```bash
gcloud projects create adco-project --name="ADCO"
gcloud config set project adco-project
```

#### 2. Enable Required APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

#### 3. Create Service Account
```bash
gcloud iam service-accounts create adco-sa \
    --display-name="ADCO Service Account"

gcloud projects add-iam-policy-binding adco-project \
    --member="serviceAccount:adco-sa@adco-project.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud iam service-accounts keys create ~/adco-key.json \
    --iam-account=adco-sa@adco-project.iam.gserviceaccount.com
```

#### 4. Set Environment Variable
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/adco-key.json"
```

Add to `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=/Users/yourname/adco-key.json
GOOGLE_CLOUD_PROJECT=adco-project
```

---

### ChromaDB Setup

ChromaDB is included in `requirements.txt` and runs locally by default.

#### Option 1: Local (Default)
No additional setup needed. ChromaDB will create a local directory.

#### Option 2: Docker
```bash
docker run -d -p 8000:8000 chromadb/chroma
```

Update `.env`:
```env
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

---

### Running with Docker

#### Build and Run
```bash
docker-compose up --build
```

This starts:
- API server on port 8000
- ChromaDB on port 8001
- Dashboard on port 8501

#### Stop Services
```bash
docker-compose down
```

---

## Verification

### Test API
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "agents": 6,
  "version": "1.0.0"
}
```

### Test Compliance Scan
```bash
curl -X POST http://localhost:8000/api/v1/compliance/scan \
  -H "Content-Type: application/json" \
  -d '{
    "source": "production_db",
    "source_type": "database"
  }'
```

### Run Evaluation
```bash
python evaluation/evaluate_agents.py
```

Check `evaluation/evaluation_report.json` for results.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'google.adk'"
```bash
pip install google-adk
```

### "Vertex AI authentication failed"
```bash
gcloud auth application-default login
# Or set GOOGLE_APPLICATION_CREDENTIALS
```

### "ChromaDB connection error"
```bash
# Check if ChromaDB is running
docker ps | grep chroma

# Or restart
docker-compose restart chromadb
```

### "ImportError: cannot import name 'Session'"
```bash
pip install --upgrade google-adk
```

### Tests fail with "No module named 'pytest'"
```bash
pip install pytest pytest-asyncio pytest-cov
```

---

## Development Setup

### Install Development Dependencies
```bash
pip install -r requirements.txt
pip install black ruff mypy pytest pytest-cov pytest-asyncio
```

### Run Linting
```bash
# Format code
black adk/ app/ tests/

# Check linting
ruff check adk/ app/ tests/

# Type checking
mypy adk/ app/ --ignore-missing-imports
```

### Run Tests with Coverage
```bash
pytest tests/ -v --cov=adk --cov=app --cov-report=html
open htmlcov/index.html
```

---

## Next Steps

1. **Explore Examples**: Check `examples/` for usage patterns
2. **Read Documentation**: See `docs/` for architecture and guides
3. **Run Demos**: Try `test_multi_turn.py` and `parallel_retrieval_demo.py`
4. **Customize**: Modify agents in `adk/agents/` for your use case
5. **Deploy**: Follow `docs/DEPLOYMENT.md` for production deployment

---

## Support

- **Issues**: [GitHub Issues](https://github.com/Muh76/Autonomous-Data-Compliance-Officer-Multi-Agent-System/issues)
- **Email**: mj.babaie@gmail.com
- **Documentation**: See `docs/FAQ.md`
