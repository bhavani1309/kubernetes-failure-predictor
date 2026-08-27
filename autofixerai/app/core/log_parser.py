import json
import yaml
import re
import os
from app.core.utils import query_llm



BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RULES_FILE = os.path.join(BASE_DIR, 'config', 'rules.yaml')

def parse_logs(log_data, rules=None, llm=None):
    import re
    import yaml
      # adjust if needed

    print("🛠 [debug] raw log_data:")
    print(log_data)

    # If rules not passed, load them:
    if rules is None:
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                rules = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading rules.yaml: {e}")
            return [], []

    print(f"🛠 [debug] using {len(rules)} rules:")
    for r in rules:
        print(f"  • {r['name']!r} → pattern: {r['pattern']}")

    issues = []
    results = []

    for pod_log in log_data.split("=== "):
        pod_log = pod_log.strip()
        if not pod_log:
            continue

        header, *lines = pod_log.splitlines()
        pod_name = header.strip()
        content = "\n".join(lines)
        print(f"\n🛠 [debug] inspecting pod: {pod_name!r}")
        print(content)

        matched = False
        for rule in rules:
            if re.search(rule["pattern"], content, re.IGNORECASE):
                print(f"✅ [debug] rule `{rule['name']}` matched!")
                issues.append({
                    "pod_name": pod_name,
                    "name": rule["name"],
                    "fix": rule["fix"],
                    "snippet": content[:200]
                })
                matched = True
                break

        if not matched:
            if any(term in content.lower() for term in ["error", "fail", "crash", "back-off", "badrequest"]):
                print(f"⚠️ [debug] no rule matched for pod {pod_name!r}, marking for LLM fallback")
                issues.append({
                    "pod_name": pod_name,
                    "name": "UnknownIssue",
                    "fix": None,
                    "snippet": content[:200],
                    "source": "LLM"
                })
            else:
                print(f"✅ [debug] skipping pod {pod_name!r} – no match and no error/crash detected")

    return issues
