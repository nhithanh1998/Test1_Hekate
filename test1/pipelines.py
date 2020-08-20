import pymongo
from itemadapter import ItemAdapter
from test1.items import BookItem, ReviewItem, CommentItem
from bson.objectid import ObjectId


class MongoPipeline:
    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            self.insert_book_item(item)
            return []
        if isinstance(item, ReviewItem):
            self.insert_review_item(item)
            return []
        if isinstance(item, CommentItem):
            self.insert_comment_item(item)
        return item

    def insert_book_item(self, item):
        self.db['book'].insert_one(ItemAdapter(item).asdict())

    def insert_review_item(self, item):
        review_id = self.db['review'].insert_one(ItemAdapter(item).asdict()).inserted_id
        self.db['book'].find_one_and_update(
            {'_id': item.get('book_id')},
            {'$addToSet': {'reviews': review_id}}
        )

    def insert_comment_item(self, item):
        comment_id = self.db['comment'].insert_one(ItemAdapter(item).asdict()).inserted_id
        self.db['review'].find_one_and_update(
            {'_id': item.get('review_id')},
            {'$addToSet': {'comments': comment_id}}
        )
