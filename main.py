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
from worker import process_file
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
    stepping_back: Optional[str] = Form(None)
):
    # Just for testing, print the incoming data
    print(f"execution_id={execution_id}")
    print(f"user_id={user_id}, user_name={user_name}")
    print(f"file name={file.filename}")
    print(f"stepping_back={stepping_back}")

    # Save uploaded file
    saved_path = await save_file_locally(execution_id, file)

    # Start background processing
    background_tasks.add_task(
        process_file, execution_id, saved_path, user_id, user_name, stepping_back
    )

    return {"message": "File received. Processing started.", "execution_id": execution_id}

@app.get("/status/{execution_id}")
def check_status(execution_id: str):
    return get_status(execution_id)