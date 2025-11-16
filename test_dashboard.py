#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timedelta

DATA_FILE = Path(__file__).parent / "agent_data.json"

def create_test_data():
    now = datetime.now()
    test_data = {
        "agents": {
            "agent-001": {
                "status_message": "Processing customer requests",
                "task_status": "working",
                "last_checkin": now.isoformat(),
                "description": "Handles customer service requests and inquiries",
                "role": "Customer Service Agent"
            },
            "agent-002": {
                "status_message": "Idle, waiting for tasks",
                "task_status": "idle",
                "last_checkin": (now - timedelta(minutes=1)).isoformat(),
                "description": "Processes background tasks and batch jobs",
                "role": "Background Worker"
            },
            "agent-003": {
                "status_message": "Database connection failed",
                "task_status": "error",
                "last_checkin": (now - timedelta(minutes=2)).isoformat(),
                "description": "Manages database operations and data persistence",
                "role": "Database Manager"
            },
            "agent-004": {
                "status_message": "Running data analysis pipeline",
                "task_status": "working",
                "last_checkin": (now - timedelta(seconds=30)).isoformat(),
                "description": "Analyzes data and generates insights",
                "role": "Data Analyst"
            },
            "agent-005": {
                "status_message": "Last seen over 5 minutes ago",
                "task_status": "working",
                "last_checkin": (now - timedelta(minutes=10)).isoformat(),
                "description": "Monitors system health and performance metrics",
                "role": "System Monitor"
            }
        }
    }

    with open(DATA_FILE, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"✓ Test data created in {DATA_FILE}")
    print(f"\nCreated {len(test_data['agents'])} test agents:")
    for aid, adata in test_data['agents'].items():
        print(f"  - {aid}: {adata['task_status']} - {adata['status_message']}")

    print(f"\n✓ Start dashboard: python dashboard.py")
    print(f"✓ Visit http://localhost:5000")

if __name__ == "__main__":
    print("Creating test data for Agent Dashboard...\n")
    create_test_data()
