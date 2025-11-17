# ADK Agent Classes Learning Guide

## Overview

This document provides a detailed learning guide for understanding and using ADK's built-in agent classes.

## LlmAgent

### What is LlmAgent?

LlmAgent is an agent that uses Large Language Models (LLMs) for reasoning, decision-making, and natural language understanding.

### Key Features

- LLM-powered reasoning
- Tool integration
- Context management
- Natural language interaction

### When to Use

- Risk analysis and assessment
- Policy matching and compliance checking
- Natural language understanding tasks
- Decision-making based on complex data

### Example: Risk Scanner Agent

```python
from google.adk.agents import LlmAgent
from google.adk.tools import Tool

class DataScanTool(Tool):
    name = "scan_data"
    description = "Scans data source for potential risks"
    
    def run(self, source: str):
        # Scan implementation
        return {"risks": [...]}

# Create LlmAgent for risk scanning
risk_scanner = LlmAgent(
    name="risk_scanner",
    tools=[DataScanTool()],
    llm_model="gpt-4",
    system_prompt="You are a risk analysis expert..."
)
```

### Learning Exercise

1. Create a simple LlmAgent that answers questions about compliance
2. Add a tool that retrieves regulation information
3. Test the agent with sample queries

## SequentialAgent

### What is SequentialAgent?

SequentialAgent executes a series of tasks in a defined order, where each step depends on the previous one.

### Key Features

- Step-by-step execution
- Context passing between steps
- Error handling at each step
- Progress tracking

### When to Use

- Report generation pipelines
- Multi-step data processing
- Workflow automation
- Sequential compliance checks

### Example: Report Writer Agent

```python
from google.adk.agents import SequentialAgent

async def collect_data(context):
    # Step 1: Collect compliance findings
    context["findings"] = await gather_findings()
    return context

async def analyze_data(context):
    # Step 2: Analyze findings
    context["analysis"] = await analyze(context["findings"])
    return context

async def generate_report(context):
    # Step 3: Generate report
    context["report"] = await create_report(context["analysis"])
    return context

async def save_report(context):
    # Step 4: Save report
    await save_to_filesystem(context["report"])
    return context

# Create SequentialAgent
report_writer = SequentialAgent(
    name="report_writer",
    steps=[collect_data, analyze_data, generate_report, save_report]
)
```

### Learning Exercise

1. Create a SequentialAgent with 3-4 simple steps
2. Add error handling to each step
3. Test with different input scenarios

## ParallelAgent

### What is ParallelAgent?

ParallelAgent executes multiple tasks concurrently, improving performance for independent operations.

### Key Features

- Concurrent execution
- Independent task processing
- Result aggregation
- Performance optimization

### When to Use

- Scanning multiple data sources
- Parallel compliance checks
- Concurrent risk assessments
- Independent data processing

### Example: Parallel Scanner

```python
from google.adk.agents import ParallelAgent

async def scan_database(context):
    # Scan database
    return {"source": "database", "risks": [...]}

async def scan_filesystem(context):
    # Scan filesystem
    return {"source": "filesystem", "risks": [...]}

async def scan_api(context):
    # Scan API
    return {"source": "api", "risks": [...]}

# Create ParallelAgent
parallel_scanner = ParallelAgent(
    name="parallel_scanner",
    tasks=[scan_database, scan_filesystem, scan_api]
)

# Execute in parallel
results = await parallel_scanner.execute({})
# Results will contain outputs from all three tasks
```

### Learning Exercise

1. Create a ParallelAgent with 3 independent tasks
2. Measure performance improvement vs sequential execution
3. Handle errors in parallel execution

## Coordinator

### What is Coordinator?

Coordinator orchestrates multiple agents, managing workflows and coordinating agent interactions.

### Key Features

- Agent orchestration
- Workflow management
- Result aggregation
- Error handling across agents

### When to Use

- Complex multi-agent workflows
- Agent coordination and delegation
- Workflow orchestration
- Result aggregation from multiple agents

### Example: Compliance Coordinator

```python
from google.adk.agents import Coordinator, LlmAgent, SequentialAgent

# Create individual agents
risk_scanner = LlmAgent(name="risk_scanner", ...)
policy_matcher = LlmAgent(name="policy_matcher", ...)
report_writer = SequentialAgent(name="report_writer", ...)

# Create Coordinator
coordinator = Coordinator(
    name="compliance_coordinator",
    agents={
        "scanner": risk_scanner,
        "matcher": policy_matcher,
        "writer": report_writer
    }
)

# Orchestrate workflow
async def audit_workflow(workflow_input):
    # Step 1: Scan for risks
    scan_result = await coordinator.agents["scanner"].execute({
        "data_sources": workflow_input["sources"]
    })
    
    # Step 2: Match against policies
    match_result = await coordinator.agents["matcher"].execute({
        "scan_results": scan_result,
        "framework": workflow_input["framework"]
    })
    
    # Step 3: Generate report
    report = await coordinator.agents["writer"].execute({
        "findings": match_result
    })
    
    return report
```

### Learning Exercise

1. Create a Coordinator with 2-3 simple agents
2. Implement a workflow that uses all agents
3. Add error handling and retry logic

## Comparison Table

| Agent Type | Use Case | Execution | Best For |
|------------|----------|-----------|----------|
| LlmAgent | LLM-powered tasks | Single task | Analysis, reasoning |
| SequentialAgent | Step-by-step workflows | Sequential | Pipelines, reports |
| ParallelAgent | Independent tasks | Concurrent | Performance, scanning |
| Coordinator | Multi-agent orchestration | Orchestrated | Complex workflows |

## Best Practices

1. **Choose the Right Agent Type**: Match agent type to your use case
2. **Keep Agents Focused**: Each agent should have a clear purpose
3. **Handle Errors**: Implement robust error handling
4. **Test Thoroughly**: Test each agent type independently
5. **Document Patterns**: Document how you use each agent type

## Next Steps

1. Complete learning exercises for each agent type
2. Create example implementations for ADCO use cases
3. Integrate ADK agents into ADCO architecture
4. Test integration with message bus and state manager

