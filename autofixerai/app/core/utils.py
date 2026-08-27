# app/core/utils.py

import requests
import json
import re
import time 
import subprocess
from datetime import datetime

SAFE_COMMANDS = [
    "kubectl delete pod",
    "kubectl rollout restart",
    "kubectl set image",
    "kubectl describe",
    "kubectl logs",
    "kubectl get",
    "kubectl create secret",
    "docker login"
]



import re
import os
import json

STATUS_FILE = "agent_status.json"

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {"running": True, "simulate": False}
def collect_pod_logs(state: dict):
    """
    Node: Collect pod logs, store in state.
    """
    pods = subprocess.run(
        ["kubectl", "get", "pods", "--no-headers", "-o", "custom-columns=:metadata.name"],
        capture_output=True, text=True
    ).stdout.splitlines()

    entries = []
    for pod in pods:
        pod = pod.strip()
        if not pod:
            continue

        curr = subprocess.run(
            ["kubectl", "logs", pod, "--all-containers", "--tail=200"],
            capture_output=True, text=True
        )
        snippet = curr.stdout or curr.stderr or ""

        prev = ""
        if "CrashLoopBackOff" in snippet or curr.returncode != 0:
            prev = subprocess.run(
                ["kubectl", "logs", pod, "--all-containers", "--previous", "--tail=200"],
                capture_output=True, text=True
            ).stdout or ""

        full = snippet + ("\n\n[previous logs]\n" + prev if prev else "")
        if full.strip():
            entries.append(f"=== {pod} ===\n{full}")

    logs = "\n\n".join(entries)
    print("🔧 [debug] collected logs preview:\n", logs[:500], "\n---")

    state.logs = logs
    return state  # ✅ IMPORTANT: return updated state

def collect_pod_logs_node(state):
    return collect_pod_logs(state)

FIX_HISTORY_FILE = "history/fix_history.json"

def save_fix_history(pod_name, command, source):
    os.makedirs("history", exist_ok=True)

    if os.path.exists(FIX_HISTORY_FILE):
        with open(FIX_HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    entry = {
        "timestamp": datetime.now().isoformat(),
        "pod": pod_name,
        "command": command,
        "source": source
    }
    history.append(entry)

    with open(FIX_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def validate_kubectl_command(cmd):
    allowed_prefixes = [
        "kubectl get", "kubectl describe", "kubectl delete", "kubectl logs",
        "kubectl rollout", "kubectl set", "kubectl edit", "kubectl top",
        "kubectl create", "kubectl autoscale"
    ]
    # Normalize command for comparison
    cmd = cmd.strip().lower()

    # Check if command starts with an allowed kubectl verb
    if any(cmd.startswith(prefix) for prefix in allowed_prefixes):
        # Optional: basic regex to block obviously wrong commands
        forbidden_patterns = [
            r"rm -rf", r":\(", r"shutdown", r"format c:", r"\bDROP\b", r"\bDELETE FROM\b",
            r"--fields", r"--cpu-percent=\d+ --min=\d+ --max=\d+"    # <-- previously caused issues
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, cmd, re.IGNORECASE):
                return False, f"Forbidden pattern detected: {pattern}"
        return True, "Safe"
    else:
        return False, "Not a recognized kubectl command"



def query_llm(issue_type, prompt, retries=3, delay=5, model = "codellama:7b-instruct"):
    """
    Query the LLM (Ollama/codellama:7b-instruct) and retry on failure.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=500)
            response.raise_for_status()  # Raise error for non-2xx codes
            result = response.json().get("response") or response.json().get("generated_text")
            if not result or not result.strip():
                raise ValueError("LLM returned empty response.")
            return result

        except Exception as e:
            print(f"⚠️ LLM request failed (Attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                print(f"🔁 Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ LLM unavailable after multiple attempts. Using fallback fix.")
                return json.dumps({
                    "name": "UnknownIssue",
                    "fix": "echo Not fixed",
                    "explanation": "LLM not available. Fallback fix used."
                })


def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("No valid JSON in response: " + text)
    except Exception as e:
        raise Exception(f"JSON parsing failed: {e}")

def generate_explanation(issue_type, log_snippet, fix_command):
    return f"Issue type '{issue_type}' detected. Applied fix: '{fix_command}'. Log snippet: {log_snippet[:150]}..."
