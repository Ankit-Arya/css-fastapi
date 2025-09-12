from fastapi import FastAPI, HTTPException, Depends
from models.request_models import UserSignUp, UserLogin, TokenResponse
from services.auth_service import register_user, authenticate_user, create_access_token
from pymongo.mongo_client import MongoClient
import certifi
from fastapi.middleware.cors import CORSMiddleware


uri = "mongodb+srv://greenthornarya676_db_user:NRhQ0lSyJBMjyD5I@ankit-css.fz6hv8r.mongodb.net/?retryWrites=true&w=majority&appName=ANKIT-CSS"
# uri = (
#     "mongodb://greenthornarya676_db_user:NRhQ0lSyJBMjyD5I@"
#     "ac-mvowc2p-shard-00-00.7ryelew.mongodb.net:27017,"
#     "ac-mvowc2p-shard-00-01.7ryelew.mongodb.net:27017,"
#     "ac-mvowc2p-shard-00-02.7ryelew.mongodb.net:27017/"
#     "?ssl=true&replicaSet=atlas-mvowc2-shard-0&authSource=admin&retryWrites=true&w=majority"
# )
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for testing
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
