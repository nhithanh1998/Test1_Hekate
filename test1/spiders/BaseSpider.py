from abc import ABC
import scrapy
from urllib.parse import urljoin
from bson.objectid import ObjectId
from test1.items import BookItem, ReviewItem, CommentItem
from test1.utils.utils import extract_data, get_nested_value_from_dict, get_first_match, add_url_params


class BaseSpider(scrapy.Spider, ABC):
    name = 'base'
    start_url = 'https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh?page=1&per_page=30'

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse, dont_filter=True)

    def parse(self, response, **kwargs):
        # get next page and do parse process again
        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page:
            yield scrapy.Request(url=urljoin(response.url, next_page), callback=self.parse)

        # get all book links in page -> access inside -> parse
        next_book_links = extract_data(raw=response.css('html').get(), url=response.url, wanted_value='next_book_link')
        for link in next_book_links:
            # GoodRead using AJAX
            yield scrapy.Request(link['url'], callback=self.__parse_book_data, meta={'cur_page': 1,
                                                                                     'genesis_url': link['url']})

    def __parse_book_data(self, response):
        genesis_url = response.meta.get('genesis_url')
        cur_page = response.meta.get('cur_page')
        # get desire value by metadata in schema.org
        book_meta_data = extract_data(raw=response.css('html').get(), url=genesis_url, wanted_value='book')[0]
        book_id = get_first_match(r"(?!.*\/).*?(?=-)", genesis_url)

        # this function recursively use to get user reviews, this flag is to check if book data already insert
        # inside database we not need to get it data again
        # yield will return an Item and pass over Pipeline to save
        if cur_page is 1:
            # add additional field that GoodRead schema.org not declare in their meta_data
            book_item = BookItem()
            book_item['_id'] = book_id
            book_item['title'] = book_meta_data['title']
            book_item['url'] = genesis_url
            book_item['rate'] = book_meta_data['rate']
            book_item['author'] = book_meta_data['author']
            book_item['description'] = response.xpath('//div[@id="description"]/span[2]/text()').get()
            book_item['reviews'] = []
            yield book_item

        # travel to next page to get more review from community
        if response.xpath('//a[@class="next_page"]'):
            next_page = cur_page + 1
            next_link = add_url_params(genesis_url, {'language_code': '', 'page': next_page})
            yield scrapy.Request(url=next_link, callback=self.__parse_book_data, meta={'cur_page': next_page,
                                                                                       'genesis_url': genesis_url})

        # get other users review
        # access to get all review url -> review_page -> parse review
        for review_url in get_nested_value_from_dict(book_meta_data['reviews'], ['properties', 'url']):
            yield scrapy.Request(url=review_url, callback=self.__parse_book_review, meta={'book_id': book_id})

    def __parse_book_review(self, response):
        review_id = response.meta.get('review_id')
        book_id = response.meta.get('book_id')

        # get desire value by metadata in schema.org you can declare it in utils.util file
        metadata = extract_data(raw=response.css('html').get(), url=response.url, wanted_value='review')[0]
        if not review_id:
            review_item = ReviewItem()
            review_id = ObjectId()

            # re process review item before insert into database
            reviewer_url = metadata['reviewer_url']
            review_item['_id'] = review_id
            review_item['book_id'] = book_id
            review_item['user_id'] = get_first_match(r"(?!.*\/).*?(?=-)", reviewer_url)
            review_item['user_name'] = response.xpath("//a[@class='userReview']/text()").get()
            review_item['rate'] = metadata['rate']
            review_item['url'] = response.url
            review_item['content'] = metadata['content']
            review_item['date_posted'] = metadata['date_posted']
            review_item['comments'] = []
            yield review_item

        # travel to next page to get more comments in this review
        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page:
            yield scrapy.Request(url=urljoin(response.url, next_page), callback=self.__parse_book_review,
                                 meta={'review_id': review_id})

        # parse comments (reply) to this review
        for comment in self.__parse_comment(response, review_id):
            yield comment

    @staticmethod
    def __parse_comment(response, review_id):
        raw_comments = response.xpath('//div[@class="comment u-anchorTarget"]').getall()
        for raw_comment in raw_comments:
            comment_item = CommentItem()
            comment_sel = scrapy.Selector(text=raw_comment, type="html")
            comment_item['review_id'] = review_id
            comment_item['user_id'] = get_first_match(r"(?!.*\/).*?(?=-)",
                                                      comment_sel.xpath('//a/@href').extract_first())
            comment_item['user_name'] = comment_sel.xpath('//a/@title').extract_first()
            comment_item['content'] = comment_sel.xpath('//div[@class = "mediumText reviewText"]/text()').extract()[
                1].strip()
            comment_item['date_posted'] = comment_sel.xpath('//div[@class = "right"]/@title').extract_first()

            yield comment_item
