# ADCO Multi-Agent System

Autonomous Data & Compliance Officer Multi-Agent System

## Overview

The ADCO (Autonomous Data & Compliance Officer) Multi-Agent System is a comprehensive compliance monitoring and reporting system that uses multiple specialized AI agents to:

- Scan data sources for compliance risks
- Match data practices against regulations
- Generate compliance reports
- Continuously monitor compliance status

## Architecture

The system consists of 6 specialized agents:

1. **Coordinator Agent**: Orchestrates workflows and coordinates other agents
2. **Risk Scanner Agent**: Scans data sources and detects risks
3. **Policy Matcher Agent**: Matches data practices against compliance regulations using RAG
4. **Report Writer Agent**: Generates compliance reports in multiple formats
5. **Critic Agent**: Validates quality and consistency of agent outputs
6. **Watchdog Agent**: Continuously monitors system and triggers audits

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

The system uses both YAML configuration (`adk/config.yaml`) and environment variables (`.env`).

Key configuration options:
- LLM provider and model selection
- Database connection
- Vector store configuration
- Agent settings
- API settings

## Usage

### Running the API Server

```bash
python -m app.api.main
```

Or using uvicorn directly:
```bash
uvicorn app.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /api/v1/compliance/scan` - Trigger a compliance scan
- `POST /api/v1/compliance/audit` - Trigger a compliance audit
- `GET /api/v1/compliance/workflow/{workflow_id}` - Get workflow status
- `POST /api/v1/reports/generate` - Generate a compliance report
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/health` - Health check

### Using the Agents Programmatically

```python
from adk.core.message_bus import MessageBus
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue
from adk.agents import CoordinatorAgent

# Initialize components
message_bus = MessageBus()
state_manager = StateManager()
task_queue = TaskQueue()

# Create coordinator
coordinator = CoordinatorAgent(
    message_bus=message_bus,
    state_manager=state_manager,
    task_queue=task_queue,
)

await coordinator.initialize()

# Run a workflow
result = await coordinator.run({
    "workflow_type": "audit",
    "data_sources": ["database1"],
    "compliance_frameworks": ["GDPR"],
})
```

## Project Structure

```
adco_project/
├── adk/                    # Core framework
│   ├── agents/            # Agent implementations
│   ├── core/              # Core framework components
│   ├── models/            # Data models and database
│   ├── rag/               # RAG engine for regulations
│   ├── tools/             # Tools and utilities
│   └── config.py          # Configuration management
├── app/                    # Application layer
│   └── api/               # REST API
├── data/                   # Data storage
│   ├── regulations/       # Regulation documents
│   └── logs/             # Log files
├── docs/                   # Documentation
└── tests/                  # Tests
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black adco_project/
ruff check adco_project/
```

## License

[Add your license here]

## Contact

- Email: mj.babaie@gmail.com
- LinkedIn: https://www.linkedin.com/in/mohammadbabaie/
- GitHub: https://github.com/Muh76
