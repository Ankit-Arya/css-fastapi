# import certifi
# from pymongo import MongoClient
# from pymongo.server_api import ServerApi

# # uri = "mongodb+srv://greenthornarya676_db_user:NRhQ0lSyJBMjyD5I@ankit-css.fz6hv8r.mongodb.net/?retryWrites=true&w=majority&appName=ANKIT-CSS"
# uri = "mongodb://localhost:27017"
# client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

# try:
#     print(client.server_info())  # Forces a connection
#     print("✅ Successfully connected to MongoDB Atlas!")
# except Exception as e:
#     print("❌ Connection failed:", e)
from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27017",
    tls=False
)

try:
    print(client.server_info())
    print("✅ Successfully connected to local MongoDB (Docker)!")
except Exception as e:
    print("❌ Connection failed:", e)
