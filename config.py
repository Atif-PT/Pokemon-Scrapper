
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGO_DB_CLIENT_URI = "mongodb+srv://abdulpk:zw87kc28@pokemonscrapper.attl5.mongodb.net/"

# Create a new client and connect to the server
client = MongoClient(MONGO_DB_CLIENT_URI, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)