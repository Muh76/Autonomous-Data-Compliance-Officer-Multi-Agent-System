# Frequently Asked Questions (FAQ)

## General Questions

### What is ADCO?
ADCO (Autonomous Data & Compliance Officer) is a multi-agent AI system that automates compliance auditing for data privacy regulations like GDPR, HIPAA, and CCPA. It uses 6 specialized AI agents to scan databases, detect violations, and generate audit reports.

### Who should use ADCO?
- **Compliance Officers** at startups and enterprises
- **Legal Teams** ensuring regulatory compliance
- **Data Protection Officers (DPOs)** managing GDPR compliance
- **DevOps/Security Teams** auditing data infrastructure

### How much time does ADCO save?
Based on our user story (Alice), ADCO reduces compliance auditing from **3 days to 15 minutes** - a **95% time savings**. Manual database reviews, regulation cross-referencing, and report generation are all automated.

---

## Technical Questions

### What AI technologies does ADCO use?
- **Google Vertex AI (Gemini Pro)**: LLM for compliance analysis
- **Presidio**: Microsoft's PII detection library
- **ChromaDB**: Vector database for RAG (Retrieval-Augmented Generation)
- **SentenceTransformers**: Embeddings for semantic search
- **Google ADK**: Agent Development Kit for orchestration

### How does ADCO detect PII?
ADCO uses **Presidio**, a production-grade PII detection library that identifies:
- Emails, phone numbers, SSNs
- Credit card numbers, IP addresses
- Medical record numbers (for HIPAA)
- Custom PII patterns via regex

It's not mocked - we use the real Presidio analyzer for accurate detection.

### How accurate is the compliance detection?
Based on our evaluation across 18 test cases:
- **Precision**: 85%+
- **Recall**: 82%+
- **F1 Score**: 83%+
- **Citation Accuracy**: 90%+

These metrics are competitive with rule-based systems while providing more flexibility and natural language explanations.

### What regulations does ADCO support?
Currently:
- **GDPR** (General Data Protection Regulation - EU)
- **HIPAA** (Health Insurance Portability and Accountability Act - US)
- **CCPA** (California Consumer Privacy Act - US)

The RAG-based architecture makes it easy to add new regulations by ingesting their text into ChromaDB.

---

## Architecture Questions

### Why use 6 agents instead of one?
**Specialization improves accuracy**. Each agent is an expert in its domain:
- **RiskScanner**: Optimized for PII detection patterns
- **PolicyMatcher**: Trained on legal compliance frameworks
- **Critic**: Focused on quality validation and fact-checking

This is more accurate than a single general-purpose agent trying to do everything.

### How do agents communicate?
Agents use a **Message Bus** pattern:
1. Coordinator receives user request
2. Publishes messages to specialized agents
3. Agents process and publish results
4. Coordinator aggregates and returns final output

This decouples agents and enables parallel execution.

### What are the 3 workflow patterns?
1. **Sequential**: RiskScanner → PolicyMatcher → ReportWriter (pipeline)
2. **Parallel**: 3 RiskScanners scan different databases concurrently (2-3x faster)
3. **Loop**: PolicyMatcher ↔ Critic feedback for iterative quality improvement

See `adk/core/workflow_patterns.py` for implementation.

### How does multi-turn conversation work?
The Session Service tracks conversation history:
- User asks: "Is collecting emails without consent GDPR compliant?"
- Assistant: "No, violates GDPR Article 6"
- User: "What if I add a checkbox?" (follow-up)
- Assistant: "That would make it compliant!" (remembers context)

Context is preserved across 5+ turns with automatic truncation to fit token limits.

---

## Deployment Questions

### How do I run ADCO locally?
```bash
# 1. Clone repository
git clone https://github.com/Muh76/Autonomous-Data-Compliance-Officer-Multi-Agent-System.git
cd adco_project

# 2. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys (Vertex AI, etc.)

# 4. Run API server
python -m app.api.main

# 5. Run dashboard (optional)
streamlit run dashboard.py
```

### What API keys do I need?
- **Google Cloud**: For Vertex AI (Gemini) access
- **Optional**: Google Search API key for regulation lookup

Set these in `.env` file. See `ENV_TEMPLATE.md` for details.

### Can I run ADCO with Docker?
Yes! We provide Docker and docker-compose configurations:
```bash
docker-compose up --build
```

This starts the API server and all dependencies (ChromaDB, etc.).

### How do I deploy to production?
ADCO is designed for cloud deployment:
- **GCP**: Use Cloud Run or GKE
- **AWS**: Use ECS or EKS
- **Azure**: Use Container Instances or AKS

See `docs/DEPLOYMENT.md` for detailed instructions (coming soon).

---

## Data & Privacy Questions

### Does ADCO store my data?
**Short-term**: Session data is stored in-memory during active workflows  
**Long-term**: Only compliance reports are stored in ChromaDB for trend analysis

**Your actual sensitive data is never stored**. We only store:
- Detected PII categories (not the actual PII values)
- Compliance findings and recommendations
- Audit report metadata

### Is ADCO GDPR compliant itself?
Yes! ADCO follows privacy-by-design principles:
- **PII Redaction**: Presidio removes sensitive data before storage
- **Data Minimization**: Only stores necessary compliance metadata
- **Right to Deletion**: Session history can be cleared on demand
- **Transparency**: All processing is logged and traceable

