import pymongo
from be.model import database

class Store:
    __database = None

    def __init__(self):
        self.database = database.get_db_conn()
        self.init_collections()

    def init_collections(self):
        self.database["user"].create_index([("user_id", pymongo.ASCENDING)])
        self.database["user_store"].create_index([("user_id", pymongo.ASCENDING), ("store_id", pymongo.ASCENDING)])
        self.database["store"].create_index([("book_id", pymongo.ASCENDING), ("store_id", pymongo.ASCENDING)])