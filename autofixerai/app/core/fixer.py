import os
import json
import yaml
from app.core.explainer import generate_explanation
from app.core.executor import run_fix_command
from app.core.history import save_fix_event
from app.core.llm_planner import plan_fixes_with_llm  # ✅ use the new chain
from app.core.learning import update_stats, has_recent_failure, log_learning_event
from app.core.utils import validate_kubectl_command


# get ROOT_DIR robustly
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CONFIG_PATH = os.path.join(ROOT_DIR, "config")
RULES_PATH = os.path.join(CONFIG_PATH, "rules.yaml")
ESCALATION_PATH = os.path.join(CONFIG_PATH, "escalation.yaml")

print(f"🔍 Using RULES_PATH: {RULES_PATH} | Exists: {os.path.exists(RULES_PATH)}")



def load_yaml(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

def get_rule_based_fix(issue_type):
    rules = load_yaml(RULES_PATH)
    for rule in rules:
        if rule["name"].lower() == issue_type.lower():
            return rule.get("fix"), "Rule"
    return None, None

def get_escalation_steps(issue_type):
    try:
        with open(ESCALATION_PATH, "r") as f:
            esc_data = yaml.safe_load(f)
        if isinstance(esc_data, list):
            esc_data = {step['issue'].lower(): step['steps'] for step in esc_data if 'issue' in step and 'steps' in step}
        return esc_data.get(issue_type.lower(), [])
    except Exception as e:
        print(f"⚠️ Error loading escalation steps: {e}")
        return []

def is_valid_kubectl_command(command):
    from app.core.utils import validate_kubectl_command
    valid, _ = validate_kubectl_command(command)
    return valid

def is_pod_healthy(pod_name):
    try:
        from subprocess import run
        result = run(["kubectl", "get", "pod", pod_name, "-o", "json"], capture_output=True, text=True, check=True)
        pod_info = json.loads(result.stdout)
        return pod_info["status"].get("phase") == "Running"
    except Exception:
        return False

def diagnose_and_fix(issues):
    results = []
    simulate = False

    if os.path.exists("agent_status.json"):
        try:
            with open("agent_status.json", "r") as f:
                config = json.load(f)
                simulate = config.get("simulate", False)
        except:
            simulate = False

    for issue in issues:
        pod_name = issue.get("pod_name")
        log_snippet = issue.get("snippet")
        issue_type = issue.get("name")

        if has_recent_failure(pod_name, issue_type):
            print(f"⚠️ Skipping {pod_name} - recently failed.")
            continue

        success = False
        fix_command, fix_source, output = None, None, ""

        # 1️⃣ Rules
        fix_command, fix_source = get_rule_based_fix(issue_type)
        if fix_command:
            fix_command = fix_command.replace("{pod}", pod_name).replace("{deployment}", pod_name)
            if is_valid_kubectl_command(fix_command):
                output = run_fix_command(fix_command, simulate)
                success = is_pod_healthy(pod_name)
                log_learning_event(pod=pod_name, issue_type=issue_type, fix_command=fix_command, success=success, source=fix_source)

        # 2️⃣ Escalation
        if not success:
            for step in get_escalation_steps(issue_type):
                fix_command = step.get("fix")
                condition = step.get("condition", "Escalation")
                if not fix_command:
                    continue
                fix_command = fix_command.replace("{pod}", pod_name).replace("{deployment}", pod_name)
                if is_valid_kubectl_command(fix_command):
                    print(f"🚨 Escalation: {fix_command} | Reason: {condition}")
                    output = run_fix_command(fix_command, simulate)
                    success = is_pod_healthy(pod_name)
                    log_learning_event(pod=pod_name, issue_type=issue_type, fix_command=fix_command, success=success, source=f"Escalation: {condition}")
                    if success:
                        fix_source = f"Escalation: {condition}"
                        break

        # 3️⃣ LLM fallback chain
        if not success:
            steps = plan_fixes_with_llm(pod_name, issue_type, log_snippet)
            for s in steps:
                cmd = s["fix"]
                reason = s["explanation"]
                if not is_valid_kubectl_command(cmd):
                    print(f"❌ Unsafe LLM fallback: {cmd}")
                    continue
                output = run_fix_command(cmd, simulate)
                success = is_pod_healthy(pod_name)
                fix_command = cmd
                fix_source = "LLM Fallback"
                log_learning_event(pod=pod_name, issue_type=issue_type, fix_command=cmd, success=success, source=fix_source)
                if success:
                    break
            if not steps:
                fix_command = "echo 'No valid LLM command'"
                fix_source = "LLM fallback failed"

        explanation = generate_explanation(issue_type, log_snippet, fix_command)
        save_fix_event({
            "issue": issue_type,
            "pod": pod_name,
            "fix_command": fix_command,
            "log_snippet": log_snippet,
            "explanation": explanation,
            "output": output,
            "fix_source": fix_source,
            "success": success
        })

        update_stats(issue_type, success)
        results.append({
            "pod": pod_name,
            "issue": issue_type,
            "command": fix_command,
            "explanation": explanation,
            "output": output,
            "fix_source": fix_source,
            "success": success
        })

    return results
