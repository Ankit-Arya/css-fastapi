import subprocess
import os
import json
import sys
from helpers import update_status

# job_registry = {}  # 🔁 execution_id -> { process, status }

# def process_file(
#     execution_id: str, 
#     file_path: str, 
#     user_id: str, 
#     user_name: str, 
#     email: str,
#     stepping_back: list
# ):
#     try:
#         update_status(execution_id, "Preparing simulation", "WIP")

#         # ✅ Always use absolute paths
#         file_path = os.path.abspath(file_path)
#         script_path = os.path.abspath("simulate_runner.py")

#         print(f"🔧 [SIMULATION] Running: {script_path}")
#         print(f"📄 File path: {file_path}")
#         print(f"🧾 Stepping back: {stepping_back}")

#         # Escape JSON properly
#         stepping_back_json = json.dumps(stepping_back)
#         print(f"🧩 Starting subprocess: {sys.executable} {script_path} {execution_id} {file_path} {stepping_back_json}")

#         # Wrap JSON in quotes to prevent it from breaking as CLI arg
#         process = subprocess.Popen(
#             [sys.executable, script_path, execution_id, file_path, stepping_back_json],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )

#         # Register for cancellation
#         job_registry[execution_id] = {
#             "process": process,
#             "status": "running"
#         }

#         # Wait for completion
#         stdout, stderr = process.communicate()
#         print("✅ STDOUT:\n", stdout.decode())
#         print("⚠️ STDERR:\n", stderr.decode())

#         if process.returncode == 0:
#             job_registry[execution_id]["status"] = "completed"
#             update_status(execution_id, "Simulation completed successfully", "completed")
#         else:
#             job_registry[execution_id]["status"] = "error"
#             update_status(execution_id, stderr.decode(), "error")

#     except Exception as e:
#         print("❌ Error in subprocess execution:", e)
#         update_status(execution_id, str(e), "error")
#         job_registry[execution_id] = {
#             "process": None,
#             "status": "error"
#         }
import threading
import subprocess
import sys
import os
import json
from typing import List

job_registry = {}  # execution_id -> { "process": Popen, "status": str }

def _monitor_process_lines(execution_id, process):
    try:
        for line in process.stdout:
            if not line:
                break
            print(f"[child stdout] {line.rstrip()}")
            # ❌ Do not call update_status here

        for line in process.stderr:
            if not line:
                break
            print(f"[child stderr] {line.rstrip()}")
            # ❌ Do not call update_status here

        process.wait()
        if process.returncode == 0:
            job_registry[execution_id]["status"] = "completed"
        else:
            job_registry[execution_id]["status"] = "error"

    except Exception as e:
        print("Monitor thread error:", e)
        job_registry[execution_id] = {"process": None, "status": "error"}

def process_file(execution_id: str, file_path: str, user_id: str, user_name: str, email: str, stepping_back: List, timetable_type: str):
    try:
        update_status(execution_id, "Preparing simulation", "WIP")
        file_path = os.path.abspath(file_path)
        script_path = os.path.abspath("simulate_runner.py")
        stepping_back_json = json.dumps(stepping_back)

        # Start subprocess with unbuffered output; text mode for easy line reads
        process = subprocess.Popen(
            [sys.executable, "-u", script_path, execution_id, file_path, stepping_back_json, timetable_type],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            text=True
        )

        job_registry[execution_id] = {"process": process, "status": "running"}

        # Start monitor thread and return immediately (so FastAPI background task completes)
        monitor_thread = threading.Thread(target=_monitor_process_lines, args=(execution_id, process), daemon=True)
        monitor_thread.start()

    except Exception as e:
        print("❌ Error in subprocess launch:", e)
        update_status(execution_id, str(e), "error")
        job_registry[execution_id] = {"process": None, "status": "error"}

def process_fileL34(execution_id: str, file_path: str, user_id: str, user_name: str, email: str, stepping_back: List, timetable_type: str):
    try:
        update_status(execution_id, "Preparing simulation", "WIP")
        file_path = os.path.abspath(file_path)
        script_path = os.path.abspath("simulate_runnerL34.py")
        stepping_back_json = json.dumps(stepping_back)

        # Start subprocess with unbuffered output; text mode for easy line reads
        process = subprocess.Popen(
            [sys.executable, "-u", script_path, execution_id, file_path, stepping_back_json, timetable_type],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            text=True
        )

        job_registry[execution_id] = {"process": process, "status": "running"}

        # Start monitor thread and return immediately (so FastAPI background task completes)
        monitor_thread = threading.Thread(target=_monitor_process_lines, args=(execution_id, process), daemon=True)
        monitor_thread.start()

    except Exception as e:
        print("❌ Error in subprocess launch:", e)
        update_status(execution_id, str(e), "error")
        job_registry[execution_id] = {"process": None, "status": "error"}

def process_fileL5(execution_id: str, file_path: str, user_id: str, user_name: str, email: str, stepping_back: List, timetable_type: str):
    try:
        update_status(execution_id, "Preparing simulation", "WIP")
        file_path = os.path.abspath(file_path)
        script_path = os.path.abspath("simulate_runnerL5.py")
        stepping_back_json = json.dumps(stepping_back)

        # Start subprocess with unbuffered output; text mode for easy line reads
        process = subprocess.Popen(
            [sys.executable, "-u", script_path, execution_id, file_path, stepping_back_json, timetable_type],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            text=True
        )

        job_registry[execution_id] = {"process": process, "status": "running"}

        # Start monitor thread and return immediately (so FastAPI background task completes)
        monitor_thread = threading.Thread(target=_monitor_process_lines, args=(execution_id, process), daemon=True)
        monitor_thread.start()

    except Exception as e:
        print("❌ Error in subprocess launch:", e)
        update_status(execution_id, str(e), "error")
        job_registry[execution_id] = {"process": None, "status": "error"}