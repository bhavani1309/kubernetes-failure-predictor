import os
import time
import subprocess
from app.core.log_parser import parse_logs
from app.core.fixer import diagnose_and_fix
import json
from datetime import datetime

STATUS_FILE = "agent_status.json"
LOG_FILE = "app/data/k8s_logs.txt"
RETRY_INTERVAL = 10
FIX_HISTORY_FILE = "history/fix_history.json"

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {"running": True, "simulate": False}

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

def collect_pod_logs():
    """
    List all pods, fetch their current and previous logs (for CrashLoopBackOff),
    and return a combined text blob for parsing.
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

        # 1) current logs
        curr = subprocess.run(
            ["kubectl", "logs", pod, "--all-containers", "--tail=200"],
            capture_output=True, text=True
        )
        snippet = curr.stdout or curr.stderr or ""

        # 2) if pod is crashing, fetch previous logs too
        prev = ""
        if "CrashLoopBackOff" in snippet or curr.returncode != 0:
            prev = subprocess.run(
                ["kubectl", "logs", pod, "--all-containers", "--previous", "--tail=200"],
                capture_output=True, text=True
            ).stdout or ""

        full = snippet + ("\n\n[previous logs]\n" + prev if prev else "")
        if full.strip():
            entries.append(f"=== {pod} ===\n{full}")

    # debug preview
    preview = "\n".join(entries)[:500]
    print("🔧 [debug] collected logs preview:\n", preview, "\n---")
    return "\n\n".join(entries)

def main():
    print("🔁 AutoFixerAI Agent started.")
    while True:
        status = load_status()
        if not status["running"]:
            print("⏸️ Agent paused.")
            time.sleep(RETRY_INTERVAL)
            continue

        log_data = collect_pod_logs()
        issues = parse_logs(log_data)

        if issues:
            print(f"⚠️ Issues found: {len(issues)}")
            if status.get("simulate"):
                for issue in issues:
                    print("💡 Simulate:", issue["name"], "on pod", issue["pod_name"])
            else:
                results = diagnose_and_fix(issues)
                for r in results:
                    print(f"✅ Fixed issue in pod {r['pod']}\n🧠 Explanation: {r['explanation']}\n")
                    save_fix_history(r['pod'], r['command'], r.get('source', 'unknown') )
        else:
            print("✅ No issues detected.")

        time.sleep(RETRY_INTERVAL)

if __name__ == "__main__":
    main()
