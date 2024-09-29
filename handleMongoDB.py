from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# MongoDB Configuration and Connection
def get_mongo_client():
    """Initialize and return the MongoDB client"""
    MONGO_URI_USER = os.getenv("MONGO_URI_USER")
    MONGO_URI_PASSWORD = os.getenv("MONGO_URI_PASSWORD")
    uri = f"mongodb+srv://{MONGO_URI_USER}:{MONGO_URI_PASSWORD}@cluster0.p39u4.mongodb.net/?retryWrites=true&w=majority&ssl=true"

    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    
def initClient():
  # Initialize MongoDB client and select collection
  mongo_client = get_mongo_client()
  if mongo_client:
      users_collection = mongo_client['Pitt_Students']['users']  # Replace 'Pitt_Students' with your database name
  else:
      raise Exception("MongoDB connection failed. Check your connection settings.")
  
  return mongo_client, users_collection