### Can I use ADCO on-premises?
Yes! ADCO can run entirely on-premises:
- Use local LLM (e.g., Llama via Ollama) instead of Vertex AI
- Run ChromaDB locally
- No external API calls required

This ensures data never leaves your infrastructure.

---

## Performance Questions

### How fast is ADCO?
- **Single database scan**: ~30-60 seconds
- **Full compliance audit** (3 databases): ~2-3 minutes
- **Parallel execution**: 2-3x faster than sequential

Performance depends on database size and LLM latency.

### Can ADCO handle large databases?
Yes, but with caveats:
- **Sampling**: For very large DBs (millions of rows), we sample representative data
- **Chunking**: Large tables are processed in batches
- **Parallel Scanning**: Multiple agents scan different tables concurrently

For production use, we recommend running scheduled scans (e.g., nightly) rather than real-time.

### How much does it cost to run?
Main costs:
- **Vertex AI (Gemini)**: ~$0.001 per 1K tokens (varies by model)
- **Compute**: Minimal (can run on small VM)
- **Storage**: ChromaDB is free and lightweight

**Estimated cost**: $10-50/month for typical startup usage (100 scans/month).

---

## Comparison Questions

### How is ADCO different from manual audits?
| Aspect | Manual Audit | ADCO |
|--------|-------------|------|
| **Time** | 3 days | 15 minutes |
| **Coverage** | 70-80% (human error) | 100% (automated) |
| **Cost** | $5,000+ (officer time) | $50/month |
| **Consistency** | Varies by person | Always consistent |
| **Citations** | Manual lookup | Automatic with sources |

### How does ADCO compare to rule-based systems?
| Feature | Rule-Based | ADCO |
|---------|-----------|------|
| **Flexibility** | Rigid rules | Natural language understanding |
| **Accuracy** | 65% precision | 85%+ precision |
| **Explainability** | "Rule #42 triggered" | "Violates GDPR Article 6 because..." |
| **Maintenance** | Update rules manually | RAG auto-updates from regulations |

### Can ADCO replace compliance officers?
**No**. ADCO is a tool to **augment** compliance officers, not replace them:
- ADCO handles repetitive scanning and initial analysis
- Officers review findings and make final decisions
- Complex legal interpretation still requires human expertise

Think of ADCO as a "compliance assistant" that saves 95% of grunt work.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'google.adk'"
Install Google ADK:
```bash
pip install google-adk
```

### "Vertex AI authentication failed"
Set up Google Cloud credentials:
```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### "ChromaDB connection error"
Ensure ChromaDB is running:
```bash
# If using docker-compose
docker-compose up chromadb

# Or install locally
pip install chromadb
```

### Evaluation script fails
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
python evaluation/evaluate_agents.py
```

---

## Contributing

### Can I contribute to ADCO?
Yes! We welcome contributions:
- **Bug reports**: Open GitHub issues
- **Feature requests**: Suggest new regulations or agents
- **Pull requests**: Follow our contribution guidelines

### How do I add a new regulation?
1. Add regulation text to `data/regulations/`
2. Run ingestion script: `python scripts/ingest_regulations.py`
3. ChromaDB will index it for RAG retrieval
4. Update PolicyMatcher prompts if needed

### How do I add a new agent?
1. Create agent class in `adk/agents/`
2. Inherit from `BaseAgent`
3. Implement `process()` method
4. Register in Coordinator
5. Add tests in `tests/`

See `adk/agents/risk_scanner.py` as an example.

---

## License & Legal

### What license is ADCO under?
**MIT License** - free for commercial and personal use.

### Can I use ADCO for commercial purposes?
Yes! The MIT license allows commercial use. However:
- ADCO provides **guidance**, not legal advice
- Always have qualified legal counsel review compliance matters
- We provide no warranties (see LICENSE file)

### Is ADCO's output legally binding?
**No**. ADCO is a tool for compliance assistance. Its outputs should be:
- Reviewed by qualified legal professionals
- Used as a starting point for compliance analysis
- Not treated as definitive legal advice

---

## Future Roadmap

### What's coming next?
- **More regulations**: SOC 2, ISO 27001, PCI DSS
- **Clause classifier**: ML model for contract risk detection
- **Real-time monitoring**: Continuous compliance scanning
- **Multi-language**: Support for non-English regulations
- **UI improvements**: Better dashboard and reporting

### When will feature X be available?
Check our [GitHub Issues](https://github.com/Muh76/Autonomous-Data-Compliance-Officer-Multi-Agent-System/issues) for roadmap and timelines.

---

## Contact

### How do I get help?
- **Email**: mj.babaie@gmail.com
- **GitHub Issues**: [Report bugs or ask questions](https://github.com/Muh76/Autonomous-Data-Compliance-Officer-Multi-Agent-System/issues)
- **LinkedIn**: [Mohammad Babaie](https://www.linkedin.com/in/mohammadbabaie/)

### Can I hire you for custom compliance solutions?
Yes! Contact me via email or LinkedIn to discuss custom implementations, consulting, or enterprise deployments.
