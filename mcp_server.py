#!/usr/bin/env python3
"""
MCP Server for Agent Dashboard
Provides tools for agents to update their status via MCP protocol
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Data file to store agent statuses
DATA_FILE = Path(__file__).parent / "agent_data.json"


def load_agent_data() -> dict:
    """Load agent data from JSON file"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"agents": {}, "history": {}}
    return {"agents": {}, "history": {}}


def save_agent_data(data: dict) -> None:
    """Save agent data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# Create MCP server instance
app = Server("agent-dashboard")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for agent status management"""
    return [
        Tool(
            name="set_agent_status",
            description="Update an agent's status message and task state",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Unique identifier for the agent"
                    },
                    "status_message": {
                        "type": "string",
                        "description": "Short description of what the agent is working on"
                    },
                    "task_status": {
                        "type": "string",
                        "enum": ["idle", "working", "warning", "error"],
                        "description": "Current task status of the agent"
                    },
                    "team": {
                        "type": "string",
                        "description": "Optional team name for grouping agents"
                    }
                },
                "required": ["agent_id", "status_message", "task_status"]
            }
        ),
        Tool(
            name="get_agent_status",
            description="Get the current status of a specific agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Unique identifier for the agent"
                    }
                },
                "required": ["agent_id"]
            }
        ),
        Tool(
            name="list_all_agents",
            description="Get a list of all registered agents and their statuses",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from agents"""

    if name == "set_agent_status":
        agent_id = arguments["agent_id"]
        status_message = arguments["status_message"]
        task_status = arguments["task_status"]
        team = arguments.get("team", None)

        # Load current data
        data = load_agent_data()

        # Ensure history structure exists
        if "history" not in data:
            data["history"] = {}

        # Current timestamp
        now = datetime.now().isoformat()

        # Update agent status
        data["agents"][agent_id] = {
            "status_message": status_message,
            "task_status": task_status,
            "last_checkin": now
        }

        # Add team if provided
        if team:
            data["agents"][agent_id]["team"] = team

        # Record history entry for agent
        if agent_id not in data["history"]:
            data["history"][agent_id] = []

        # Add history entry (keep last 100 entries)
        data["history"][agent_id].append({
            "timestamp": now,
            "status": task_status,
            "message": status_message,
            "team": team
        })

        # Keep only last 100 history entries per agent
        if len(data["history"][agent_id]) > 100:
            data["history"][agent_id] = data["history"][agent_id][-100:]

        # Record history entry for team if agent belongs to one
        if team:
            team_history_key = f"team:{team}"
            if team_history_key not in data["history"]:
                data["history"][team_history_key] = []

            data["history"][team_history_key].append({
                "timestamp": now,
                "status": task_status,
                "message": status_message,
                "agent_id": agent_id
            })

            # Keep only last 100 history entries per team
            if len(data["history"][team_history_key]) > 100:
                data["history"][team_history_key] = data["history"][team_history_key][-100:]

        # Save data
        save_agent_data(data)

        team_info = f"\nTeam: {team}" if team else ""
        return [TextContent(
            type="text",
            text=f"Agent '{agent_id}' status updated successfully.\nStatus: {task_status}\nMessage: {status_message}{team_info}"
        )]

    elif name == "get_agent_status":
        agent_id = arguments["agent_id"]
        data = load_agent_data()

        if agent_id in data["agents"]:
            agent = data["agents"][agent_id]
            return [TextContent(
                type="text",
                text=json.dumps(agent, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_id}' not found"
            )]

    elif name == "list_all_agents":
        data = load_agent_data()
        return [TextContent(
            type="text",
            text=json.dumps(data["agents"], indent=2)
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
