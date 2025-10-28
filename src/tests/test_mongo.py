import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def test_mongo_connection():
    client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
    client.admin.command("ismaster")
    print("MongoDB connection successful!")
