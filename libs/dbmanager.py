import pymongo

class DBManager:
    """
    Class for maintaining a MongoDB database.
    """

    def __init__(self, dbpath):
        self.client = pymongo.MongoClient(dbpath)
        self.db = self.client["devgpt"] # database

    def drop_db(self):
        self.client.drop_database("devgpt")

    def add_data(self, collection_name, data):
        collection = self.db[collection_name]
        collection.insert_many(data)

    def get_all_documents(self, collection_name):
        return self.db[collection_name].find()
    
    def update(self, collection_name, filter, update):
        collection = self.db[collection_name]
        collection.update_one(filter, update)

    def close(self):
        self.client.close()