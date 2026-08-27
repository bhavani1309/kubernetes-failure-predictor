# app/core/learning.py

import os
import json
from datetime import datetime

LEARNING_LOG = "app/data/learning_log.json"
RECENT_FAILURES = "app/data/recent_failures.json"

def _load(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def update_stats(issue_type: str, success: bool):
    """
    Track total / successful fixes per issue_type.
    """
    stats = _load(LEARNING_LOG)
    entry = stats.get(issue_type, {"total": 0, "success": 0})
    entry["total"] += 1
    if success:
        entry["success"] += 1
    stats[issue_type] = entry
    _save(LEARNING_LOG, stats)

def has_recent_failure(pod: str, issue_type: str, window: int = 3600):
    """
    Prevent retrying the same fix on the same pod within the last `window` seconds.
    """
    rec = _load(RECENT_FAILURES)
    key = f"{pod}:{issue_type}"
    last = rec.get(key)
    if last and (datetime.now().timestamp() - last) < window:
        return True
    return False

def log_learning_event(pod: str, issue_type: str, fix_command: str, success: bool, source: str):
    """
    Record that we tried this fix on this pod.
    If it failed, mark the timestamp so we don't spam it again.
    """
    rec = _load(RECENT_FAILURES)
    key = f"{pod}:{issue_type}"
    if not success:
        rec[key] = datetime.now().timestamp()
    else:
        rec.pop(key, None)
    _save(RECENT_FAILURES, rec)

def log_fix_attempt(issue_type: str, command: str, success: bool):
    """
    Just an alias to `update_stats` + `log_learning_event` if needed elsewhere.
    """
    # We already capture stats; you can hook additional analytics here.
    pass
