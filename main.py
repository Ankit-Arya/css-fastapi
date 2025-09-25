import json
import signal
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, Depends, UploadFile
from models.request_models import UserSignUp, UserLogin, TokenResponse
from services.auth_service import register_user, authenticate_user, create_access_token
from pymongo.mongo_client import MongoClient
import certifi
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
from helpers import save_file_locally, update_status, get_status
from worker import process_file, job_registry  
import os

uri = "mongodb+srv://greenthornarya676_db_user:NRhQ0lSyJBMjyD5I@ankit-css.fz6hv8r.mongodb.net/?retryWrites=true&w=majority&appName=ANKIT-CSS"

client = MongoClient(uri, tlsCAFile=certifi.where())
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client["user_auth_db"]
users_collection = db["users"]

app = FastAPI()

# Ensure temp_files directory exists
os.makedirs("temp_files", exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup")
def signup(user: UserSignUp):
    success = register_user(user, users_collection)
    if not success:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return {"message": "Sign up successful."}

@app.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    if not authenticate_user(user.email, user.password, users_collection):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/lines")
def get_dmrc_lines():
    return {
        "lines": [
            "Red Line",
            "Yellow Line",
            "Blue Line",
            "Green Line",
            "Violet Line",
            "Orange Line (Airport Express)",
            "Pink Line",
            "Magenta Line",
            "Grey Line",
            "Aqua Line (Noida Metro)"
        ]
    }

@app.post("/simulate")
async def simulate(
    background_tasks: BackgroundTasks,
    execution_id: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Form(""),
    user_name: str = Form(""),
    email: str = Form(""),
    stepping_back: Optional[str] = Form(None)
):
    # Just for testing, print the incoming data
    print(f"execution_id={execution_id}")
    print(f"user_id={user_id}, user_name={user_name}, email={email}")
    print(f"file name={file.filename}")
    print(f"stepping_back={stepping_back}")

    # ✅ Parse stepping_back JSON if provided
    parsed_stepping_back = []
    if stepping_back:
        try:
            parsed_stepping_back = json.loads(stepping_back)
        except Exception as e:
            print("Failed to parse stepping_back JSON:", e)
            
    # Save uploaded file
    saved_path = await save_file_locally(execution_id, file)

    # Start background processing
    background_tasks.add_task(
        process_file, execution_id, saved_path, user_id, user_name,email, parsed_stepping_back
    )

    return {"message": "File received. Processing started.", "execution_id": execution_id}

@app.get("/status/{execution_id}")
def check_status(execution_id: str):
    return get_status(execution_id)

@app.get("/download/{execution_id}")
def download_file(execution_id: str):
    # Always resolve to absolute path from this script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "temp_files", f"trip_chart_{execution_id}.xlsx")

    print("📁 Trying to serve file at:", file_path)

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return FileResponse(
            path=file_path,
            filename=f"trip_chart_{execution_id}.xlsx",
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    raise HTTPException(status_code=404, detail="File not ready or corrupted")

@app.delete("/cancel/{execution_id}")
def cancel_simulation(execution_id: str):
    job = job_registry.get(execution_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="No running job found for this execution ID."
        )

    process = job.get("process")
    if process is None:
        raise HTTPException(
            status_code=400,
            detail="Process info missing."
        )

    try:
        os.kill(process.pid, signal.SIGTERM)

        # ✅ Correct update_status usage
        update_status(
            execution_id,
            "Process Cancelled",   # step_name
            "cancelled",           # status
            "User requested cancellation"  # message (optional)
        )

        job["status"] = "cancelled"
        return {"status": "cancelled", "message": "Simulation cancelled."}

    except Exception as e:
        update_status(
            execution_id,
            "Cancel Failed",
            "error",
            str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to cancel process: {e}")