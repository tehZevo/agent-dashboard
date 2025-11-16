#!/usr/bin/env python3
"""
Test script for the Agent Dashboard
Simulates multiple agents updating their status
"""
import json
from pathlib import Path
from datetime import datetime, timedelta


DATA_FILE = Path(__file__).parent / "agent_data.json"


def create_test_data():
    """Create test agent data"""

    now = datetime.now()

    test_data = {
        "agents": {
            "agent-001": {
                "status_message": "Processing customer requests",
                "task_status": "working",
                "last_checkin": now.isoformat()
            },
            "agent-002": {
                "status_message": "Idle, waiting for tasks",
                "task_status": "idle",
                "last_checkin": (now - timedelta(minutes=1)).isoformat()
            },
            "agent-003": {
                "status_message": "Database connection failed",
                "task_status": "error",
                "last_checkin": (now - timedelta(minutes=2)).isoformat()
            },
            "agent-004": {
                "status_message": "Running data analysis pipeline",
                "task_status": "working",
                "last_checkin": (now - timedelta(seconds=30)).isoformat()
            },
            "agent-005": {
                "status_message": "Last seen over 5 minutes ago",
                "task_status": "working",
                "last_checkin": (now - timedelta(minutes=10)).isoformat()
            }
        }
    }

    with open(DATA_FILE, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"✓ Test data created in {DATA_FILE}")
    print(f"\nCreated {len(test_data['agents'])} test agents:")
    for agent_id, agent_data in test_data['agents'].items():
        print(f"  - {agent_id}: {agent_data['task_status']} - {agent_data['status_message']}")

    print(f"\n✓ You can now start the dashboard with: python dashboard.py")
    print(f"✓ Then visit http://localhost:5000 in your browser")


if __name__ == "__main__":
    print("Creating test data for Agent Dashboard...\n")
    create_test_data()
