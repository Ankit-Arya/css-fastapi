import bcrypt
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_long_secret_key"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=2)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def register_user(user_data, users_collection):
    # Restrict to @dmrc.org emails
    if not user_data.email.endswith("@dmrc.org"):
        return None  # invalid domain
    
    # Check if the user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        return None  # User already exists

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Prepare user document
    new_user = {
        "email": user_data.email,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }

    # Insert user into the database
    await users_collection.insert_one(new_user)

    return True  # Indicate success


async def authenticate_user(email: str, password: str, users_collection):
    user = await users_collection.find_one({"email": email})  # Await the coroutine properly
    if user and verify_password(password, user["password"]):
        return True
    return False
