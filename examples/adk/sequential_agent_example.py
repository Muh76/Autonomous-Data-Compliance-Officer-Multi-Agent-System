"""Example: SequentialAgent for report generation."""

# Note: This is a template/example. Actual ADK imports may differ.

try:
    from google.adk.agents import SequentialAgent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("Note: ADK not installed. This is an example template.")


async def step1_collect_data(context: dict) -> dict:
    """Step 1: Collect compliance findings."""
    print("Step 1: Collecting data...")
    context["findings"] = [
        {"id": 1, "type": "risk", "severity": "high"},
        {"id": 2, "type": "gap", "severity": "medium"},
    ]
    return context


async def step2_analyze_data(context: dict) -> dict:
    """Step 2: Analyze findings."""
    print("Step 2: Analyzing data...")
    findings = context.get("findings", [])
    context["analysis"] = {
        "total_findings": len(findings),
        "high_severity": sum(1 for f in findings if f["severity"] == "high"),
        "summary": "Found 2 compliance issues requiring attention"
    }
    return context


async def step3_generate_summary(context: dict) -> dict:
    """Step 3: Generate executive summary."""
    print("Step 3: Generating summary...")
    analysis = context.get("analysis", {})
    context["summary"] = f"""
    Executive Summary:
    - Total Findings: {analysis.get('total_findings', 0)}
    - High Severity: {analysis.get('high_severity', 0)}
    - {analysis.get('summary', 'No summary available')}
    """
    return context


async def step4_format_report(context: dict) -> dict:
    """Step 4: Format final report."""
    print("Step 4: Formatting report...")
    context["report"] = {
        "title": "Compliance Report",
        "summary": context.get("summary", ""),
        "findings": context.get("findings", []),
        "analysis": context.get("analysis", {})
    }
    return context


def create_report_agent():
    """Create a SequentialAgent for report generation."""
    if not ADK_AVAILABLE:
        print("ADK not available. Returning mock agent structure.")
        return None
    
    agent = SequentialAgent(
        name="report_generator",
        steps=[
            step1_collect_data,
            step2_analyze_data,
            step3_generate_summary,
            step4_format_report
        ]
    )
    
    return agent


async def example_usage():
    """Example of using the sequential agent."""
    agent = create_report_agent()
    
    if agent:
        result = await agent.execute({})
        print("\nFinal Report:")
        print(result.get("report", {}))
    else:
        print("Example usage (mock):")
        print("  Would execute steps sequentially:")
        print("    1. Collect data")
        print("    2. Analyze data")
        print("    3. Generate summary")
        print("    4. Format report")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())

