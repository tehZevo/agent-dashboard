#!/usr/bin/env python3
from fastmcp import FastMCP
from lib.tool_handlers import handle_set_status, handle_get_status, handle_list_agents

mcp = FastMCP("agent-dashboard")

@mcp.tool
def set_agent_status(
    agent_id: str,
    status_message: str,
    task_status: str,
    team: str = None,
    description: str = None,
    role: str = None
) -> str:
    """
    Update an agent's status message and task state.
    
    Args:
        agent_id: Unique identifier for the agent
        status_message: Short description of what the agent is working on
        task_status: Current task status (idle, working, warning, or error)
        team: Optional team name for grouping agents
        description: Optional description of the agent's purpose and capabilities
        role: Optional role name for the agent (e.g., 'Data Processor', 'API Handler')
    
    Returns:
        A confirmation message with the updated status details
    """
    if task_status not in ["idle", "working", "warning", "error"]:
        raise ValueError(f"Invalid task_status: {task_status}. Must be one of: idle, working, warning, error")
    
    args = {
        "agent_id": agent_id,
        "status_message": status_message,
        "task_status": task_status,
        "team": team,
        "description": description,
        "role": role
    }
    result = handle_set_status(args)
    return result[0].text

@mcp.tool
def get_agent_status(agent_id: str) -> str:
    """
    Get the current status of a specific agent.
    
    Args:
        agent_id: Unique identifier for the agent
    
    Returns:
        JSON string containing the agent's current status information
    """
    args = {"agent_id": agent_id}
    result = handle_get_status(args)
    return result[0].text

@mcp.tool
def list_all_agents() -> str:
    """
    Get a list of all registered agents and their statuses.
    
    Returns:
        JSON string containing all agents and their status information
    """
    args = {}
    result = handle_list_agents(args)
    return result[0].text

if __name__ == "__main__":
    mcp.run()
