from scrapy.item import Item, Field


class Review(Item):
    user_id = Field()
    user_name = Field()
    review_rate = Field()
    review_content = Field()
    created_date = Field()
