from scrapy.item import Item, Field


class Book(Item):
    book_id = Field()
    book_url = Field()
    book_title = Field()
    book_description = Field()