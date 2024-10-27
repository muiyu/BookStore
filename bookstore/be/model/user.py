import jwt
import time
import logging
import pymongo
from be.model import error
from be.model import db_conn

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False

            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text.get("timestamp")
            if ts is None:
                return False
            
            now = time.time()
            if now - ts <= self.token_lifetime:
                return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))

        return False


    def register(self, user_id: str, password: str):
        try:
            # Check if user with the same user_id already exists
            existing_user = self.conn['user'].find_one({"user_id": user_id})
            if existing_user:
                return error.error_exist_user_id(user_id)

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            user_doc = {
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal
            }
            self.conn['user'].insert_one(user_doc)
            return 200, "ok"
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)

    def check_token(self, user_id: str, token: str) -> (int, str):
        user = self.conn['user'].find_one({'user_id': user_id})
        if user is None:
            return error.error_authorization_fail()

        db_token = user.get('token', '')
        is_token_valid = self.__check_token(user_id, db_token, token)
        if not is_token_valid:
            return error.error_authorization_fail()

        return 200, "ok"


    def check_password(self, user_id: str, password: str) -> (int, str):
        try:
            user = self.conn['user'].find_one({'user_id': user_id}, {'_id': 0, 'password': 1})
            if user is None:
                return error.error_authorization_fail()

            if user.get('password') != password:
                return error.error_authorization_fail()

        except pymongo.errors.PyMongoError as e:
            return 528, str(e)

        return 200, "ok"


    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            result = self.conn['user'].update_one(
                {'user_id': user_id},
                {'$set': {'token': token, 'terminal': terminal}}
            )
            if not result.matched_count:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, str(e), ""
        except Exception as e:
            return 530, str(e), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            result = self.conn['user'].update_one(
                {'user_id': user_id},
                {'$set': {'token': dummy_token, 'terminal': terminal}}
            )
            if not result.matched_count:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, str(e)
        return 200, "ok"


    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            result = self.conn['user'].delete_one({'user_id': user_id})
            if result.deleted_count != 1:
                return error.error_authorization_fail()
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, str(e)
        return 200, "ok"


    def change_password(self, user_id: str, old_password: str, new_password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            self.conn['user'].update_one(
                {'user_id': user_id},
                {'$set': {
                    'password': new_password,
                    'token': token,
                    'terminal': terminal,
                }},
            )
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, str(e)
        return 200, "ok"


    ### 新功能：图书搜索 ###
    def search_book(self, title='', content='', tag='', store_id=''):
        try:
            query = {}

            ### 根据title、content、tag、store_id查询图书 ###
            if title:
                query['title'] = {"$regex": title}
            if content:
                query['content'] = {"$regex": content}
            if tag:
                query['tags'] = {"$regex": tag}

            if store_id:
                store_query = {"store_id": store_id}
                store_result = self.conn["store"].find_one(store_query, {"book_id": 1})
                if not store_result:
                    return error.error_non_exist_store_id(store_id)
                book_ids = [item["book_id"] for item in store_result.get("book_id", [])]
                query['id'] = {"$in": book_ids}

            ### 获得符合条件的书籍信息 ###
            results = list(self.conn["books"].find(query))
            if not results:
                return 529, "No matching books found."
            else:
                return 200, "ok"
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, "{}".format(str(e))


    ### 新功能：收藏图书 ###
    def collect_book(self, user_id, book_id):
        try:
            ### 检查用户是否存在于数据库中 ###
            existing_user = self.conn['user'].find_one({"_id": user_id})
            if not existing_user:
                return error.error_non_exist_user_id(user_id)

            ### 检查该书籍是否已在用户的收藏中 ###
            if (book_id) in existing_user.get("collection", []):
                return error.error_exist_collection(book_id)

            ### 将书籍添加到用户的收藏中 ###
            self.conn['user'].update_one(
                {"_id": user_id},
                {"$addToSet": {"collection": (book_id)}}
            )
            return 200, "ok"
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, "{}".format(str(e))


    ### 新功能：取消收藏图书 ###
    def uncollect_book(self, user_id, book_id, store_id):
        try:
            ### 检查用户是否在数据库中 ###
            existing_user = self.conn['user'].find_one({"_id": user_id})
            if not existing_user:
                return error.error_non_exist_user_id(user_id)

            ### 从收藏中移除书籍 ###
            self.conn['user'].update_one(
                {"_id": user_id},
                {"$pull": {"collection": (book_id, store_id)}}
            )
            return 200, "ok"
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, "{}".format(str(e))


    ### 新功能：获取用户收藏 ###
    def get_collection(self, user_id):
        try:
            existing_user = self.conn['user'].find_one({"_id": user_id})
            if not existing_user:
                return error.error_non_exist_user_id(user_id)

            ### 获取用户的收藏 ###
            collection = existing_user.get("collection", [])
            return 200, collection
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, "{}".format(str(e))
        
    
    ### 新功能：收藏店铺 ###
    def collect_store(self, user_id, store_id):
        try:
            existing_user = self.conn['user'].find_one({"_id": user_id})
            if not existing_user:
                return error.error_non_exist_user_id(user_id)

            ### 检查店铺是否已在用户的收藏中 ###
            if store_id in existing_user.get("store_collection", []):
                return error.error_exist_collection(store_id)

            ### 将店铺添加到收藏中 ###
            self.conn['user'].update_one(
                {"_id": user_id},
                {"$addToSet": {"store_collection": store_id}}
            )
            return 200, "ok"
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, "{}".format(str(e))


    ### 新功能：取消收藏店铺 ###
    def uncollect_store(self, user_id, store_id):
        try:
            existing_user = self.conn['user'].find_one({"_id": user_id})
            if not existing_user:
                return error.error_non_exist_user_id(user_id)

            ### 从收藏中移除店铺 ###
            self.conn['user'].update_one(
                {"_id": user_id},
                {"$pull": {"store_collection": store_id}}
            )
            return 200, "ok"
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, "{}".format(str(e))


    ### 新功能：获取用户收藏的店铺 ###
    def get_store_collection(self, user_id):
        try:
            existing_user = self.conn['user'].find_one({"_id": user_id})
            if not existing_user:
                return error.error_non_exist_user_id(user_id)

            ### 获取用户的店铺收藏列表 ###
            store_collection = existing_user.get("store_collection", [])
            return 200, store_collection
        except pymongo.errors.PyMongoError as e:
            return 528, str(e)
        except Exception as e:
            return 530, "{}".format(str(e))
