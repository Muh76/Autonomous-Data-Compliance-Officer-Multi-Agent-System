"""
Multi-agent workflow patterns for Coordinator.
Demonstrates sequential, parallel, and loop execution patterns.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from ..core.logger import get_logger

logger = get_logger(__name__)


class WorkflowPatterns:
    """
    Multi-agent workflow execution patterns.
    
    Implements three core patterns:
    1. Sequential: Step-by-step execution (A → B → C)
    2. Parallel: Concurrent execution (A || B || C)
    3. Loop: Feedback-driven iteration (A → Critic → A)
    """
    
    @staticmethod
    async def execute_sequential(
        agents: List[tuple],
        initial_input: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially (pipeline pattern).
        
        Each agent's output becomes the next agent's input.
        
        Args:
            agents: List of (agent, input_key) tuples
            initial_input: Initial workflow input
            session_id: Session ID for context
            
        Returns:
            Final result from last agent
            
        Example:
            agents = [
                (risk_scanner, "scan_input"),
                (policy_matcher, "scan_result"),
                (report_writer, "findings")
            ]
        """
        logger.info("Starting sequential workflow", agent_count=len(agents), session_id=session_id)
        
        current_input = initial_input
        results = []
        
        for i, (agent, input_key) in enumerate(agents):
            logger.info(
                "Sequential step",
                step=i+1,
                agent=agent.name if hasattr(agent, 'name') else agent.__class__.__name__,
                session_id=session_id
            )
            
            # Prepare input for this agent
            if input_key:
                # If input_key specified, wrap current result
                agent_input = {input_key: current_input}
            else:
                # Otherwise pass through directly
                agent_input = current_input if isinstance(current_input, dict) else {"input": current_input}
            
            # Execute agent
            start_time = datetime.utcnow()
            result = await agent.process(agent_input, session_id=session_id)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                "Sequential step completed",
                step=i+1,
                duration_seconds=duration,
                session_id=session_id
            )
            
            # Store result and prepare for next step
            results.append({
                "agent": agent.name if hasattr(agent, 'name') else agent.__class__.__name__,
                "result": result,
                "duration": duration
            })
            current_input = result
        
        logger.info("Sequential workflow completed", total_steps=len(agents), session_id=session_id)
        
        return {
            "pattern": "sequential",
            "steps": results,
            "final_result": current_input
        }
    
    @staticmethod
    async def execute_parallel(
        agents: List[tuple],
        inputs: List[Dict[str, Any]],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute agents in parallel (concurrent pattern).
        
        All agents run simultaneously on their respective inputs.
        
        Args:
            agents: List of (agent, input) tuples
            inputs: List of inputs for each agent
            session_id: Session ID for context
            
        Returns:
            Combined results from all agents
            
        Example:
            agents = [
                (risk_scanner, {"source": "db1"}),
                (risk_scanner, {"source": "db2"}),
                (risk_scanner, {"source": "db3"})
            ]
        """
        logger.info("Starting parallel workflow", agent_count=len(agents), session_id=session_id)
        
        # Create tasks for all agents
        tasks = []
        for i, (agent, agent_input) in enumerate(zip(agents, inputs)):
            task = agent.process(agent_input, session_id=f"{session_id}_parallel_{i}")
            tasks.append(task)
        
        # Execute all tasks concurrently
        start_time = datetime.utcnow()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Process results
        successful_results = []
        failed_results = []
        
        for i, (agent, result) in enumerate(zip(agents, results)):
            if isinstance(result, Exception):
                logger.error(
                    "Parallel agent failed",
                    agent=agent.name if hasattr(agent, 'name') else agent.__class__.__name__,
                    error=str(result)
                )
                failed_results.append({
                    "agent": agent.name if hasattr(agent, 'name') else agent.__class__.__name__,
                    "error": str(result)
                })
            else:
                successful_results.append({
                    "agent": agent.name if hasattr(agent, 'name') else agent.__class__.__name__,
                    "result": result
                })
        
        logger.info(
            "Parallel workflow completed",
            total_agents=len(agents),
            successful=len(successful_results),
            failed=len(failed_results),
            duration_seconds=duration,
            session_id=session_id
        )
        
        return {
            "pattern": "parallel",
            "successful": successful_results,
            "failed": failed_results,
            "duration": duration
        }
    
    @staticmethod
    async def execute_loop(
        agent,
        critic_agent,
        initial_input: Dict[str, Any],
        session_id: str,
        max_iterations: int = 3,
        quality_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Execute agent with critic feedback loop (refinement pattern).
        
        Agent produces output → Critic validates → If invalid, retry with feedback.
        
        Args:
            agent: Primary agent to execute
            critic_agent: Critic agent for validation
            initial_input: Initial input for agent
            session_id: Session ID for context
            max_iterations: Maximum retry attempts
            quality_threshold: Minimum quality score to accept
            
        Returns:
            Final validated result
            
        Example:
            result = execute_loop(
                agent=policy_matcher,
                critic_agent=critic,
                initial_input={"practice": "data_collection"},
                session_id="session_123"
            )
        """
        logger.info(
            "Starting loop workflow",
            agent=agent.name if hasattr(agent, 'name') else agent.__class__.__name__,
            max_iterations=max_iterations,
            session_id=session_id
        )
        
        current_input = initial_input
        iteration_history = []
        
        for iteration in range(max_iterations):
            logger.info(
                "Loop iteration",
                iteration=iteration+1,
                max_iterations=max_iterations,
                session_id=session_id
            )
            
            # Execute primary agent
            agent_result = await agent.process(current_input, session_id=f"{session_id}_iter_{iteration}")
            
            # Validate with critic
            critic_input = {
                "agent_output": agent_result,
                "agent_type": agent.name if hasattr(agent, 'name') else agent.__class__.__name__,
                "validation_criteria": {"quality_threshold": quality_threshold}
            }
            validation = await critic_agent.process(critic_input, session_id=f"{session_id}_critic_{iteration}")
            
            # Calculate quality score
            quality_scores = validation.get("quality_scores", {})
            avg_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.0
            is_valid = validation.get("is_valid", False)
            
            iteration_history.append({
                "iteration": iteration + 1,
                "agent_result": agent_result,
                "validation": validation,
                "quality_score": avg_quality,
                "is_valid": is_valid
            })
            
            logger.info(
                "Loop iteration completed",
                iteration=iteration+1,
                quality_score=avg_quality,
                is_valid=is_valid,
                session_id=session_id
            )
            
            # Check if result is acceptable
            if is_valid and avg_quality >= quality_threshold:
                logger.info(
                    "Loop workflow completed successfully",
                    iterations=iteration+1,
                    final_quality=avg_quality,
                    session_id=session_id
                )
                return {
                    "pattern": "loop",
                    "iterations": iteration + 1,
                    "final_result": agent_result,
                    "final_quality": avg_quality,
                    "history": iteration_history
                }
            
            # Prepare feedback for next iteration
            if iteration < max_iterations - 1:
                recommendations = validation.get("recommendations", [])
                current_input = {
                    **initial_input,
                    "feedback": recommendations,
                    "previous_attempt": agent_result
                }
        
        # Max iterations reached
        logger.warning(
            "Loop workflow max iterations reached",
            max_iterations=max_iterations,
            best_quality=max([h["quality_score"] for h in iteration_history]),
            session_id=session_id
        )
        
        # Return best attempt
        best_iteration = max(iteration_history, key=lambda x: x["quality_score"])
        
        return {
            "pattern": "loop",
            "iterations": max_iterations,
            "final_result": best_iteration["agent_result"],
            "final_quality": best_iteration["quality_score"],
            "history": iteration_history,
            "warning": "Max iterations reached without meeting quality threshold"
        }
