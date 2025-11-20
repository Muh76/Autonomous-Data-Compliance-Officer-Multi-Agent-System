# ADK Learning Resources

This directory contains learning materials and examples for Google ADK.

## Structure

```
learning/adk/
├── README.md                    # This file
├── agent_classes.md            # Detailed guide on ADK agent classes
├── test_adk_setup.py          # Test script to verify ADK installation
└── exercises/                  # Practice exercises (to be created)
```

## Learning Path

### 1. Start Here: Setup and Basics

1. Read `docs/adk/README.md` for overview
2. Follow `docs/adk/setup.md` for installation
3. Run `test_adk_setup.py` to verify setup

### 2. Understand Agent Classes

1. Read `agent_classes.md` for detailed explanations
2. Review examples in `examples/adk/`
3. Complete learning exercises

### 3. Practice with Examples

1. Study `examples/adk/simple_llm_agent.py`
2. Study `examples/adk/sequential_agent_example.py`
3. Create your own examples

### 4. Plan Integration

1. Read `docs/adk/integration_strategy.md`
2. Understand compatibility requirements
3. Plan agent migration

## Exercises

### Exercise 1: Simple LlmAgent

Create a LlmAgent that:
- Answers questions about compliance
- Uses a tool to retrieve regulation information
- Handles errors gracefully

### Exercise 2: SequentialAgent Pipeline

Create a SequentialAgent that:
- Collects data
- Processes data
- Generates output
- Saves results

### Exercise 3: ParallelAgent Scanner

Create a ParallelAgent that:
- Scans multiple data sources concurrently
- Aggregates results
- Handles errors in parallel execution

### Exercise 4: Coordinator Workflow

Create a Coordinator that:
- Orchestrates 2-3 agents
- Manages workflow state
- Handles errors and retries

## Resources

- [ADK Documentation](docs/adk/README.md)
- [Setup Guide](docs/adk/setup.md)
- [Integration Strategy](docs/adk/integration_strategy.md)
- [Example Code](../examples/adk/)

## Next Steps

After completing the learning materials:

1. ✅ Understand ADK architecture
2. ✅ Know when to use each agent type
3. ✅ Understand tool system
4. ✅ Plan integration with ADCO
5. → Proceed to Phase 1 implementation




