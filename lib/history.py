from datetime import datetime, timedelta

def calc_24h_breakdown(agent_id, history, current_status, current_time):
    breakdown = init_breakdown()
    agent_hist = history.get(agent_id, [])

    if not agent_hist:
        breakdown["offline"] = 100.0
        return breakdown

    cutoff = current_time - timedelta(hours=24)
    timeline = build_timeline(agent_hist, cutoff)

    if not timeline:
        return handle_no_timeline(agent_hist, current_status, current_time, breakdown)

    timeline.append((current_time, get_category(current_status, breakdown)))
    return calc_percentages(timeline, cutoff, breakdown)

def init_breakdown():
    return {"working": 0.0, "idle": 0.0, "warning": 0.0, "error": 0.0, "offline": 0.0}

def build_timeline(hist, cutoff):
    timeline = []
    for entry in hist:
        ts, cat = parse_entry(entry, cutoff)
        if ts:
            timeline.append((ts, cat))
    timeline.sort(key=lambda x: x[0])
    return timeline

def parse_entry(entry, cutoff):
    try:
        ts = datetime.fromisoformat(entry["timestamp"])
        if ts >= cutoff:
            cat = get_category(entry.get("status", "unknown"), {})
            return ts, cat
    except (ValueError, TypeError, KeyError):
        pass
    return None, None

def get_category(status, breakdown):
    cats = {"working": "working", "idle": "idle", "warning": "warning", "error": "error"}
    return cats.get(status, "offline")

def handle_no_timeline(hist, status, curr_time, breakdown):
    try:
        last = datetime.fromisoformat(hist[-1]["timestamp"])
        diff = curr_time - last
        if diff > timedelta(hours=24):
            breakdown["offline"] = 100.0
        elif status in breakdown:
            breakdown[status] = 100.0
        else:
            breakdown["offline"] = 100.0
    except (ValueError, TypeError, KeyError, IndexError):
        breakdown["offline"] = 100.0
    return breakdown

def calc_percentages(timeline, cutoff, breakdown):
    total_secs = 24 * 60 * 60
    start = cutoff

    if timeline[0][0] > start:
        offline_dur = (timeline[0][0] - start).total_seconds()
        breakdown["offline"] += offline_dur
        start = timeline[0][0]

    for i in range(len(timeline) - 1):
        curr_entry = timeline[i]
        next_entry = timeline[i + 1]
        status = curr_entry[1]
        dur = (next_entry[0] - curr_entry[0]).total_seconds()
        if status in breakdown:
            breakdown[status] += dur

    for status in breakdown:
        breakdown[status] = round((breakdown[status] / total_secs) * 100, 1)

    return breakdown
