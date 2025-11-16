from datetime import datetime, timedelta
import os

STALE_TIMEOUT = int(os.getenv('STALE_TIMEOUT_MINUTES', '5'))

def get_display_status(last_checkin_str, task_status):
    if is_stale(last_checkin_str):
        return create_status("stale", "gray", "Stale")
    return map_task_status(task_status)

def is_stale(last_checkin_str):
    try:
        last_checkin = datetime.fromisoformat(last_checkin_str)
        diff = datetime.now() - last_checkin
        return diff > timedelta(minutes=STALE_TIMEOUT)
    except (ValueError, TypeError):
        return True

def map_task_status(task_status):
    status_map = {
        "idle": create_status("idle", "blue", "Idle"),
        "working": create_status("working", "green", "Working"),
        "warning": create_status("warning", "yellow", "Warning"),
        "error": create_status("error", "red", "Error")
    }
    return status_map.get(task_status, create_status("unknown", "gray", "Unknown"))

def create_status(status, color, label):
    return {"status": status, "color": color, "label": label}

def calc_team_status(agents):
    if not agents:
        return create_status("empty", "gray", "Empty")
    statuses = [a["display_status"] for a in agents]
    priority = ["error", "warning", "working", "idle", "stale"]
    for p in priority:
        if p in statuses:
            return map_task_status(p) if p != "stale" else create_status("stale", "gray", "Stale")
    return create_status("unknown", "gray", "Unknown")
