import subprocess
import os
import json
import sys
from helpers import update_status

job_registry = {}  # 🔁 execution_id -> { process, status }

def process_file(
    execution_id: str, 
    file_path: str, 
    user_id: str, 
    user_name: str, 
    email: str,
    stepping_back: list
):
    try:
        update_status(execution_id, "Preparing simulation", "WIP")

        # ✅ Always use absolute paths
        file_path = os.path.abspath(file_path)
        script_path = os.path.abspath("simulate_runner.py")

        print(f"🔧 [SIMULATION] Running: {script_path}")
        print(f"📄 File path: {file_path}")
        print(f"🧾 Stepping back: {stepping_back}")

        # Escape JSON properly
        stepping_back_json = json.dumps(stepping_back)
        print(f"🧩 Starting subprocess: {sys.executable} {script_path} {execution_id} {file_path} {stepping_back_json}")

        # Wrap JSON in quotes to prevent it from breaking as CLI arg
        process = subprocess.Popen(
            [sys.executable, script_path, execution_id, file_path, stepping_back_json],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Register for cancellation
        job_registry[execution_id] = {
            "process": process,
            "status": "running"
        }

        # Wait for completion
        stdout, stderr = process.communicate()
        print("✅ STDOUT:\n", stdout.decode())
        print("⚠️ STDERR:\n", stderr.decode())

        if process.returncode == 0:
            job_registry[execution_id]["status"] = "completed"
            update_status(execution_id, "Simulation completed successfully", "completed")
        else:
            job_registry[execution_id]["status"] = "error"
            update_status(execution_id, stderr.decode(), "error")

    except Exception as e:
        print("❌ Error in subprocess execution:", e)
        update_status(execution_id, str(e), "error")
        job_registry[execution_id] = {
            "process": None,
            "status": "error"
        }
