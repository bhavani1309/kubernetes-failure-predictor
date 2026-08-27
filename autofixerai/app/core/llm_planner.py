import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL = "codellama:7b-instruct"

VALID_PREFIXES = [
    "kubectl get", "kubectl describe", "kubectl logs",
    "kubectl rollout", "kubectl set", "kubectl delete",
    "kubectl restart", "kubectl top", "kubectl autoscale"
]

FORBIDDEN_FLAGS = [
    "--containers", "--cpu-percent", "--fields", "--context",
    "-c0", "-w", "--unknown"
]

INVALID_PATTERNS = [
    "<", ">", "{", "}", "[", "]", "fake", "nonsense", "invalid"
]

def is_safe_kubectl_command(command: str):
    cmd = command.strip().lower()
    if not cmd.startswith("kubectl "):
        return False
    if any(flag in cmd for flag in FORBIDDEN_FLAGS):
        return False
    if any(bad in cmd for bad in INVALID_PATTERNS):
        return False
    if not any(cmd.startswith(prefix) for prefix in VALID_PREFIXES):
        return False
    return True

def query_llm(prompt, max_tokens=500, temp=0.3):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": temp,
        "max_tokens": max_tokens
    }
    try:
        res = requests.post(OLLAMA_API_URL, json=payload, timeout=500)
        res.raise_for_status()
        data = res.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"⚠️ LLM request failed: {e}")
        return None

def plan_fixes_with_llm(pod_name, issue_name, logs):
    prompt = f"""
You are a Kubernetes SRE.
Pod: '{pod_name}' is failing with: '{issue_name}'.
Logs:
{logs}

TASK:
Suggest 1–2 *real* safe `kubectl` commands to diagnose/fix.
- Only official k8s commands.
- DO NOT output any non-command text.
- If you cannot provide valid kubectl: COMMAND 1: NO_VALID_COMMAND

Format exactly:
COMMAND 1: <command>
REASON 1: <reason>
"""
    response = query_llm(prompt)
    if not response:
        return []

    print(f"\n🧠 Raw LLM response:\n{response}")
    steps = []
    cmd, reason = None, None

    for line in response.splitlines():
        if line.strip().lower().startswith("command"):
            cmd = line.split(":", 1)[-1].strip().strip("`")
        elif line.strip().lower().startswith("reason"):
            reason = line.split(":", 1)[-1].strip()

        if cmd and reason:
            if cmd == "NO_VALID_COMMAND":
                cmd, reason = None, None
                continue
            if is_safe_kubectl_command(cmd):
                steps.append({"fix": cmd, "explanation": reason})
            else:
                print(f"❌ Discarded invalid LLM command: {cmd}")
            cmd, reason = None, None

    return steps
