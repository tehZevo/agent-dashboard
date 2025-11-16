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


@app.route('/api/agents')
def get_agents():
    """API endpoint to get all agent statuses"""
    data = load_agent_data()
    agents_list = []

    for agent_id, agent_info in data.get("agents", {}).items():
        display_status = get_agent_display_status(
            agent_info.get("last_checkin", ""),
            agent_info.get("task_status", "unknown")
        )

        agents_list.append({
            "id": agent_id,
            "status_message": agent_info.get("status_message", ""),
            "task_status": agent_info.get("task_status", "unknown"),
            "last_checkin": agent_info.get("last_checkin", ""),
            "display_status": display_status["status"],
            "display_color": display_status["color"],
            "display_label": display_status["label"]
        })

    # Sort by last check-in time (most recent first)
    agents_list.sort(
        key=lambda x: x.get("last_checkin", ""),
        reverse=True
    )

    return jsonify({"agents": agents_list})


@app.route('/api/config')
def get_config():
    """API endpoint to get configuration"""
    return jsonify({
        "stale_timeout_minutes": STALE_TIMEOUT_MINUTES
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
