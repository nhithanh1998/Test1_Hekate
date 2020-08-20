from pymongo import MongoClient


client = MongoClient("mongodb+srv://nhithanh123vnn:nhithanh123@cluster0.gwjou.mongodb.net")
db = client.get_database('test1')
collection = db.get_collection('book')
book = {
    "author": "Thanh"
}
book_id = collection.insert_one(book).inserted_id
print(book_id)