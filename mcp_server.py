#!/usr/bin/env python3
import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from lib.tool_handlers import handle_set_status, handle_get_status, handle_list_agents

app = Server("agent-dashboard")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="set_agent_status",
            description="Update an agent's status message and task state",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Unique identifier for the agent"},
                    "status_message": {"type": "string", "description": "Short description of what the agent is working on"},
                    "task_status": {"type": "string", "enum": ["idle", "working", "warning", "error"], "description": "Current task status of the agent"},
                    "team": {"type": "string", "description": "Optional team name for grouping agents"},
                    "description": {"type": "string", "description": "Optional description of the agent's purpose and capabilities"},
                    "role": {"type": "string", "description": "Optional role name for the agent (e.g., 'Data Processor', 'API Handler')"}
                },
                "required": ["agent_id", "status_message", "task_status"]
            }
        ),
        Tool(
            name="get_agent_status",
            description="Get the current status of a specific agent",
            inputSchema={
                "type": "object",
                "properties": {"agent_id": {"type": "string", "description": "Unique identifier for the agent"}},
                "required": ["agent_id"]
            }
        ),
        Tool(
            name="list_all_agents",
            description="Get a list of all registered agents and their statuses",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    if name == "set_agent_status":
        return handle_set_status(arguments)
    elif name == "get_agent_status":
        return handle_get_status(arguments)
    elif name == "list_all_agents":
        return handle_list_agents(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
