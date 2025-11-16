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
import requests
from concurrent.futures import ThreadPoolExecutor

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Data file to store agent statuses
DATA_FILE = Path(__file__).parent / "agent_data.json"

# Thread pool for async webhook delivery
webhook_executor = ThreadPoolExecutor(max_workers=5)


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


def deliver_webhook(webhook_url: str, payload: dict) -> None:
    """
    Deliver a webhook payload to a URL
    Runs in a separate thread to avoid blocking
    """
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    except Exception as e:
        # Log error but don't fail the status update
        print(f"Webhook delivery failed for {webhook_url}: {str(e)}")


def trigger_webhooks(event_type: str, data: dict) -> None:
    """
    Trigger all registered webhooks with the given event data
    """
    agent_data = load_agent_data()
    webhooks = agent_data.get("webhooks", [])

    if not webhooks:
        return

    payload = {
        "event": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    # Deliver webhooks asynchronously
    for webhook in webhooks:
        webhook_url = webhook.get("url")
        webhook_events = webhook.get("events", ["all"])

        # Check if webhook should receive this event
        if "all" in webhook_events or event_type in webhook_events:
            webhook_executor.submit(deliver_webhook, webhook_url, payload)


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
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the agent's purpose and capabilities"
                    },
                    "role": {
                        "type": "string",
                        "description": "Optional role name for the agent (e.g., 'Data Processor', 'API Handler')"
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
        description = arguments.get("description", None)
        role = arguments.get("role", None)

        # Load current data
        data = load_agent_data()

        # Ensure history structure exists
        if "history" not in data:
            data["history"] = {}

        # Check if this is a new agent or status change
        is_new_agent = agent_id not in data["agents"]
        old_status = data["agents"].get(agent_id, {}).get("task_status")
        status_changed = not is_new_agent and old_status != task_status

        # Current timestamp
        now = datetime.now().isoformat()

        # Update agent status
        data["agents"][agent_id] = {
            "status_message": status_message,
            "task_status": task_status,
            "last_checkin": now
        }

        # Add optional fields if provided
        if team:
            data["agents"][agent_id]["team"] = team
        if description:
            data["agents"][agent_id]["description"] = description
        if role:
            data["agents"][agent_id]["role"] = role

        # Record history entry for agent
        if agent_id not in data["history"]:
            data["history"][agent_id] = []

        # Add history entry (keep last 100 entries)
        history_entry = {
            "timestamp": now,
            "status": task_status,
            "message": status_message,
            "team": team
        }
        if description:
            history_entry["description"] = description
        if role:
            history_entry["role"] = role

        data["history"][agent_id].append(history_entry)

        # Keep only last 100 history entries per agent
        if len(data["history"][agent_id]) > 100:
            data["history"][agent_id] = data["history"][agent_id][-100:]

        # Record history entry for team if agent belongs to one
        if team:
            team_history_key = f"team:{team}"
            if team_history_key not in data["history"]:
                data["history"][team_history_key] = []

            team_history_entry = {
                "timestamp": now,
                "status": task_status,
                "message": status_message,
                "agent_id": agent_id
            }
            if description:
                team_history_entry["description"] = description
            if role:
                team_history_entry["role"] = role

            data["history"][team_history_key].append(team_history_entry)

            # Keep only last 100 history entries per team
            if len(data["history"][team_history_key]) > 100:
                data["history"][team_history_key] = data["history"][team_history_key][-100:]

        # Save data
        save_agent_data(data)

        # Trigger webhooks
        webhook_data = {
            "agent_id": agent_id,
            "status_message": status_message,
            "task_status": task_status,
            "team": team,
            "timestamp": data["agents"][agent_id]["last_checkin"]
        }
        if description:
            webhook_data["description"] = description
        if role:
            webhook_data["role"] = role

        # Add previous status to webhook data if status changed
        if status_changed:
            webhook_data["previous_status"] = old_status

        # Trigger appropriate webhooks based on status changes
        if is_new_agent:
            trigger_webhooks("agent_online", webhook_data)
        else:
            # Always trigger general status_update for backward compatibility
            trigger_webhooks("status_update", webhook_data)

            # Trigger status-specific webhooks only when status actually changes
            if status_changed:
                # Trigger status-specific event
                status_event = f"status_changed_to_{task_status}"
                trigger_webhooks(status_event, webhook_data)

        team_info = f"\nTeam: {team}" if team else ""
        description_info = f"\nDescription: {description}" if description else ""
        role_info = f"\nRole: {role}" if role else ""
        return [TextContent(
            type="text",
            text=f"Agent '{agent_id}' status updated successfully.\nStatus: {task_status}\nMessage: {status_message}{team_info}{description_info}{role_info}"
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
