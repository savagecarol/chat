from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME", "auth_database")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "user")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db[COLLECTION_NAME]

# Test connection
print(client.list_database_names())
print(db.list_collection_names())
