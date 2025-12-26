from datetime import datetime
import json
import signal
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, Depends, UploadFile
from models.request_models import UserSignUp, UserLogin, TokenResponse
from services.auth_service import register_user, authenticate_user, create_access_token
from pymongo.mongo_client import MongoClient
import certifi
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
from helpers import save_file_locally, update_status, get_status
from worker import process_file, job_registry, process_fileL34, process_fileL5  
import os
from fastapi.responses import StreamingResponse
from bson import ObjectId

# uri = "mongodb+srv://greenthornarya676_db_user:NRhQ0lSyJBMjyD5I@ankit-css.fz6hv8r.mongodb.net/?retryWrites=true&w=majority&appName=ANKIT-CSS"

# # ASYNC DB
# client = motor.motor_asyncio.AsyncIOMotorClient(uri)
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
# db = client["user_auth_db"]
# fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
# users_collection = db["users"]
# notices_collection = db["notices"]
# LOCAL MONGODB URI (Docker)

uri = "mongodb://localhost:27017"

# ASYNC DB CLIENT
client = motor.motor_asyncio.AsyncIOMotorClient(
    uri,
    tls=False
)

# DATABASE
db = client["user_auth_db"]

# COLLECTIONS
users_collection = db["users"]
notices_collection = db["notices"]

# GRIDFS
fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
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

# @app.post("/signup")
# def signup(user: UserSignUp):
#     success = register_user(user, users_collection)
#     if not success:
#         raise HTTPException(status_code=400, detail="Email already registered.")
#     return {"message": "Sign up successful."}

# @app.post("/login", response_model=TokenResponse)
# def login(user: UserLogin):
#     if not authenticate_user(user.email, user.password, users_collection):
#         raise HTTPException(status_code=401, detail="Incorrect email or password.")
#     token = create_access_token(user.email)
# #     return {"access_token": token, "token_type": "bearer"}
# @app.post("/signup")
# async def signup(user: UserSignUp):
#     success = await register_user(user, users_collection)  # Make register_user async
#     if not success:
#         raise HTTPException(status_code=400, detail="Email already registered.")
#     return {"message": "Sign up successful."}

# @app.post("/login", response_model=TokenResponse)
# async def login(user: UserLogin):
#     auth_success = await authenticate_user(user.email, user.password, users_collection)  # Make async
#     if not auth_success:
#         raise HTTPException(status_code=401, detail="Incorrect email or password.")
#     token = create_access_token(user.email)  # This can stay sync if it doesn't do async work
#     return {"access_token": token, "token_type": "bearer"}

# for frontend only auth

# ---------------- SIGNUP ----------------
@app.post("/signup")
async def signup(user: UserSignUp):
    success = await register_user(user, users_collection)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Email already registered or invalid domain."
        )

    return {"message": "Sign up successful."}


# ---------------- LOGIN ----------------
@app.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    auth_success = await authenticate_user(
        user.email,
        user.password,
        users_collection
    )

    if not auth_success:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password."
        )

    token = create_access_token(user.email)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


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
    user_email: str = Form(""),
    stepping_back: Optional[str] = Form(None),
    timetable_type: str = Form("large")  # 🆕 new field from frontend

):
    # Just for testing, print the incoming data
    print(f"execution_id={execution_id}")
    print(f"user_id={user_id}, user_name={user_name}, user_email={user_email}")
    print(f"file name={file.filename}")
    print(f"stepping_back={stepping_back}")
    print(f"timetable_type={timetable_type}")  # 🆕 log the new field

    # ✅ Parse stepping_back JSON if provided
    parsed_stepping_back = []
    if stepping_back:
        try:
            parsed_stepping_back = json.loads(stepping_back)
        except Exception as e:
            print("Failed to parse stepping_back JSON:", e)
    # Save uploaded file into MongoDB GridFS
    file_id = await fs.upload_from_stream(
        filename=file.filename,
        source=file.file,
        metadata={
            "uploaded_by": user_name or user_email or user_id or "Unknown",
            "execution_id": execution_id,
            "content_type": file.content_type,
            "timetable_type": timetable_type,  # 🆕 Save it as metadata too

        }
    )
    # ✅ Reset file pointer before reusing
    file.file.seek(0)
    # Determine initiatedBy using whichever field is available
    initiated_by = user_name or user_email or user_id or "Unknown"

    # Save notice entry in MongoDB
    notice = {
        "executionId": execution_id,
        "initiatedBy": initiated_by,
        "timestamp": datetime.now(),
        "file_id": str(file_id),
        "file_name": file.filename,
        "timetable_type": timetable_type
    }
    await notices_collection.insert_one(notice)
       
    # Save uploaded file
    saved_path = await save_file_locally(execution_id, file)

    # Start background processing
    background_tasks.add_task(
        process_file, execution_id, saved_path, user_id, user_name,user_email, parsed_stepping_back, timetable_type
    )

    return {"message": "File received. Processing started.", "execution_id": execution_id}

