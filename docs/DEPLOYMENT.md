# ADCO Deployment Guide

## Deployment Options

ADCO can be deployed in multiple ways depending on your needs:

1. **Local Development** - For testing and development
2. **Docker** - Containerized deployment
3. **Google Cloud Run** - Serverless deployment
4. **Kubernetes** - Production-scale deployment

---

## Option 1: Local Development

### Prerequisites
- Python 3.11+
- 8GB RAM minimum
- Google Cloud credentials (for Vertex AI)

### Steps
```bash
# 1. Clone and setup
git clone https://github.com/Muh76/Autonomous-Data-Compliance-Officer-Multi-Agent-System.git
cd adco_project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Run API server
python -m app.api.main
```

**Access**: `http://localhost:8000`

---

## Option 2: Docker Deployment

### Build and Run
```bash
# Build image
docker build -t adco:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v $(pwd)/credentials.json:/app/credentials.json \
  --name adco-api \
  adco:latest
```

### Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services**:
- API: `http://localhost:8000`
- ChromaDB: `http://localhost:8001`
- Dashboard: `http://localhost:8501`

---

## Option 3: Google Cloud Run

### Prerequisites
- Google Cloud account
- `gcloud` CLI installed
- Docker installed

### Steps

#### 1. Build and Push Image
```bash
# Set project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push
docker build -t gcr.io/$PROJECT_ID/adco:latest .
docker push gcr.io/$PROJECT_ID/adco:latest
```

#### 2. Deploy to Cloud Run
```bash
gcloud run deploy adco \
  --image gcr.io/$PROJECT_ID/adco:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID
```

#### 3. Get Service URL
```bash
gcloud run services describe adco --region us-central1 --format 'value(status.url)'
```

### Cost Estimate
- **Free tier**: 2 million requests/month
- **Typical cost**: $10-50/month for moderate usage

---

## Option 4: Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (GKE, EKS, or AKS)
- `kubectl` configured
- Docker registry access

### Deployment Files

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adco-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: adco-api
  template:
    metadata:
      labels:
        app: adco-api
    spec:
      containers:
      - name: adco
        image: gcr.io/YOUR_PROJECT/adco:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: adco-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: adco-api
```

#### Deploy
```bash
kubectl apply -f deployment.yaml
kubectl get services adco-service
```

---

## Environment Variables

### Required
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Optional
```env
# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Logging
LOG_LEVEL=INFO

# Cache
CACHE_MAX_SIZE=1000
CACHE_DEFAULT_TTL=3600

# API
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Health Checks

### API Health
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

### ChromaDB Health
```bash
curl http://localhost:8001/api/v1/heartbeat
```

---

## Monitoring

### Logs
```bash
# Docker
docker logs -f adco-api

# Kubernetes
kubectl logs -f deployment/adco-api

# Cloud Run
gcloud run services logs read adco --region us-central1
```

### Metrics
Access Streamlit dashboard:
- Local: `http://localhost:8501`
- Docker: `http://localhost:8501`
- Cloud: Deploy dashboard separately

---

## Scaling

### Horizontal Scaling (Kubernetes)
```bash
kubectl scale deployment adco-api --replicas=5
```

### Auto-scaling (Cloud Run)
```bash
gcloud run services update adco \
  --min-instances=1 \
  --max-instances=10 \
  --region us-central1
```

---

## Security

### API Authentication
Add API key authentication:
```python
# In app/api/main.py
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.get("/api/v1/compliance/scan")
async def scan(api_key: str = Depends(api_key_header)):
    # Validate API key
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
```

### HTTPS
- **Cloud Run**: Automatic HTTPS
- **Kubernetes**: Use Ingress with cert-manager
- **Docker**: Use nginx reverse proxy

---

## Backup & Recovery

### ChromaDB Backup
```bash
# Backup
docker exec adco-chromadb tar czf /tmp/chroma-backup.tar.gz /chroma/data
docker cp adco-chromadb:/tmp/chroma-backup.tar.gz ./backups/

# Restore
docker cp ./backups/chroma-backup.tar.gz adco-chromadb:/tmp/
docker exec adco-chromadb tar xzf /tmp/chroma-backup.tar.gz -C /
```

---

## Troubleshooting

### Issue: "Out of memory"
**Solution**: Increase container memory
```bash
# Docker
docker run -m 4g adco:latest

# Kubernetes
# Update resources.limits.memory in deployment.yaml
```

### Issue: "Vertex AI authentication failed"
**Solution**: Check credentials
```bash
# Verify credentials file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
gcloud auth application-default print-access-token
```

### Issue: "ChromaDB connection refused"
**Solution**: Ensure ChromaDB is running
```bash
# Check ChromaDB status
docker ps | grep chroma

# Restart ChromaDB
docker-compose restart chromadb
```

---

## Performance Tuning

### Enable Caching
```python
from adk.tools.cache import cache_llm_response

@cache_llm_response(ttl=3600)
async def expensive_llm_call():
    # Your LLM call here
    pass
```

### Optimize ChromaDB
```python
# Use batch operations
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)
```

---

## Production Checklist

- [ ] Set up monitoring (logs, metrics, alerts)
- [ ] Configure backups (ChromaDB, session data)
- [ ] Enable HTTPS/TLS
- [ ] Add API authentication
- [ ] Set up rate limiting
- [ ] Configure auto-scaling
- [ ] Test disaster recovery
- [ ] Document runbooks
- [ ] Set up CI/CD pipeline
- [ ] Load testing

---

## Support

- **Issues**: [GitHub Issues](https://github.com/Muh76/Autonomous-Data-Compliance-Officer-Multi-Agent-System/issues)
- **Email**: mj.babaie@gmail.com
- **Documentation**: See `docs/` directory
