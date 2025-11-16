#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from lib.data_io import load_data, save_data
from lib.status import get_display_status, calc_team_status, STALE_TIMEOUT
from lib.history import calc_24h_breakdown

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/agents')
def get_agents():
    data = load_data()
    agents_list = build_agents_list(data)
    teams_list = build_teams_list(agents_list)
    unassigned = [a for a in agents_list if not a["team"]]
    return jsonify({"agents": agents_list, "teams": teams_list, "unassigned_agents": unassigned})

def build_agents_list(data):
    agents_list = []
    history = data.get("history", {})
    current_time = datetime.now()

    for agent_id, info in data.get("agents", {}).items():
        display_status = get_display_status(info.get("last_checkin", ""), info.get("task_status", "unknown"))
        breakdown = calc_24h_breakdown(agent_id, history, info.get("task_status", "unknown"), current_time)

        # Get team info from configuration (not from agent data)
        team_info = agent_to_team.get(agent_id, None)
        team_name = team_info["team_name"] if team_info else None
        team_id = team_info["team_id"] if team_info else None

        agent = {
            "id": agent_id,
            "status_message": info.get("status_message", ""),
            "task_status": info.get("task_status", "unknown"),
            "last_checkin": info.get("last_checkin", ""),
            "display_status": display_status["status"],
            "display_color": display_status["color"],
            "display_label": display_status["label"],
            "team": info.get("team", None),
            "description": info.get("description", None),
            "role": info.get("role", None),
            "breakdown_24h": breakdown
        }
        agents_list.append(agent)

    agents_list.sort(key=lambda x: x.get("last_checkin", ""), reverse=True)
    return agents_list

def build_teams_list(agents_list):
    teams_dict = {}
    for agent in agents_list:
        team_name = agent.get("team")
        if team_name:
            if team_name not in teams_dict:
                teams_dict[team_name] = {
                    "team_id": team_id,
                    "team_description": team_info.get("team_description", ""),
                    "agents": []
                }
            teams_dict[team_name]["agents"].append(agent)

    teams_list = []
    for name, agents in teams_dict.items():
        agents.sort(key=lambda x: x.get("last_checkin", ""), reverse=True)
        team_status = calc_team_status(agents)
        teams_list.append({
            "name": name,
            "agents": agents,
            "agent_count": len(agents),
            "status": team_status["status"],
            "color": team_status["color"],
            "label": team_status["label"]
        })

    teams_list.sort(key=lambda x: x["name"])
    return teams_list

@app.route('/api/config')
def get_config():
    return jsonify({"stale_timeout_minutes": STALE_TIMEOUT})

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    data = load_data()
    if agent_id in data.get("agents", {}):
        del data["agents"][agent_id]
        save_data(data)
        return jsonify({"success": True, "message": f"Agent '{agent_id}' deleted successfully"})
    return jsonify({"success": False, "message": f"Agent '{agent_id}' not found"}), 404

@app.route('/api/teams/<team_name>', methods=['DELETE'])
def delete_team(team_name):
    data = load_data()
    agents = data.get("agents", {})
    to_delete = [aid for aid, info in agents.items() if info.get("team") == team_name]

    if not to_delete:
        return jsonify({"success": False, "message": f"No agents found in team '{team_name}'"}), 404

    for aid in to_delete:
        del data["agents"][aid]

    save_data(data)
    return jsonify({"success": True, "message": f"Deleted {len(to_delete)} agent(s) from team '{team_name}'", "deleted_count": len(to_delete)})

@app.route('/api/history')
def get_history():
    data = load_data()
    history = data.get("history", {})
    processed = {}

    for key, entries in history.items():
        proc_entries = []
        for entry in entries:
            display = get_display_status(entry.get("timestamp", ""), entry.get("status", "unknown"))
            proc_entry = {**entry, "display_status": display["status"], "display_color": display["color"], "display_label": display["label"]}
            proc_entries.append(proc_entry)
        processed[key] = proc_entries

    return jsonify(processed)

@app.route('/api/webhooks', methods=['GET'])
def get_webhooks():
    data = load_data()
    return jsonify({"webhooks": data.get("webhooks", [])})

@app.route('/api/webhooks', methods=['POST'])
def add_webhook():
    webhook_data = request.get_json()
    if not webhook_data or "url" not in webhook_data:
        return jsonify({"error": "URL is required"}), 400

    url = webhook_data["url"]
    events = webhook_data.get("events", ["all"])
    data = load_data()

    if any(w["url"] == url for w in data["webhooks"]):
        return jsonify({"error": "Webhook URL already registered"}), 400

    webhook = {"url": url, "events": events, "created_at": datetime.now().isoformat()}
    data["webhooks"].append(webhook)
    save_data(data)

    return jsonify({"message": "Webhook added successfully", "webhook": webhook}), 201

