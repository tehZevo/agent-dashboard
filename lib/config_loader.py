#!/usr/bin/env python3
import yaml
import os

CONFIG_FILE = "config.yaml"

def load_team_config():
    """
    Load team configuration from config.yaml
    Returns a dictionary mapping team IDs to team info, and a mapping of agent IDs to teams
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), CONFIG_FILE)
    
    if not os.path.exists(config_path):
        print(f"Warning: {CONFIG_FILE} not found. Using empty team configuration.")
        return {}, {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config or 'teams' not in config:
            print(f"Warning: No teams defined in {CONFIG_FILE}")
            return {}, {}
        
        teams = {}
        agent_to_team = {}
        
        for team in config['teams']:
            team_id = team.get('id')
            if not team_id:
                continue
            
            teams[team_id] = {
                'name': team.get('name', team_id),
                'description': team.get('description', ''),
                'agent_ids': team.get('agent_ids', [])
            }
            
            # Create mapping of agent_id -> team info
            for agent_id in team.get('agent_ids', []):
                agent_to_team[agent_id] = {
                    'team_id': team_id,
                    'team_name': team.get('name', team_id)
                }
        
        return teams, agent_to_team
    
    except Exception as e:
        print(f"Error loading {CONFIG_FILE}: {e}")
        return {}, {}

def get_team_for_agent(agent_id, agent_to_team):
    """
    Get the team name for a given agent ID
    Returns the team name or None if the agent is not assigned to a team
    """
    team_info = agent_to_team.get(agent_id)
    return team_info['team_name'] if team_info else None
