import json
import os
from datetime import datetime

HISTORY_FILE = "autofixer_history.json"

def save_fix_event(event):
    event["timestamp"] = event.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    event["fix_source"] = event.get("fix_source", "N/A")
    event["success"] = event.get("success", False)

    data = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)

    data.append(event)

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)