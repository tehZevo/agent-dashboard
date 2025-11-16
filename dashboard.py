#!/usr/bin/env python3
"""
Agent Dashboard Web Interface
Displays agent statuses in a web interface with auto-refresh
"""
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from pathlib import Path
import json

app = Flask(__name__)

# Data file location
DATA_FILE = Path(__file__).parent / "agent_data.json"

# Timeout in minutes before marking agent as stale
STALE_TIMEOUT_MINUTES = 5


def load_agent_data() -> dict:
    """Load agent data from JSON file"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"agents": {}}
    return {"agents": {}}


def get_agent_display_status(last_checkin_str: str, task_status: str) -> dict:
    """
    Determine the display status based on last check-in time
    Returns dict with status and color
    """
    try:
        last_checkin = datetime.fromisoformat(last_checkin_str)
        time_diff = datetime.now() - last_checkin

        # If agent hasn't checked in within the timeout, mark as stale
        if time_diff > timedelta(minutes=STALE_TIMEOUT_MINUTES):
            return {
                "status": "stale",
                "color": "gray",
                "label": "Stale"
            }
    except (ValueError, TypeError):
        # If we can't parse the date, consider it stale
        return {
            "status": "stale",
            "color": "gray",
            "label": "Stale"
        }

    # Map task status to colors
    status_map = {
        "idle": {"status": "idle", "color": "blue", "label": "Idle"},
        "working": {"status": "working", "color": "green", "label": "Working"},
        "error": {"status": "error", "color": "red", "label": "Error"}
    }

    return status_map.get(task_status, {
        "status": "unknown",
        "color": "gray",
        "label": "Unknown"
    })


@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')


def calculate_team_status(agents):
    """
    Calculate overall team status based on individual agent statuses
    Priority: error > working > idle > stale
    """
    if not agents:
        return {"status": "empty", "color": "gray", "label": "Empty"}

    statuses = [agent["display_status"] for agent in agents]

    # Priority order
    if "error" in statuses:
        return {"status": "error", "color": "red", "label": "Error"}
    elif "working" in statuses:
        return {"status": "working", "color": "green", "label": "Working"}
    elif "idle" in statuses:
        return {"status": "idle", "color": "blue", "label": "Idle"}
    elif "stale" in statuses:
        return {"status": "stale", "color": "gray", "label": "Stale"}
    else:
        return {"status": "unknown", "color": "gray", "label": "Unknown"}


@app.route('/api/agents')
def get_agents():
    """API endpoint to get all agent statuses"""
    data = load_agent_data()
    agents_list = []
    teams_dict = {}

    for agent_id, agent_info in data.get("agents", {}).items():
        display_status = get_agent_display_status(
            agent_info.get("last_checkin", ""),
            agent_info.get("task_status", "unknown")
        )

        agent = {
            "id": agent_id,
            "status_message": agent_info.get("status_message", ""),
            "task_status": agent_info.get("task_status", "unknown"),
            "last_checkin": agent_info.get("last_checkin", ""),
            "display_status": display_status["status"],
            "display_color": display_status["color"],
            "display_label": display_status["label"],
            "team": agent_info.get("team", None)
        }

        agents_list.append(agent)

        # Group by team
        team_name = agent_info.get("team", None)
        if team_name:
            if team_name not in teams_dict:
                teams_dict[team_name] = []
            teams_dict[team_name].append(agent)

    # Sort agents by last check-in time (most recent first)
    agents_list.sort(
        key=lambda x: x.get("last_checkin", ""),
        reverse=True
    )

    # Build teams list with calculated statuses
    teams_list = []
    for team_name, team_agents in teams_dict.items():
        # Sort team agents by last check-in
        team_agents.sort(
            key=lambda x: x.get("last_checkin", ""),
            reverse=True
        )

        team_status = calculate_team_status(team_agents)
        teams_list.append({
            "name": team_name,
            "agents": team_agents,
            "agent_count": len(team_agents),
            "status": team_status["status"],
            "color": team_status["color"],
            "label": team_status["label"]
        })

    # Sort teams by name
    teams_list.sort(key=lambda x: x["name"])

    # Separate agents without teams
    unassigned_agents = [a for a in agents_list if not a["team"]]

    return jsonify({
        "agents": agents_list,
        "teams": teams_list,
        "unassigned_agents": unassigned_agents
    })


@app.route('/api/config')
def get_config():
    """API endpoint to get configuration"""
    return jsonify({
        "stale_timeout_minutes": STALE_TIMEOUT_MINUTES
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