@app.post("/simulateL34")
async def simulateL34(
    background_tasks: BackgroundTasks,
    execution_id: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Form(""),
    user_name: str = Form(""),
    user_email: str = Form(""),
    stepping_back: Optional[str] = Form(None),
    timetable_type: str = Form("large")  # 🆕 new field from frontend

):
    # Just for testing, print the incoming data
    print(f"execution_id={execution_id}")
    print(f"user_id={user_id}, user_name={user_name}, user_email={user_email}")
    print(f"file name={file.filename}")
    print(f"stepping_back={stepping_back}")
    print(f"timetable_type={timetable_type}")  # 🆕 log the new field

    # ✅ Parse stepping_back JSON if provided
    parsed_stepping_back = []
    if stepping_back:
        try:
            parsed_stepping_back = json.loads(stepping_back)
        except Exception as e:
            print("Failed to parse stepping_back JSON:", e)
    # Save uploaded file into MongoDB GridFS
    file_id = await fs.upload_from_stream(
        filename=file.filename,
        source=file.file,
        metadata={
            "uploaded_by": user_name or user_email or user_id or "Unknown",
            "execution_id": execution_id,
            "content_type": file.content_type,
            "timetable_type": timetable_type,  # 🆕 Save it as metadata too

        }
    )
    # ✅ Reset file pointer before reusing
    file.file.seek(0)
    # Determine initiatedBy using whichever field is available
    initiated_by = user_name or user_email or user_id or "Unknown"

    # Save notice entry in MongoDB
    notice = {
        "executionId": execution_id,
        "initiatedBy": initiated_by,
        "timestamp": datetime.now(),
        "file_id": str(file_id),
        "file_name": file.filename,
        "timetable_type": timetable_type
    }
    await notices_collection.insert_one(notice)        
    # Save uploaded file
    saved_path = await save_file_locally(execution_id, file)

    # Start background processing
    background_tasks.add_task(
        process_fileL34, execution_id, saved_path, user_id, user_name,user_email, parsed_stepping_back,timetable_type  
    )

    return {"message": "File received. Processing started.", "execution_id": execution_id}


# @app.post("/simulateL5")
# async def simulateL5(
#     background_tasks: BackgroundTasks,
#     execution_id: str = Form(...),
#     file: UploadFile = File(...),
#     user_id: str = Form(""),
#     user_name: str = Form(""),
#     user_email: str = Form(""),
#     stepping_back: Optional[str] = Form(None),
#     timetable_type: str = Form("large")  # 🆕 new field from frontend

# ):
#     # Just for testing, print the incoming data
#     print(f"execution_id={execution_id}")
#     print(f"user_id={user_id}, user_name={user_name}, user_email={user_email}")
#     print(f"file name={file.filename}")
#     print(f"stepping_back={stepping_back}")
#     print(f"timetable_type={timetable_type}")  # 🆕 log the new field

#     # ✅ Parse stepping_back JSON if provided
#     parsed_stepping_back = []
#     if stepping_back:
#         try:
#             parsed_stepping_back = json.loads(stepping_back)
#         except Exception as e:
#             print("Failed to parse stepping_back JSON:", e)
#     # Save uploaded file into MongoDB GridFS
#     file_id = await fs.upload_from_stream(
#         filename=file.filename,
#         source=file.file,
#         metadata={
#             "uploaded_by": user_name or user_email or user_id or "Unknown",
#             "execution_id": execution_id,
#             "content_type": file.content_type,
#             "timetable_type": timetable_type,  # 🆕 Save it as metadata too

#         }
#     )
#     # ✅ Reset file pointer before reusing
#     file.file.seek(0)
#     # Determine initiatedBy using whichever field is available
#     initiated_by = user_name or user_email or user_id or "Unknown"

#     # Save notice entry in MongoDB
#     notice = {
#         "executionId": execution_id,
#         "initiatedBy": initiated_by,
#         "timestamp": datetime.now(),
#         "file_id": str(file_id),
#         "file_name": file.filename,
#         "timetable_type": timetable_type
#     }
#     await notices_collection.insert_one(notice)        
#     # Save uploaded file
#     saved_path = await save_file_locally(execution_id, file)

#     # Start background processing
#     background_tasks.add_task(
#         process_fileL5, execution_id, saved_path, user_id, user_name,user_email, parsed_stepping_back, timetable_type
#     )

#     return {"message": "File received. Processing started.", "execution_id": execution_id}

