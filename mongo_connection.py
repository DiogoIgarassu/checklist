# mongo_connection.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_mongo_client():
    uri = "mongodb+srv://diogoigarassu:S4Uai3QGAtn4AUkv@cluster0.5foqgxf.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client
