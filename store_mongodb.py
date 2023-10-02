import pymongo
import json
import re

class StorageMongoDB:
    def __init__(self, server, port, db):
        connection = pymongo.MongoClient(
            server,
            port
        )
        self.db = connection[db]
        
        self._actives = self.db['drug'].distinct('Hoạt chất')
        
    def insert_one(self, collection_name, item):
        collection = self.db[collection_name]
        collection.insert_one(item)
        
    def insert_many(self, collection_name, items):
        collection = self.db[collection_name]
        collection.insert_many(items)
        
    def find_drug(self, active_name, limit=3, sort=-1):
        collection = self.db['drug']
        items = collection.find({'Hoạt chất': active_name}).sort('Số lượng', sort).limit(limit)
        return items
    
    @property
    def actives(self):
        return self._actives
        
def push_collections():
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "storage"
    
    db = StorageMongoDB(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB)
    
    with open("data/storage/drug_filtered.json", encoding='utf-8') as f:
        drug_items = json.load(f)
    db.insert_many("drug", drug_items)
    
    with open("data/storage/add_filtered.json", encoding='utf-8') as f:
        add_items = json.load(f)
    db.insert_many("add", add_items)
        
if __name__ == '__main__':
    push_collections()