import os

from pymongo import MongoClient

MONGO = os.getenv('MONGO_URI', 'mongodb://mongo:27017')
client = MongoClient(MONGO)
telemetry = client.operations.telemetry


def store_telemetry(device):
    telemetry.update_one({'deviceId': device['deviceId']}, {'$set': device}, upsert=True)


def list_devices(store_id):
    return list(telemetry.find({'storeId': store_id}, {'_id': 0}).sort('deviceId', 1))