# ADK Quick Start Guide

## 5-Minute Setup

### 1. Install ADK

```bash
pip install google-adk
```

### 2. Verify Installation

```bash
python learning/adk/test_adk_setup.py
```

### 3. Create Your First Agent

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="my_agent",
    llm_model="gpt-4"
)

result = await agent.execute({"task": "Hello!"})
```

## Key Concepts (30 seconds each)

### LlmAgent
- Uses LLM for reasoning
- Best for: Analysis, Q&A, decision-making

### SequentialAgent
- Executes steps in order
- Best for: Pipelines, workflows

### ParallelAgent
- Executes tasks concurrently
- Best for: Performance, independent tasks

### Coordinator
- Orchestrates multiple agents
- Best for: Complex workflows

## Next Steps

1. Read full guide: `docs/adk/README.md`
2. Study examples: `examples/adk/`
3. Complete exercises: `learning/adk/`
4. Plan integration: `docs/adk/integration_strategy.md`

## Resources

- Full Documentation: `docs/adk/README.md`
- Setup Guide: `docs/adk/setup.md`
- Learning Guide: `learning/adk/agent_classes.md`
- Integration Strategy: `docs/adk/integration_strategy.md`

