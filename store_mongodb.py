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
        
        self._actives = None
        
        self._regex_drugs = None

        
    def insert_one(self, collection_name, item):
        collection = self.db[collection_name]
        collection.insert_one(item)
        
    def insert_many(self, collection_name, items):
        collection = self.db[collection_name]
        collection.insert_many(items)
        
    def find_drug(self, field, query_string, limit=3, sort=-1):
        query_string = query_string.replace('(', '\(').replace(')', '\)')
        collection = self.db['drug']
        items = collection.find({field: {"$regex": query_string}}).sort('Số lượng', sort).limit(limit)
        return items
    
    def create_query_string(self):
        self.db['drug'].aggregate([
            { "$project": { 
                    "Query": { "$concat": [
                        "$Hoạt chất",
                        {"$toString": {"$ifNull": [{"$concat": [".*", "$Liều dùng"]}, ""]} },
                    ]
                    } 
                } 
            },
            { "$merge": "drug" }
        ])
    
    @property
    def actives(self):
        if self._actives is None:
            self._actives = self.db['drug'].distinct('Hoạt chất')
        return self._actives
    
    @property
    def regex_drugs(self):
        if self._regex_drugs is None:
            self._regex_drugs = self.db['drug'].distinct('Query')
        return self._regex_drugs
        
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
    
    db.create_query_string()
        
if __name__ == '__main__':
    # push_collections()
    
    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "storage"
    
    db = StorageMongoDB(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB)
    search_options = [regex for regex in db.regex_drugs if regex is not None]
    search_options = list(set(search_options))
    search_options.sort()
    with open('data/search_option.json', 'w') as f:
        json.dump({'options': search_options}, f)
        