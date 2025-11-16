from flask import Blueprint, jsonify, request
from datetime import datetime
from lib.data_io import load_data, save_data

team_bp = Blueprint('teams', __name__)

@team_bp.route('/api/teams', methods=['GET'])
def get_teams():
    data = load_data()
    teams_list = []
    for tid, cfg in data.get("teams", {}).items():
        teams_list.append({
            "id": tid,
            "name": cfg.get("name", tid),
            "description": cfg.get("description", ""),
            "agent_ids": cfg.get("agent_ids", [])
        })
    return jsonify({"teams": teams_list})

@team_bp.route('/api/teams', methods=['POST'])
def create_team():
    team_data = request.get_json()
    if not team_data or "id" not in team_data:
        return jsonify({"error": "Team ID is required"}), 400

    tid = team_data["id"]
    name = team_data.get("name", tid)
    desc = team_data.get("description", "")
    aids = team_data.get("agent_ids", [])

    data = load_data()
    if tid in data.get("teams", {}):
        return jsonify({"error": f"Team '{tid}' already exists"}), 400

    if "teams" not in data:
        data["teams"] = {}

    data["teams"][tid] = {"name": name, "description": desc, "agent_ids": aids}
    save_data(data)

    return jsonify({
        "message": "Team created successfully",
        "team": {"id": tid, "name": name, "description": desc, "agent_ids": aids}
    }), 201

@team_bp.route('/api/teams/<team_id>', methods=['PUT'])
def update_team(team_id):
    team_data = request.get_json()
    if not team_data:
        return jsonify({"error": "Team data is required"}), 400

    data = load_data()
    if team_id not in data.get("teams", {}):
        return jsonify({"error": f"Team '{team_id}' not found"}), 404

    if "name" in team_data:
        data["teams"][team_id]["name"] = team_data["name"]
    if "description" in team_data:
        data["teams"][team_id]["description"] = team_data["description"]
    if "agent_ids" in team_data:
        data["teams"][team_id]["agent_ids"] = team_data["agent_ids"]

    save_data(data)

    return jsonify({
        "message": "Team updated successfully",
        "team": {
            "id": team_id,
            "name": data["teams"][team_id]["name"],
            "description": data["teams"][team_id]["description"],
            "agent_ids": data["teams"][team_id]["agent_ids"]
        }
    })

@team_bp.route('/api/teams/<team_id>/agents/<agent_id>', methods=['POST'])
def add_agent_to_team(team_id, agent_id):
    data = load_data()
    if team_id not in data.get("teams", {}):
        return jsonify({"error": f"Team '{team_id}' not found"}), 404

    if agent_id not in data["teams"][team_id]["agent_ids"]:
        data["teams"][team_id]["agent_ids"].append(agent_id)
        save_data(data)
        return jsonify({"message": f"Agent '{agent_id}' added to team '{team_id}'"})
    return jsonify({"message": f"Agent '{agent_id}' is already in team '{team_id}'"})

@team_bp.route('/api/teams/<team_id>/agents/<agent_id>', methods=['DELETE'])
def remove_agent_from_team(team_id, agent_id):
    data = load_data()
    if team_id not in data.get("teams", {}):
        return jsonify({"error": f"Team '{team_id}' not found"}), 404

    if agent_id in data["teams"][team_id]["agent_ids"]:
        data["teams"][team_id]["agent_ids"].remove(agent_id)
        save_data(data)
        return jsonify({"message": f"Agent '{agent_id}' removed from team '{team_id}'"})
    return jsonify({"error": f"Agent '{agent_id}' is not in team '{team_id}'"}), 404
