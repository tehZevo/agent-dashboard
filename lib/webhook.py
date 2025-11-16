import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from lib.data_io import load_data

executor = ThreadPoolExecutor(max_workers=5)

def deliver(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=10, headers={"Content-Type": "application/json"})
        response.raise_for_status()
    except Exception as e:
        print(f"Webhook delivery failed for {url}: {str(e)}")

def trigger(event_type, data):
    agent_data = load_data()
    webhooks = agent_data.get("webhooks", [])
    if not webhooks:
        return

    payload = {"event": event_type, "timestamp": datetime.now().isoformat(), "data": data}

    for webhook in webhooks:
        url = webhook.get("url")
        events = webhook.get("events", ["all"])
        if "all" in events or event_type in events:
            executor.submit(deliver, url, payload)
