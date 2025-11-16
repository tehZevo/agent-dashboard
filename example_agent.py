#!/usr/bin/env python3
"""
Example Agent Client
Demonstrates how an agent can communicate with the dashboard via MCP
"""
import time
import random


def example_agent_workflow():
    """
    Example workflow showing how an agent would update its status.

    In a real implementation, the agent would call the MCP tools through
    the MCP protocol. This is a conceptual example showing the workflow.
    """

    agent_id = "example-agent-001"

    # Example 1: Agent starts and sets idle status
    print(f"Agent {agent_id} starting...")
    print("Setting status to 'idle'")
    # In reality: call set_agent_status tool with:
    # {
    #   "agent_id": "example-agent-001",
    #   "status_message": "Waiting for tasks",
    #   "task_status": "idle"
    # }

    time.sleep(2)

    # Example 2: Agent receives work and updates status
    print(f"\nAgent {agent_id} received work")
    print("Setting status to 'working'")
    # In reality: call set_agent_status tool with:
    # {
    #   "agent_id": "example-agent-001",
    #   "status_message": "Processing customer data analysis",
    #   "task_status": "working"
    # }

    time.sleep(3)

    # Example 3: Agent updates progress
    print(f"\nAgent {agent_id} updating progress")
    print("Updating status message")
    # In reality: call set_agent_status tool with:
    # {
    #   "agent_id": "example-agent-001",
    #   "status_message": "Generating final report (75% complete)",
    #   "task_status": "working"
    # }

    time.sleep(2)

    # Example 4: Agent completes work
    print(f"\nAgent {agent_id} completed work")
    print("Setting status back to 'idle'")
    # In reality: call set_agent_status tool with:
    # {
    #   "agent_id": "example-agent-001",
    #   "status_message": "Task completed successfully",
    #   "task_status": "idle"
    # }

    # Example 5: Simulating an error
    print(f"\nAgent {agent_id} encountered an error")
    print("Setting status to 'error'")
    # In reality: call set_agent_status tool with:
    # {
    #   "agent_id": "example-agent-001",
    #   "status_message": "Database connection failed",
    #   "task_status": "error"
    # }


def continuous_heartbeat_example():
    """
    Example of how an agent would send periodic heartbeats to avoid
    being marked as stale.
    """

    agent_id = "heartbeat-agent"

    print(f"\nAgent {agent_id} starting continuous operation...")
    print("Sending heartbeat every 60 seconds to avoid stale status\n")

    tasks = [
        "Analyzing log files",
        "Processing user feedback",
        "Updating knowledge base",
        "Running system diagnostics",
        "Optimizing query performance"
    ]

    for i in range(5):
        task = random.choice(tasks)
        print(f"Iteration {i+1}: {task}")

        # In reality: call set_agent_status tool with:
        # {
        #   "agent_id": "heartbeat-agent",
        #   "status_message": task,
        #   "task_status": "working"
        # }

        time.sleep(1)  # In real scenario, this would be 60 seconds or less

    print("\nContinuous operation example completed")


if __name__ == "__main__":
    print("=== Example Agent Workflow ===")
    example_agent_workflow()

    print("\n" + "="*50 + "\n")

    print("=== Continuous Heartbeat Example ===")
    continuous_heartbeat_example()

    print("\n" + "="*50)
    print("\nNote: This is a demonstration script.")
    print("To actually communicate with the dashboard, agents should")
    print("use the MCP protocol to call the set_agent_status tool.")
