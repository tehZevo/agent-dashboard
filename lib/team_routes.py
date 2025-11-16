from flask import Blueprint, jsonify
from lib.config_loader import load_team_config

team_bp = Blueprint('teams', __name__)

@team_bp.route('/api/teams', methods=['GET'])
def get_teams():
    """
    Get teams from config.yaml (read-only)
    Team creation/modification must be done by editing config.yaml
    """
    teams_config, _ = load_team_config()
    teams_list = []
    for tid, cfg in teams_config.items():
        teams_list.append({
            "id": tid,
            "name": cfg.get("name", tid),
            "description": cfg.get("description", ""),
            "agent_ids": cfg.get("agent_ids", [])
        })
    return jsonify({"teams": teams_list})

# All team creation, update, and agent assignment routes have been removed
# Teams must now be configured via config.yaml
