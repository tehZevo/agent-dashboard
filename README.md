# Agent Dashboard

A simple web-based dashboard for monitoring AI agents via the Model Context Protocol (MCP).

## Features

- **Real-time agent monitoring**: View all active agents and their current status
- **Team organization**: Group agents into teams for better organization
- **Collapseable teams**: Click team headers to expand/collapse team sections
- **Team status aggregation**: Overall team status calculated from individual agent statuses
- **Status tracking**: Agents can report four states: idle, working, warning, or error
- **Status messages**: Each agent can set a short description of what they're working on
- **Stale detection**: Automatically marks agents as "stale" if they haven't checked in within 5 minutes
- **Auto-refresh**: Dashboard updates every 2 seconds
- **Clean web interface**: Modern, responsive design with color-coded status indicators
- **Webhook integrations**: Subscribe to status update events via HTTP webhooks
- **Browser notifications**: Real-time desktop notifications when agents transition to error or stale states
- **Notification center**: View and manage recent alerts with a notification panel in the dashboard

## Installation

### Option 1: Docker (Recommended)

The easiest way to run the agent dashboard is using Docker:

1. Clone this repository
2. Start the services:

```bash
docker-compose up -d
```

The dashboard will be available at `http://localhost:5000`

To view logs:
```bash
docker-compose logs -f
```

To stop the services:
```bash
docker-compose down
```

### Option 2: Local Python Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Docker Usage

If you're using Docker (recommended), both services are already running after `docker-compose up`. You can:

- Access the dashboard at `http://localhost:5000`
- Configure MCP clients to connect to the containerized MCP server
- Data persists in `agent_data.json` in your project directory

### Local Python Usage

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
  "task_status": "working",  // Options: "idle", "working", "warning", "error"
  "team": "Production Team"  // Optional: assign agent to a team
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

## Teams

Agents can be organized into teams by specifying a `team` parameter when updating their status. The dashboard will:

- Group agents by team in collapseable sections
- Calculate overall team status based on all agents in the team
- Team status priority (highest to lowest): Error > Warning > Working > Idle > Stale
- Display team member count and aggregate status
- Show unassigned agents in a separate section

Click on a team header to collapse or expand the team's agents. The collapse state persists during dashboard auto-refresh.

## Notifications

The dashboard includes a real-time notification system to alert you when agents encounter issues.

### Browser Notifications

- Desktop notifications appear when agents transition to **error** or **stale** states
- Notifications are triggered by state changes (not when an agent is already in error/stale)
- On first visit, the browser will request permission to show notifications
- Error state notifications require interaction to dismiss for increased visibility
- Clicking a notification brings focus to the dashboard and opens the notification panel

### Notification Center

- Access the notification center via the bell icon in the top-right corner of the dashboard
- View all recent notifications with timestamps and status change details
- Unread notifications are highlighted with a badge showing the count
- Opening the panel automatically marks all notifications as read
- Clear all notifications with the "Clear All" button
- Notifications persist in browser localStorage across page refreshes
- Maximum of 50 notifications are stored (oldest are automatically removed)

### Notification Details

Each notification includes:
- **Agent ID**: Which agent triggered the notification
- **Status change**: The transition (e.g., "working → error")
- **Message**: The agent's status message at the time of transition
- **Timestamp**: When the state change occurred

## Webhook Integrations

The dashboard supports webhook integrations to send real-time notifications when agent status updates occur. Webhooks can be managed via MCP tools or the REST API.

### Webhook Events

Webhooks can subscribe to the following event types:

- **status_update**: Triggered when an existing agent updates its status
- **agent_online**: Triggered when a new agent comes online (first status update)
- **agent_offline**: Reserved for future use (agents going offline)
- **all**: Subscribe to all event types

### Webhook Payload Format

Webhooks receive POST requests with the following JSON payload:

```json
{
  "event": "status_update",
  "timestamp": "2025-11-16T12:34:56.789012",
  "data": {
    "agent_id": "agent-001",
    "status_message": "Processing user requests",
    "task_status": "working",
    "team": "Production Team",
    "timestamp": "2025-11-16T12:34:56.789012"
  }
}
```

### Managing Webhooks via MCP Tools

Use the following MCP tools to manage webhooks:

#### add_webhook

Register a new webhook URL:

```python
{
  "url": "https://example.com/webhook",
  "events": ["status_update", "agent_online"]  // Optional, defaults to ["all"]
}
```

#### remove_webhook

Remove a registered webhook:

```python
{
  "url": "https://example.com/webhook"
}
```

#### list_webhooks

List all registered webhooks (no parameters required).

### Managing Webhooks via REST API

#### GET /api/webhooks

List all registered webhooks:

```bash
curl http://localhost:5000/api/webhooks
```

#### POST /api/webhooks

Add a new webhook:

```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["status_update", "agent_online"]
  }'
```

#### DELETE /api/webhooks

Remove a webhook:

```bash
curl -X DELETE http://localhost:5000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/webhook"}'
```

### Webhook Delivery

- Webhooks are delivered asynchronously to avoid blocking status updates
- Delivery timeout is set to 10 seconds
- Failed webhook deliveries are logged but do not affect agent status updates
- Webhooks receive HTTP POST requests with `Content-Type: application/json` header

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
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose orchestration
├── .dockerignore         # Docker build ignore patterns
└── README.md            # This file
```

## License

MIT
