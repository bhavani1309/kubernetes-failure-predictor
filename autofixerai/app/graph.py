import json
import os

import yaml
from pydantic import BaseModel  # ✅ import Pydantic for state
from app.core.log_parser import parse_logs

from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM  # ✅ updated new import

# === Setup paths ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
rules_path = os.path.join(BASE_DIR, 'config', 'rules.yaml')
logs_path = os.path.join(BASE_DIR, 'app', 'data', 'k8s_logs.txt')

with open(rules_path, 'r', encoding='utf-8') as f:
    rules = yaml.safe_load(f)

print("✅ Loaded rules:", rules)

# === 2. Setup LLM
llm = OllamaLLM(model="codellama:7b-instruct")

# === 3. Define Pydantic state model ✅✅
class GraphState(BaseModel):
    logs: str
    issues: list
    results: list

# === 4. Collect logs
def collect_logs(_):
    with open(logs_path, "r") as f:
        logs = f.read()
    return {"logs": logs}

# === 5. Diagnose + fix
def diagnose_and_fix(data):
    logs = data.logs

    issues = parse_logs(logs, rules, llm)
    return {"logs": logs, "issues": issues, "results": []}

# === 6. Save agent status + fix history
def save_agent_status(issues):
    with open("agent_status.json", "w") as f:
        json.dump({"issues": issues}, f, indent=2)

def save_fix_history(results):
    history_path = "history/fix_history.json"
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history = json.load(f)
    else:
        history = []
    history.extend(results)
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

def store_results(data):
    save_agent_status(data["issues"])
    save_fix_history(data["results"])
    return data

# === 7. Build graph
graph = StateGraph(GraphState)
graph.add_node("collect_logs", collect_logs)
graph.add_node("diagnose_and_fix", diagnose_and_fix)
graph.add_node("store_results", store_results)

graph.set_entry_point("collect_logs")
graph.add_edge("collect_logs", "diagnose_and_fix")
graph.add_edge("diagnose_and_fix", "store_results")
graph.add_edge("store_results", END)

app = graph.compile()

# === 8. Run once
if __name__ == "__main__":
    result = app.invoke({"logs": "", "issues": [], "results": []})

    print("✅ Graph output:", result)
