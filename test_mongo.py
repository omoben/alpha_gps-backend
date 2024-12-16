import certifi
from pymongo import MongoClient

# MongoDB connection string
MONGO_URI = "mongodb+srv://dotmon:12345@gpscluster.rlkpc.mongodb.net/gps?retryWrites=true&w=majority&appName=GpsCluster"

try:
    # Connect to MongoDB with SSL verification using certifi
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    
    # Access the database
    db = client["gps"]
    print("Connected to MongoDB!")
except Exception as e:
    print(f"An error occurred: {e}")

