import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config")
RULES_PATH = os.path.join(CONFIG_PATH, "rules.yaml")
ESCALATION_PATH = os.path.join(CONFIG_PATH, "escalation.yaml")

print("📂 Current Working Directory:", os.getcwd())
print("📂 ROOT_DIR:", ROOT_DIR)
print("📂 CONFIG_PATH:", CONFIG_PATH)
print("📄 RULES_PATH:", RULES_PATH, " | Exists:", os.path.exists(RULES_PATH))
print("📄 ESCALATION_PATH:", ESCALATION_PATH, " | Exists:", os.path.exists(ESCALATION_PATH))

with open(RULES_PATH, "r") as f:
    print("✅ Opened rules.yaml successfully")
