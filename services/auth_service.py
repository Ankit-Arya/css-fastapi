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


# def register_user(user_data, users_collection):
#     if users_collection.find_one({"email": user_data.email}):
#         return None
#     hashed = hash_password(user_data.password)
#     users_collection.insert_one({"email": user_data.email, "password": hashed})
#     return True
async def register_user(user_data, users_collection):
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        return None
    hashed = hash_password(user_data.password)
    await users_collection.insert_one({"email": user_data.email, "password": hashed})
    return True

# def authenticate_user(email, password, users_collection):
#     user = users_collection.find_one({"email": email})
#     if user and verify_password(password, user["password"]):
#         return True
#     return False


async def authenticate_user(email: str, password: str, users_collection):
    user = await users_collection.find_one({"email": email})  # Await the coroutine properly
    if user and verify_password(password, user["password"]):
        return True
    return False
