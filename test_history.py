#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

DATA_FILE = Path(__file__).parent / "agent_data.json"

def get_status_messages():
    return {
        "working": ["Processing customer requests", "Running data pipeline", "Executing task batch", "Analyzing logs", "Training ML model"],
        "idle": ["Waiting for tasks", "Ready for work", "Idle, no tasks assigned", "Standby mode"],
        "warning": ["High memory usage detected", "API rate limit approaching", "Slow response times", "Retrying failed operation"],
        "error": ["Database connection failed", "API timeout", "Out of memory", "Task execution failed"]
    }

def get_agents_config():
    return [
        {"id": "agent-001", "team": "Data Team"},
        {"id": "agent-002", "team": "Data Team"},
        {"id": "agent-003", "team": "Data Team"},
        {"id": "agent-004", "team": "API Team"},
        {"id": "agent-005", "team": "API Team"},
        {"id": "agent-006", "team": "ML Team"},
        {"id": "agent-007", "team": None},
    ]

def gen_agent_hist(num_entries, now, msgs):
    hist = []
    for i in range(num_entries):
        mins_ago = (num_entries - i) * 2
        ts = (now - timedelta(minutes=mins_ago)).isoformat()
        if i < 5:
            st = random.choice(["idle", "working"])
        elif i < num_entries - 5:
            st = random.choice(["working", "working", "idle", "warning"])
        else:
            st = random.choice(["working", "idle", "warning", "error"])
        msg = random.choice(msgs[st])
        hist.append({"timestamp": ts, "status": st, "message": msg})
    return hist

def build_agents(configs, now, msgs):
    agents = {}
    history = {}

    for cfg in configs:
        aid = cfg["id"]
        team = cfg["team"]
        num = random.randint(20, 30)
        hist = gen_agent_hist(num, now, msgs)

        for entry in hist:
            entry["team"] = team

        curr_st = hist[-1]["status"]
        curr_msg = hist[-1]["message"]

        agents[aid] = {
            "status_message": curr_msg,
            "task_status": curr_st,
            "last_checkin": now.isoformat(),
            "team": team
        }

        history[aid] = hist

    return agents, history

def build_team_histories(agents, history):
    teams = {}
    for aid, hist in list(history.items()):
        team = agents[aid].get("team")
        if team:
            key = f"team:{team}"
            if key not in teams:
                teams[key] = []

            for entry in hist:
                teams[key].append({
                    "timestamp": entry["timestamp"],
                    "status": entry["status"],
                    "message": entry["message"],
                    "agent_id": aid
                })

    for key, th in teams.items():
        th.sort(key=lambda x: x["timestamp"])
        history[key] = th

def print_summary(agents, history):
    print(f"✓ Test data created in {DATA_FILE}")
    print(f"\nCreated {len(agents)} test agents:")
    for aid, adata in agents.items():
        team = adata.get('team', 'Unassigned')
        entries = len(history.get(aid, []))
        print(f"  - {aid} ({team}): {adata['task_status']} - {entries} history entries")

    print(f"\nTeam histories:")
    for key in history:
        if key.startswith("team:"):
            tname = key.replace("team:", "")
            entries = len(history[key])
            print(f"  - {tname}: {entries} history entries")

    print(f"\n✓ Start dashboard: python dashboard.py")
    print(f"✓ Visit http://localhost:5000")

def create_test_history():
    now = datetime.now()
    msgs = get_status_messages()
    configs = get_agents_config()
    agents, history = build_agents(configs, now, msgs)
    build_team_histories(agents, history)

    data = {"agents": agents, "history": history}

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print_summary(agents, history)

if __name__ == "__main__":
    print("Creating test data with history...\n")
    create_test_history()
