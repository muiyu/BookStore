import time
import pytest
import json
from fe.access import book
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
from fe.access import book
from fe.access import auth
from fe import conf
from be.model import store
import re
import uuid
import random


class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, 2)
        self.db = store.database.get_db_conn()
        self.a_book_in_store = self.db["store"].find_one({})
        self.store_id = self.a_book_in_store["store_id"]
        all_books_in_store = self.db['store'].find({"store_id": self.store_id})
        book_infos_in_store = [json.loads(item["book_info"]) for item in all_books_in_store]
        existing_titles = [info["title"] for info in book_infos_in_store]
        existing_tags = []
        existing_content = []
        for info in book_infos_in_store:
            existing_tags += info['tags']
            existing_content += info['content'].split("\n")
        existing_tags = set(existing_tags)
        existing_content = set(existing_content)
        book_ids_in_store = [item["book_id"] for item in all_books_in_store]
        query = {
            "book_id": {"$nin": book_ids_in_store}
        }
        all_book_not_in_store = list(self.db['store'].find(query))
        for result in all_book_not_in_store:
            tags_of_res = set(json.loads(result['book_info'])['tags'])
            content_of_res_with_empty = re.split(r'\s+|[().,!?;]', json.loads(result['book_info'])['content'])
            content_of_res = set([line.strip() for line in content_of_res_with_empty if line.strip()])
            if (json.loads(result['book_info'])['title'] not in existing_titles) & tags_of_res.isdisjoint(existing_tags) & content_of_res.isdisjoint(existing_content):
                self.book_not_in_store = result
                break
        self.book_info_not_in_store = json.loads(self.book_not_in_store["book_info"])
        self.book_info = json.loads(self.a_book_in_store["book_info"])
        self.title_in_store = self.book_info['title']
        self.tag_in_store = self.book_info['tags'][random.randint(0,len(self.book_info['tags'])-1)]
        self.content_in_store = self.book_info['content'].split("\n")[0]
        self.title_not_in_store = self.book_info_not_in_store['title']
        self.tag_not_in_store = self.book_info_not_in_store['tags'][random.randint(0, len(self.book_info_not_in_store['tags']) - 1)]
        self.content_not_in_store = self.book_info_not_in_store['content'].split("\n")[0]
        yield

    def test_search_global(self):
        for b in self.books:
            test_title = b.title
            test_content = b.content.split("\n")[0]
            test_tag = b.tags[random.randint(0,len(b.tags)-1)]
            assert self.auth.search_book(title=test_title) == 200
            assert self.auth.search_book(content=test_content) == 200
            assert self.auth.search_book(tag=test_tag) == 200
            assert self.auth.search_book(title=test_title, content=test_content) == 200
            assert self.auth.search_book(title=test_title, tag=test_tag) == 200
            assert self.auth.search_book(content=test_content, tag=test_tag) == 200
            assert self.auth.search_book(title=test_title, content=test_content, tag=test_tag) == 200

    def test_search_global_not_exists(self):
        test_title = "This is a test title!"
        test_content = "This is a test context!"
        test_tag = "This is a test tag!"
        assert self.auth.search_book(title=test_title) == 529
        assert self.auth.search_book(content=test_content) == 529
        assert self.auth.search_book(tag=test_tag) == 529
        assert self.auth.search_book(title=test_title, content=test_content) == 529
        assert self.auth.search_book(title=test_title, tag=test_tag) == 529
        assert self.auth.search_book(content=test_content, tag=test_tag) == 529
        assert self.auth.search_book(title=test_title, content=test_content, tag=test_tag) == 529

    def test_search_in_store(self):
        assert self.auth.search_book(title=self.title_in_store, store_id=self.store_id) == 200
        assert self.auth.search_book(content=self.content_in_store, store_id=self.store_id) == 200
        assert self.auth.search_book(tag=self.tag_in_store, store_id=self.store_id) == 200
        assert self.auth.search_book(title=self.title_in_store, content=self.content_in_store, store_id=self.store_id) == 200
        assert self.auth.search_book(title=self.title_in_store, tag=self.tag_in_store, store_id=self.store_id) == 200
        assert self.auth.search_book(content=self.content_in_store, tag=self.tag_in_store, store_id=self.store_id) == 200
        assert self.auth.search_book(title=self.title_in_store, content=self.content_in_store, tag=self.tag_in_store, store_id=self.store_id) == 200

    def test_search_not_exist_store_id(self):
        store_id_not_exist = '不存在的商店'
        assert self.auth.search_book(title=self.title_in_store, store_id=store_id_not_exist) == 513
        assert self.auth.search_book(content=self.content_in_store, store_id=store_id_not_exist) == 513
        assert self.auth.search_book(tag=self.tag_in_store, store_id=store_id_not_exist) == 513
        assert self.auth.search_book(title=self.title_in_store, content=self.content_in_store,store_id=store_id_not_exist) == 513
        assert self.auth.search_book(title=self.title_in_store, tag=self.tag_in_store, store_id=store_id_not_exist) == 513
        assert self.auth.search_book(content=self.content_in_store, tag=self.tag_in_store,store_id=store_id_not_exist) == 513
        assert self.auth.search_book(title=self.title_in_store, content=self.content_in_store, tag=self.tag_in_store,store_id=store_id_not_exist) == 513

    def test_search_in_store_not_exist(self):
        # test_title = "This is a test title!"
        # test_content = "This is a test context!"
        # test_tag = "This is a test tag!"
        assert self.auth.search_book(title=self.title_not_in_store, store_id=self.store_id) == 529
        assert self.auth.search_book(content=self.content_not_in_store, store_id=self.store_id) == 529
        assert self.auth.search_book(tag=self.tag_not_in_store, store_id=self.store_id) == 529
        assert self.auth.search_book(title=self.title_not_in_store, content=self.content_not_in_store, store_id=self.store_id) == 529
        assert self.auth.search_book(title=self.title_not_in_store, tag=self.tag_not_in_store, store_id=self.store_id) == 529
        assert self.auth.search_book(content=self.content_not_in_store, tag=self.tag_not_in_store, store_id=self.store_id) == 529
        assert self.auth.search_book(title=self.title_not_in_store, content=self.content_not_in_store, tag=self.tag_not_in_store, store_id=self.store_id) == 529