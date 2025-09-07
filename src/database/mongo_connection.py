# src/database/mongo_connection.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "metaliverpool-intern")

# Raise error if missing
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables.")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def get_mongo_connection():
    """
    Returns the MongoDB connection object.
    
    Returns:
        MongoClient: The MongoDB client connected to the specified database.
    """
    return db