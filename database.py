# bot/database.py
from pymongo import MongoClient
from pymongo.write_concern import WriteConcern
from gridfs import GridFS
import os
from datetime import datetime

MONGO_URI = os.getenv('MONGO_URI', 'YOUR_MONGO_URI')
MONGO_DB = "telegram_bot"

try:
    client = MongoClient(MONGO_URI, w='majority', wtimeoutms=1000)
    db = client[MONGO_DB]
    fs = GridFS(db)
    users_collection = db['authorized_users']
    access_collection = db['access_count']
    logs_collection = db['logs']
    feedback_collection = db['feedback']
    blocked_collection = db['blocked_users']
except Exception as e:
    print(f"MongoDB connection error: {e}")
    raise

def load_authorized_users():
    # ... (your load_authorized_users function)
    pass

def save_authorized_user(user_id, retries=3):
    # ... (your save_authorized_user function)
    pass

def remove_authorized_user(user_id):
    # ... (your remove_authorized_user function)
    pass

# ... (other MongoDB helper functions: load_blocked_users, save_blocked_user, etc.)
