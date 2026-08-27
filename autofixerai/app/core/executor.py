import subprocess

def validate_kubectl_command(command: str) -> bool:
    if not command.strip().startswith("kubectl"):
        return False
    try:
        dry_run_cmd = f"{command} --dry-run=client"
        result = subprocess.run(dry_run_cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def run_fix_command(command: str, simulate: bool = True) -> str:
    if simulate:
        return f"(Simulated) Would run: {command}"

    if not validate_kubectl_command(command):
        return f"❌ Unsafe or invalid command: {command}"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"✅ Command executed:{result.stdout}"
        else:
            return f"❌ Command failed:{result.stderr}"
    except Exception as e:
        return f"⚠️ Exception occurred: {str(e)}"
