#!/usr/bin/env python3
"""
Agent Dashboard Web Interface
Displays agent statuses in a web interface with auto-refresh
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
from pathlib import Path
import json
import os

app = Flask(__name__)

# Data file location
DATA_FILE = Path(__file__).parent / "agent_data.json"

# Timeout in minutes before marking agent as stale
# Can be configured via STALE_TIMEOUT_MINUTES environment variable
STALE_TIMEOUT_MINUTES = int(os.getenv('STALE_TIMEOUT_MINUTES', '5'))


def load_agent_data() -> dict:
    """Load agent data from JSON file"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Ensure webhooks key exists
                if "webhooks" not in data:
                    data["webhooks"] = []
                # Ensure history key exists
                if "history" not in data:
                    data["history"] = {}
                return data
        except (json.JSONDecodeError, IOError):
            return {"agents": {}, "history": {}, "webhooks": []}
    return {"agents": {}, "history": {}, "webhooks": []}


def save_agent_data(data: dict) -> None:
    """Save agent data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


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
        "warning": {"status": "warning", "color": "yellow", "label": "Warning"},
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
    Priority: error > warning > working > idle > stale
    """
    if not agents:
        return {"status": "empty", "color": "gray", "label": "Empty"}

    statuses = [agent["display_status"] for agent in agents]

    # Priority order
    if "error" in statuses:
        return {"status": "error", "color": "red", "label": "Error"}
    elif "warning" in statuses:
        return {"status": "warning", "color": "yellow", "label": "Warning"}
    elif "working" in statuses:
        return {"status": "working", "color": "green", "label": "Working"}
    elif "idle" in statuses:
        return {"status": "idle", "color": "blue", "label": "Idle"}
    elif "stale" in statuses:
        return {"status": "stale", "color": "gray", "label": "Stale"}
    else:
        return {"status": "unknown", "color": "gray", "label": "Unknown"}


def calculate_24h_breakdown(agent_id: str, history: dict, current_status: str, current_time: datetime) -> dict:
    """
    Calculate the percentage breakdown of time spent in each status over the last 24 hours

    Returns dict with percentages for each status:
    {
        "working": 45.5,
        "idle": 30.2,
        "warning": 10.0,
        "error": 5.3,
        "offline": 9.0
    }
    """
    # Initialize breakdown
    breakdown = {
        "working": 0.0,
        "idle": 0.0,
        "warning": 0.0,
        "error": 0.0,
        "offline": 0.0
    }

    # Get agent history
    agent_history = history.get(agent_id, [])
    if not agent_history:
        # No history - assume offline for 24h
        breakdown["offline"] = 100.0
        return breakdown

    # Filter history to last 24 hours
    cutoff_time = current_time - timedelta(hours=24)

    # Build timeline of status changes
    timeline = []
    for entry in agent_history:
        try:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if timestamp >= cutoff_time:
                status = entry.get("status", "unknown")
                # Map status to our categories
                if status in ["working"]:
                    category = "working"
                elif status in ["idle"]:
                    category = "idle"
                elif status in ["warning"]:
                    category = "warning"
                elif status in ["error"]:
                    category = "error"
                else:
                    category = "offline"
                timeline.append((timestamp, category))
        except (ValueError, TypeError, KeyError):
            continue

    # Sort timeline by timestamp
    timeline.sort(key=lambda x: x[0])

    # If no valid history in last 24h, check if agent is currently active
    if not timeline:
        # Check if agent has recent check-in
        try:
            last_checkin = datetime.fromisoformat(agent_history[-1]["timestamp"])
            time_diff = current_time - last_checkin
            if time_diff > timedelta(hours=24):
                breakdown["offline"] = 100.0
            else:
                # Agent is active but no status changes in 24h
                if current_status in ["working", "idle", "warning", "error"]:
                    breakdown[current_status] = 100.0
                else:
                    breakdown["offline"] = 100.0
        except (ValueError, TypeError, KeyError, IndexError):
            breakdown["offline"] = 100.0
        return breakdown

    # Add current status to timeline
    timeline.append((current_time, current_status if current_status in breakdown else "offline"))

    # Calculate time spent in each status
    total_seconds = 24 * 60 * 60  # 24 hours in seconds

    # Start from 24h ago
    start_time = cutoff_time

    # If first timeline entry is after cutoff, assume offline until then
    if timeline[0][0] > start_time:
        offline_duration = (timeline[0][0] - start_time).total_seconds()
        breakdown["offline"] += offline_duration
        start_time = timeline[0][0]

    # Calculate duration for each status period
    for i in range(len(timeline) - 1):
        current_entry = timeline[i]
        next_entry = timeline[i + 1]

        status = current_entry[1]
        duration = (next_entry[0] - current_entry[0]).total_seconds()

        if status in breakdown:
            breakdown[status] += duration

    # Convert to percentages
    for status in breakdown:
        breakdown[status] = round((breakdown[status] / total_seconds) * 100, 1)

    return breakdown


