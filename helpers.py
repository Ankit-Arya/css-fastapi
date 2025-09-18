import os
import json
from fastapi import UploadFile
import shutil

STATUS_FILE = "status_store.json"

async def save_file_locally(execution_id: str, file: UploadFile) -> str:
    path = f"temp_files/{execution_id}_{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path


def update_status(execution_id: str, step_name: str, status: str, message: str = ""):
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            statuses = json.load(f)
    else:
        statuses = {}

    steps = statuses.get(execution_id, [])

    # Remove any existing step with same name
    steps = [step for step in steps if step["name"] != step_name]

    # Add updated step
    steps.append({
        "name": step_name,
        "status": status,
        "message": message
    })

    statuses[execution_id] = steps

    with open(STATUS_FILE, "w") as f:
        json.dump(statuses, f, indent=2)


def get_status(execution_id: str) -> dict:
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            statuses = json.load(f)
            return {"steps": statuses.get(execution_id, [])}
    return {"steps": []}
