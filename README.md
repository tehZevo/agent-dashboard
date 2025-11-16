# Agent Dashboard

A simple web-based dashboard for monitoring AI agents via the Model Context Protocol (MCP).

## Features

- **Real-time agent monitoring**: View all active agents and their current status
- **Status tracking**: Agents can report four states: idle, working, warning, or error
- **Status messages**: Each agent can set a short description of what they're working on
- **Stale detection**: Automatically marks agents as "stale" if they haven't checked in within 5 minutes
- **Auto-refresh**: Dashboard updates every 2 seconds
- **Clean web interface**: Modern, responsive design with color-coded status indicators

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Start the MCP Server

The MCP server provides the interface for agents to communicate their status:

```bash
python mcp_server.py
```

The server runs on stdio and can be configured in MCP client settings.

### 2. Start the Web Dashboard

In a separate terminal, start the web dashboard:

```bash
python dashboard.py
```

The dashboard will be available at `http://localhost:5000`

### 3. Configure MCP Client

Add the MCP server to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "agent-dashboard": {
      "command": "python",
      "args": ["/path/to/agent-dashboard/mcp_server.py"]
    }
  }
}
```

## Agent Integration

Agents can communicate with the dashboard using the following MCP tools:

### set_agent_status

Update an agent's status:

```python
{
  "agent_id": "agent-001",
  "status_message": "Processing user requests",
  "task_status": "working"  // Options: "idle", "working", "warning", "error"
}
```

### get_agent_status

Retrieve a specific agent's status:

```python
{
  "agent_id": "agent-001"
}
```

### list_all_agents

Get all registered agents and their statuses (no parameters required).

## Status States

- **Working** (Green): Agent is actively processing tasks
- **Idle** (Blue): Agent is waiting for work
- **Warning** (Yellow): Agent is having issues but attempting to resolve them
- **Error** (Red): Agent encountered an error
- **Stale** (Gray): Agent hasn't checked in within 5 minutes

## Example Agent Client

See `example_agent.py` for a sample implementation of how an agent can update its status via MCP.

## Configuration

You can modify the stale timeout by editing the `STALE_TIMEOUT_MINUTES` variable in `dashboard.py` (default: 5 minutes).

## File Structure

```
agent-dashboard/
├── mcp_server.py          # MCP server for agent communication
├── dashboard.py           # Flask web application
├── templates/
│   └── index.html        # Dashboard HTML template
├── static/
│   └── style.css         # Dashboard styles
├── agent_data.json       # Agent status data (auto-generated)
├── example_agent.py      # Example agent implementation
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## License

MIT
