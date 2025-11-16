from datetime import datetime
from mcp.types import TextContent
import json
from lib.data_io import load_data, save_data
from lib.webhook import trigger

def handle_set_status(args):
    agent_id = args["agent_id"]
    status_msg = args["status_message"]
    task_status = args["task_status"]
    team = args.get("team")
    desc = args.get("description")
    role = args.get("role")

    data = load_data()
    ensure_history(data)

    is_new = agent_id not in data["agents"]
    old_status = data["agents"].get(agent_id, {}).get("task_status")
    changed = not is_new and old_status != task_status
    now = datetime.now().isoformat()

    update_agent(data, agent_id, status_msg, task_status, team, desc, role, now)
    add_history(data, agent_id, task_status, status_msg, team, desc, role, now)
    if team:
        add_team_history(data, team, agent_id, task_status, status_msg, desc, role, now)

    save_data(data)

    webhook_data = build_webhook_data(agent_id, status_msg, task_status, team, desc, role, now, old_status, changed)
    send_webhooks(is_new, changed, task_status, webhook_data)

    return [TextContent(type="text", text=format_response(agent_id, task_status, status_msg, team, desc, role))]

def ensure_history(data):
    if "history" not in data:
        data["history"] = {}

def update_agent(data, aid, msg, status, team, desc, role, now):
    data["agents"][aid] = {"status_message": msg, "task_status": status, "last_checkin": now}
    if team:
        data["agents"][aid]["team"] = team
    if desc:
        data["agents"][aid]["description"] = desc
    if role:
        data["agents"][aid]["role"] = role

def add_history(data, aid, status, msg, team, desc, role, now):
    if aid not in data["history"]:
        data["history"][aid] = []

    entry = {"timestamp": now, "status": status, "message": msg, "team": team}
    if desc:
        entry["description"] = desc
    if role:
        entry["role"] = role

    data["history"][aid].append(entry)
    if len(data["history"][aid]) > 100:
        data["history"][aid] = data["history"][aid][-100:]

def add_team_history(data, team, aid, status, msg, desc, role, now):
    key = f"team:{team}"
    if key not in data["history"]:
        data["history"][key] = []

    entry = {"timestamp": now, "status": status, "message": msg, "agent_id": aid}
    if desc:
        entry["description"] = desc
    if role:
        entry["role"] = role

    data["history"][key].append(entry)
    if len(data["history"][key]) > 100:
        data["history"][key] = data["history"][key][-100:]

def build_webhook_data(aid, msg, status, team, desc, role, now, old_status, changed):
    wh_data = {"agent_id": aid, "status_message": msg, "task_status": status, "team": team, "timestamp": now}
    if desc:
        wh_data["description"] = desc
    if role:
        wh_data["role"] = role
    if changed:
        wh_data["previous_status"] = old_status
    return wh_data

def send_webhooks(is_new, changed, status, data):
    if is_new:
        trigger("agent_online", data)
    else:
        trigger("status_update", data)
        if changed:
            trigger(f"status_changed_to_{status}", data)

def format_response(aid, status, msg, team, desc, role):
    parts = [f"Agent '{aid}' status updated successfully.", f"Status: {status}", f"Message: {msg}"]
    if team:
        parts.append(f"Team: {team}")
    if desc:
        parts.append(f"Description: {desc}")
    if role:
        parts.append(f"Role: {role}")
    return "\n".join(parts)

def handle_get_status(args):
    aid = args["agent_id"]
    data = load_data()
    if aid in data["agents"]:
        return [TextContent(type="text", text=json.dumps(data["agents"][aid], indent=2))]
    return [TextContent(type="text", text=f"Agent '{aid}' not found")]

def handle_list_agents(args):
    data = load_data()
    return [TextContent(type="text", text=json.dumps(data["agents"], indent=2))]