@app.post("/simulateL5")
async def simulateL5(
    background_tasks: BackgroundTasks,
    execution_id: str = Form(...),
    file: UploadFile = File(...),

    user_id: str = Form(""),
    user_name: str = Form(""),
    user_email: str = Form(""),

    stepping_back: Optional[str] = Form(None),
    timetable_type: str = Form("large"),

    # 🆕 NEW FIELDS
    duty_hours: str = Form(""),       # HH:MM
    running_hours: str = Form(""),    # HH:MM
    single_run_max: str = Form(""),   # HH:MM

    break_small: int = Form(0),       # minutes
    break_large: int = Form(0),       # minutes
):
    # --- Debug Logging ---
    print(f"execution_id={execution_id}")
    print(f"user_id={user_id}, user_name={user_name}, user_email={user_email}")
    print(f"file name={file.filename}")
    print(f"stepping_back={stepping_back}")
    print(f"timetable_type={timetable_type}")

    # 🆕 Print new fields
    print(f"duty_hours={duty_hours}")
    print(f"running_hours={running_hours}")
    print(f"single_run_max={single_run_max}")
    print(f"break_small={break_small}")
    print(f"break_large={break_large}")

    # --- Parse stepping_back JSON ---
    # parsed_stepping_back = []
    # if stepping_back:
    #     try:
    #         parsed_stepping_back = json.loads(stepping_back)
    #     except Exception as e:
    #         print("Failed to parse stepping_back JSON:", e)
    parsed_stepping_back = {}

    if stepping_back:
        try:
            parsed_stepping_back = json.loads(stepping_back)

            # Safety: ensure expected keys exist
            parsed_stepping_back.setdefault("SBC1", {})
            parsed_stepping_back.setdefault("SBC2", {})

        except Exception as e:
            print("Failed to parse stepping_back JSON:", e)
            parsed_stepping_back = {}

    # --- Save uploaded file to GridFS ---
    file_id = await fs.upload_from_stream(
        filename=file.filename,
        source=file.file,
        metadata={
            "uploaded_by": user_name or user_email or user_id or "Unknown",
            "execution_id": execution_id,
            "content_type": file.content_type,
            "timetable_type": timetable_type,

            # 🆕 Save new metadata
            # "duty_hours": duty_hours,
            # "running_hours": running_hours,
            "single_run_max": single_run_max,
            "break_small": break_small,
            "break_large": break_large,
        }
    )

    # Reset file pointer
    file.file.seek(0)

    initiated_by = user_name or user_email or user_id or "Unknown"

    # --- Save notice entry ---
    notice = {
        "executionId": execution_id,
        "initiatedBy": initiated_by,
        "timestamp": datetime.now(),
        "file_id": str(file_id),
        "file_name": file.filename,
        "timetable_type": timetable_type,

        # 🆕 Log new fields also
        # "duty_hours": duty_hours,
        # "running_hours": running_hours,
        "single_run_max": single_run_max,
        "break_small": break_small,
        "break_large": break_large,
    }
    await notices_collection.insert_one(notice)

    # Save file locally
    saved_path = await save_file_locally(execution_id, file)

    # --- Start background processing ---
    background_tasks.add_task(
        process_fileL5,
        execution_id,
        saved_path,
        user_id,
        user_name,
        user_email,
        parsed_stepping_back,
        timetable_type,

        # 🆕 Pass new fields to processing
        # duty_hours,
        # running_hours,
        single_run_max,
        break_small,
        break_large
    )

    return {
        "message": "File received. Processing started.",
        "execution_id": execution_id
    }


@app.get("/notices")
async def get_notices():
    notices = await notices_collection.find().sort("timestamp", -1).to_list(50)
    for n in notices:
        n["_id"] = str(n["_id"])
    return notices



@app.get("/status/{execution_id}")
def check_status(execution_id: str):
    return get_status(execution_id)

# @app.api_route("/download/{execution_id}", methods=["GET", "HEAD"])
# def download_file(execution_id: str):
#     # Always resolve to absolute path from this script's location
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     file_path = os.path.join(base_dir, "temp_files", f"trip_chart_{execution_id}.xlsx")

#     print("📁 Trying to serve file at:", file_path)

#     if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
#         return FileResponse(
#             path=file_path,
#             filename=f"trip_chart_{execution_id}.xlsx",
#             media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )
    
#     raise HTTPException(status_code=404, detail="File not ready or corrupted")
@app.api_route("/download/{execution_id}", methods=["GET", "HEAD"])
def download_file(execution_id: str):
    """
    Serve the Excel file corresponding to the execution_id.
    Handles both cases where execution_id may already contain 'trip_chart_' prefix.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Ensure no double prefix
    if not execution_id.startswith("trip_chart_"):
        execution_id = f"trip_chart_{execution_id}"

    # Ensure proper file extension
    if execution_id.endswith(".xlsx"):
        file_name = execution_id
    else:
        file_name = f"{execution_id}.xlsx"

    file_path = os.path.join(base_dir, "temp_files", file_name)

    # ✅ Only log when file is found
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        print(f"✅ File ready to serve: {file_name}")
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    # ❌ Don't print anything for missing/empty files to reduce spam
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
    
@app.get("/files/{file_id}")
async def get_file(file_id: str):
    try:
        grid_out = await fs.open_download_stream(ObjectId(file_id))
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(
        grid_out,
        media_type=grid_out.metadata.get("content_type", "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename={grid_out.filename}"}
    )


