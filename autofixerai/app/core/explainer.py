import requests

def generate_explanation(issue_type, log_snippet, command, model="mistral"):
    prompt = f"""
You are a DevOps expert AI agent.

A system log showed this issue:
{log_snippet}

Issue type: {issue_type}

You chose to fix it with the command:
{command}

Explain in simple terms why this command was used to resolve the issue.
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=500
        )
        data = response.json()
        return data.get("response", "⚠️ No response from LLM")
    except Exception as e:
        return f"❌ LLM Error: {e}"
