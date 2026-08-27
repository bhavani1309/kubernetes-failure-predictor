# === app/core/escalation.py ===
import yaml
import os

ESCALATION_FILE = "config/escalation.yaml"


def load_escalation_rules():
    if not os.path.exists(ESCALATION_FILE):
        return {}
    with open(ESCALATION_FILE, "r") as f:
        return yaml.safe_load(f)


def get_escalation_steps(issue_type):
    try:
        with open(ESCALATION_FILE, "r") as f:
            esc = yaml.safe_load(f)
            for rule in esc:
                if rule.get("issue", "").lower() == issue_type.lower():
                    return rule.get("steps", [])
    except Exception as e:
        print(f"⚠️ Failed to load escalation.yaml: {e}")
    return []