@app.route('/api/webhooks', methods=['DELETE'])
def remove_webhook():
    webhook_data = request.get_json()
    if not webhook_data or "url" not in webhook_data:
        return jsonify({"error": "URL is required"}), 400

    url = webhook_data["url"]
    data = load_data()
    initial_count = len(data["webhooks"])
    data["webhooks"] = [w for w in data["webhooks"] if w["url"] != url]

    if len(data["webhooks"]) == initial_count:
        return jsonify({"error": "Webhook URL not found"}), 404

    save_data(data)
    return jsonify({"message": "Webhook removed successfully"})

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """API endpoint to get all team configurations"""
    data = load_agent_data()
    teams_list = []

    for team_id, team_config in data.get("teams", {}).items():
        teams_list.append({
            "id": team_id,
            "name": team_config.get("name", team_id),
            "description": team_config.get("description", ""),
            "agent_ids": team_config.get("agent_ids", [])
        })

    return jsonify({
        "teams": teams_list
    })


@app.route('/api/teams', methods=['POST'])
def create_team():
    """API endpoint to create a new team"""
    team_data = request.get_json()

    if not team_data or "id" not in team_data:
        return jsonify({"error": "Team ID is required"}), 400

    team_id = team_data["id"]
    team_name = team_data.get("name", team_id)
    team_description = team_data.get("description", "")
    agent_ids = team_data.get("agent_ids", [])

    # Load current data
    data = load_agent_data()

    # Check if team already exists
    if team_id in data["teams"]:
        return jsonify({"error": f"Team '{team_id}' already exists"}), 400

    # Create new team
    data["teams"][team_id] = {
        "name": team_name,
        "description": team_description,
        "agent_ids": agent_ids
    }

    # Save data
    save_agent_data(data)

    return jsonify({
        "message": "Team created successfully",
        "team": {
            "id": team_id,
            "name": team_name,
            "description": team_description,
            "agent_ids": agent_ids
        }
    }), 201


@app.route('/api/teams/<team_id>', methods=['PUT'])
def update_team(team_id):
    """API endpoint to update a team configuration"""
    team_data = request.get_json()

    if not team_data:
        return jsonify({"error": "Team data is required"}), 400

    # Load current data
    data = load_agent_data()

    # Check if team exists
    if team_id not in data["teams"]:
        return jsonify({"error": f"Team '{team_id}' not found"}), 404

    # Update team
    if "name" in team_data:
        data["teams"][team_id]["name"] = team_data["name"]
    if "description" in team_data:
        data["teams"][team_id]["description"] = team_data["description"]
    if "agent_ids" in team_data:
        data["teams"][team_id]["agent_ids"] = team_data["agent_ids"]

    # Save data
    save_agent_data(data)

    return jsonify({
        "message": "Team updated successfully",
        "team": {
            "id": team_id,
            "name": data["teams"][team_id]["name"],
            "description": data["teams"][team_id]["description"],
            "agent_ids": data["teams"][team_id]["agent_ids"]
        }
    })


@app.route('/api/teams/<team_id>/agents/<agent_id>', methods=['POST'])
def add_agent_to_team(team_id, agent_id):
    """API endpoint to add an agent to a team"""
    data = load_agent_data()

    # Check if team exists
    if team_id not in data["teams"]:
        return jsonify({"error": f"Team '{team_id}' not found"}), 404

    # Add agent to team if not already present
    if agent_id not in data["teams"][team_id]["agent_ids"]:
        data["teams"][team_id]["agent_ids"].append(agent_id)

        # Save data
        save_agent_data(data)

        return jsonify({
            "message": f"Agent '{agent_id}' added to team '{team_id}'"
        })
    else:
        return jsonify({
            "message": f"Agent '{agent_id}' is already in team '{team_id}'"
        })


@app.route('/api/teams/<team_id>/agents/<agent_id>', methods=['DELETE'])
def remove_agent_from_team(team_id, agent_id):
    """API endpoint to remove an agent from a team"""
    data = load_agent_data()

    # Check if team exists
    if team_id not in data["teams"]:
        return jsonify({"error": f"Team '{team_id}' not found"}), 404

    # Remove agent from team
    if agent_id in data["teams"][team_id]["agent_ids"]:
        data["teams"][team_id]["agent_ids"].remove(agent_id)

        # Save data
        save_agent_data(data)

        return jsonify({
            "message": f"Agent '{agent_id}' removed from team '{team_id}'"
        })
    else:
        return jsonify({
            "error": f"Agent '{agent_id}' is not in team '{team_id}'"
        }), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
