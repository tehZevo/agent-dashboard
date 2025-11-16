#!/usr/bin/env python3
"""
Test script for Agent Dashboard History Feature
Generates test agents with multiple status changes to test history visualization
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

DATA_FILE = Path(__file__).parent / "agent_data.json"

def create_test_history():
    """Create test data with history for agents and teams"""

    now = datetime.now()

    # List of possible status messages per status type
    status_messages = {
        "working": [
            "Processing customer requests",
            "Running data pipeline",
            "Executing task batch",
            "Analyzing logs",
            "Training ML model"
        ],
        "idle": [
            "Waiting for tasks",
            "Ready for work",
            "Idle, no tasks assigned",
            "Standby mode"
        ],
        "warning": [
            "High memory usage detected",
            "API rate limit approaching",
            "Slow response times",
            "Retrying failed operation"
        ],
        "error": [
            "Database connection failed",
            "API timeout",
            "Out of memory",
            "Task execution failed"
        ]
    }

    # Create agents with teams
    agents_config = [
        {"id": "agent-001", "team": "Data Team"},
        {"id": "agent-002", "team": "Data Team"},
        {"id": "agent-003", "team": "Data Team"},
        {"id": "agent-004", "team": "API Team"},
        {"id": "agent-005", "team": "API Team"},
        {"id": "agent-006", "team": "ML Team"},
        {"id": "agent-007", "team": None},  # Unassigned
    ]

    agents = {}
    history = {}

    # Generate history for each agent (20-30 entries over the last hour)
    for config in agents_config:
        agent_id = config["id"]
        team = config["team"]

        num_entries = random.randint(20, 30)
        agent_history = []

        # Generate historical entries
        for i in range(num_entries):
            minutes_ago = (num_entries - i) * 2  # Events every 2 minutes
            timestamp = (now - timedelta(minutes=minutes_ago)).isoformat()

            # Vary status randomly but keep it realistic
            if i < 5:
                status = random.choice(["idle", "working"])
            elif i < num_entries - 5:
                status = random.choice(["working", "working", "idle", "warning"])
            else:
                # More recent statuses
                status = random.choice(["working", "idle", "warning", "error"])

            message = random.choice(status_messages[status])

            agent_history.append({
                "timestamp": timestamp,
                "status": status,
                "message": message,
                "team": team
            })

        # Current status (most recent)
        current_status = agent_history[-1]["status"]
        current_message = agent_history[-1]["message"]

        agents[agent_id] = {
            "status_message": current_message,
            "task_status": current_status,
            "last_checkin": now.isoformat(),
            "team": team
        }

        history[agent_id] = agent_history

    # Generate team history by aggregating agent histories
    team_histories = {}

    # Aggregate all agent history entries into team history
    for agent_id, agent_history in list(history.items()):
        team = agents[agent_id].get("team")
        if team:
            team_key = f"team:{team}"
            if team_key not in team_histories:
                team_histories[team_key] = []

            # Add agent's history to team history
            for entry in agent_history:
                team_histories[team_key].append({
                    "timestamp": entry["timestamp"],
                    "status": entry["status"],
                    "message": entry["message"],
                    "agent_id": agent_id
                })

    # Sort team histories by timestamp and add to main history
    for team_key, team_history in team_histories.items():
        team_history.sort(key=lambda x: x["timestamp"])
        history[team_key] = team_history

    test_data = {
        "agents": agents,
        "history": history
    }

    with open(DATA_FILE, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"✓ Test data with history created in {DATA_FILE}")
    print(f"\nCreated {len(agents)} test agents:")
    for agent_id, agent_data in agents.items():
        team = agent_data.get('team', 'Unassigned')
        entries = len(history.get(agent_id, []))
        print(f"  - {agent_id} ({team}): {agent_data['task_status']} - {entries} history entries")

    print(f"\nTeam histories:")
    for key in history:
        if key.startswith("team:"):
            team_name = key.replace("team:", "")
            entries = len(history[key])
            print(f"  - {team_name}: {entries} history entries")

    print(f"\n✓ Start the dashboard with: python dashboard.py")
    print(f"✓ Visit http://localhost:5000 to see the history visualization")


if __name__ == "__main__":
    print("Creating test data with history for Agent Dashboard...\n")
    create_test_history()
