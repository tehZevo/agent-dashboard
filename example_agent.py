#!/usr/bin/env python3
import time
import random

def example_workflow():
    aid = "example-agent-001"

    print(f"Agent {aid} starting...")
    print("Setting status to 'idle'")
    time.sleep(2)

    print(f"\nAgent {aid} received work")
    print("Setting status to 'working'")
    time.sleep(3)

    print(f"\nAgent {aid} updating progress")
    print("Updating status message")
    time.sleep(2)

    print(f"\nAgent {aid} completed work")
    print("Setting status back to 'idle'")

    print(f"\nAgent {aid} encountered an error")
    print("Setting status to 'error'")

def heartbeat_example():
    aid = "heartbeat-agent"

    print(f"\nAgent {aid} starting continuous operation...")
    print("Sending heartbeat every 60 seconds\n")

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
        time.sleep(1)

    print("\nContinuous operation example completed")

if __name__ == "__main__":
    print("=== Example Agent Workflow ===")
    example_workflow()

    print("\n" + "="*50 + "\n")

    print("=== Continuous Heartbeat Example ===")
    heartbeat_example()

    print("\n" + "="*50)
    print("\nNote: Use MCP protocol to call set_agent_status tool")
