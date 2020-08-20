from scrapy import Item, Field


class BookItem(Item):
    _id = Field()
    title = Field()
    url = Field()
    description = Field()
    rate = Field()
    author = Field()
    reviews = Field()


class ReviewItem(Item):
    _id = Field()
    book_id = Field()
    user_id = Field()
    user_name = Field()
    rate = Field()
    content = Field()
    date_posted = Field()
    replies = Field()
