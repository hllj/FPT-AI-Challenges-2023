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
    
    with open("data/storage/drug_filtered.json") as f:
        drug_items = json.load(f)
    db.insert_many("drug", drug_items)
    
    with open("data/storage/add_filtered.json") as f:
        add_items = json.load(f)
    db.insert_many("add", add_items)
        
if __name__ == '__main__':
    push_collections()
    
    # MONGODB_SERVER = "localhost"
    # MONGODB_PORT = 27017
    # MONGODB_DB = "storage"
    
    # db = StorageMongoDB(MONGODB_SERVER, MONGODB_PORT, MONGODB_DB)
    
    # # drugs = db.find_drug('Ibuprofen')
    
    # # for drug in drugs:
    # #     print(drug)
    
    # # print(db.actives)
    
    # text = "Đơn thuốc tham khảo:\n\n1. Paracetamol: Dùng để giảm sốt và giảm đau.\n   Liều lượng: Uống 1-2 viên mỗi 4-6 giờ khi cần thiết. Không vượt quá 8 viên trong 24 giờ.\n\n2. Ibuprofen: Dùng để giảm đau và giảm viêm.\n   Liều lượng: Uống 1-2 viên mỗi 6-8 giờ khi cần thiết. Không vượt quá 6 viên trong 24 giờ.\n\n3. Chlorpheniramine: Dùng để giảm triệu chứng dị ứng như chảy nước mũi và ngứa.\n   Liều lượng: Uống 1-2 viên mỗi 4-6 giờ khi cần thiết. Không vượt quá 6 viên trong 24 giờ.\n\n4. Dextromethorphan: Dùng để giảm ho.\n   Liều lượng: Uống 1-2 viên mỗi 4-6 giờ khi cần thiết. Không vượt quá 8 viên trong 24 giờ.\n\nLưu ý: Đây chỉ là đơn thuốc tham khảo và không thay thế cho sự tư vấn và chỉ định của bác sĩ. Trước khi sử dụng bất kỳ loại thuốc nào, hãy tham khảo ý kiến ​​của bác sĩ hoặc nhà dược."
    
    # all_active = []
    
    # for active in db.actives:
    #     if active == None:
    #         continue
    #     if active in text:
    #         x = re.search(active, text)
    #         all_active.append({
    #             'active': active, 
    #             'start': x.start()
    #         })
    #         print(x.start())
    
    # all_active.sort(key=lambda x: x['start'])

    # print(all_active)