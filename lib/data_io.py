from pathlib import Path
import json

DATA_FILE = Path(__file__).parent.parent / "agent_data.json"

def load_data():
    if not DATA_FILE.exists():
        return create_empty()
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            ensure_keys(data)
            return data
    except (json.JSONDecodeError, IOError):
        return create_empty()

def create_empty():
    return {"agents": {}, "history": {}, "webhooks": []}

def ensure_keys(data):
    if "webhooks" not in data:
        data["webhooks"] = []
    if "history" not in data:
        data["history"] = {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
