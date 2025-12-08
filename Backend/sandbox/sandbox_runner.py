import subprocess
import tempfile
import os
import uuid

def run_in_sandbox(code: str, stdin: str):
    file_id = str(uuid.uuid4())
    tmp_dir = tempfile.gettempdir()          # <-- works on Windows/Linux/Mac
    filepath = os.path.join(tmp_dir, f"{file_id}.py")

    with open(filepath, "w") as f:
        f.write(code)

    try:
        proc = subprocess.run(
            ["python", filepath],            # <-- use python instead of python3 on Windows
            input=stdin.encode(),
            capture_output=True,
            timeout=2
        )
        return {
            "stdout": proc.stdout.decode(),
            "stderr": proc.stderr.decode(),
            "exit_code": proc.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Timeout: infinite loop detected"}
    except Exception as e:
        return {"error": str(e)}