@app.route('/api/agents')
def get_agents():
    """API endpoint to get all agent statuses"""
    data = load_agent_data()
    agents_list = []
    teams_dict = {}
    history = data.get("history", {})
    current_time = datetime.now()

    for agent_id, agent_info in data.get("agents", {}).items():
        display_status = get_agent_display_status(
            agent_info.get("last_checkin", ""),
            agent_info.get("task_status", "unknown")
        )

        # Calculate 24h breakdown
        breakdown_24h = calculate_24h_breakdown(
            agent_id,
            history,
            agent_info.get("task_status", "unknown"),
            current_time
        )

        agent = {
            "id": agent_id,
            "status_message": agent_info.get("status_message", ""),
            "task_status": agent_info.get("task_status", "unknown"),
            "last_checkin": agent_info.get("last_checkin", ""),
            "display_status": display_status["status"],
            "display_color": display_status["color"],
            "display_label": display_status["label"],
            "team": agent_info.get("team", None),
            "description": agent_info.get("description", None),
            "role": agent_info.get("role", None),
            "breakdown_24h": breakdown_24h
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


@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """API endpoint to delete a specific agent"""
    data = load_agent_data()

    if agent_id in data.get("agents", {}):
        del data["agents"][agent_id]
        save_agent_data(data)
        return jsonify({"success": True, "message": f"Agent '{agent_id}' deleted successfully"})
    else:
        return jsonify({"success": False, "message": f"Agent '{agent_id}' not found"}), 404


@app.route('/api/teams/<team_name>', methods=['DELETE'])
def delete_team(team_name):
    """API endpoint to delete all agents in a specific team"""
    data = load_agent_data()
    agents = data.get("agents", {})

    # Find all agents in this team
    agents_to_delete = [agent_id for agent_id, agent_info in agents.items()
                       if agent_info.get("team") == team_name]

    if not agents_to_delete:
        return jsonify({"success": False, "message": f"No agents found in team '{team_name}'"}), 404

    # Delete all agents in the team
    for agent_id in agents_to_delete:
        del data["agents"][agent_id]

    save_agent_data(data)
    return jsonify({
        "success": True,
        "message": f"Deleted {len(agents_to_delete)} agent(s) from team '{team_name}'",
        "deleted_count": len(agents_to_delete)
    })


@app.route('/api/history')
def get_history():
    """API endpoint to get history for all agents and teams"""
    data = load_agent_data()
    history = data.get("history", {})

    # Process history to include display status for each entry
    processed_history = {}
    for key, entries in history.items():
        processed_entries = []
        for entry in entries:
            display_status = get_agent_display_status(
                entry.get("timestamp", ""),
                entry.get("status", "unknown")
            )
            processed_entry = {
                **entry,
                "display_status": display_status["status"],
                "display_color": display_status["color"],
                "display_label": display_status["label"]
            }
            processed_entries.append(processed_entry)
        processed_history[key] = processed_entries

    return jsonify(processed_history)


@app.route('/api/webhooks', methods=['GET'])
def get_webhooks():
    """API endpoint to get all registered webhooks"""
    data = load_agent_data()
    return jsonify({
        "webhooks": data.get("webhooks", [])
    })


@app.route('/api/webhooks', methods=['POST'])
def add_webhook():
    """API endpoint to add a new webhook"""
    webhook_data = request.get_json()

    if not webhook_data or "url" not in webhook_data:
        return jsonify({"error": "URL is required"}), 400

    url = webhook_data["url"]
    events = webhook_data.get("events", ["all"])

    # Load current data
    data = load_agent_data()

    # Check if webhook already exists
    existing = next((w for w in data["webhooks"] if w["url"] == url), None)
    if existing:
        return jsonify({"error": "Webhook URL already registered"}), 400

    # Add new webhook
    webhook = {
        "url": url,
        "events": events,
        "created_at": datetime.now().isoformat()
    }
    data["webhooks"].append(webhook)

    # Save data
    save_agent_data(data)

    return jsonify({
        "message": "Webhook added successfully",
        "webhook": webhook
    }), 201


@app.route('/api/webhooks', methods=['DELETE'])
def remove_webhook():
    """API endpoint to remove a webhook"""
    webhook_data = request.get_json()

    if not webhook_data or "url" not in webhook_data:
        return jsonify({"error": "URL is required"}), 400

    url = webhook_data["url"]

    # Load current data
    data = load_agent_data()

    # Find and remove webhook
    initial_count = len(data["webhooks"])
    data["webhooks"] = [w for w in data["webhooks"] if w["url"] != url]

    if len(data["webhooks"]) == initial_count:
        return jsonify({"error": "Webhook URL not found"}), 404

    # Save data
    save_agent_data(data)

    return jsonify({
        "message": "Webhook removed successfully"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
