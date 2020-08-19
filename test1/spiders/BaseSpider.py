from abc import ABC
import re
import scrapy
from urllib.parse import urljoin

import pprint

from test1.items import Book
from test1.utils.utils import extract_data, get_nested_value_from_dict

pp = pprint.PrettyPrinter(indent=2)


# https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh?page=1&per_page=30

class BaseSpider(scrapy.Spider, ABC):
    name = 'base'
    start_url = 'https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh?page=1&per_page=30'

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse)

    def parse(self, response, **kwargs):
        # get next page and do parse process again
        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page:
            yield scrapy.Request(url=urljoin(response.url, next_page), callback=self.parse)

        # get all book links in page -> access inside -> parse
        next_book_links = extract_data(raw=response.css('html').get(), url=response.url, wanted_value='next_book_link')
        for link in next_book_links:
            yield scrapy.Request(url=link['url'], callback=self.__parse_book_data)

    def __parse_book_data(self, response):
        page_url = response.url

        # get desire value by metadata in schema.org
        book = extract_data(raw=response.css('html').get(), url=page_url, wanted_value='book')[0]

        # add additional field that GoodRead schema.org not declare in their meta_data
        pattern = r"(?!.*\/).*?(?=-)"
        book['id'] = re.findall(pattern, response.url)[0]
        book['link'] = page_url
        book['description'] = response.xpath('//div[@id="description"]/span[2]/text()').get()

        # travel to next page to get more review from community
        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page:
            yield scrapy.Request(url=urljoin(response.url, next_page), callback=self.__parse_book_review)

        # get other users review
        # access to get all review url -> review_page -> parse review
        for review_url in get_nested_value_from_dict(book['reviews'], ['properties', 'url']):
            yield scrapy.Request(url=review_url, callback=self.__parse_book_review)

    def __parse_book_review(self, response):
        # get desire value by metadata in schema.org you can declare it in utils.util file
        review = extract_data(raw=response.css('html').get(), url=response.url, wanted_value='review')[0]
        # add additional field that not covered yet in their metadata
        pattern = r"(?!.*\/).*?(?=-)"
        reviewer_url = review['review_url']
        review['name'] = response.xpath("//a[@class='userReview']/text()").get()
        review['reviewer_id'] = re.findall(pattern, reviewer_url)[0]
        # parse comments (reply) to this review
        self.parse_comment(response)

    def parse_comment(self, response):
        comments = []

        # travel to next page to get more comments
        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page:
            yield scrapy.Request(url=urljoin(response.url, next_page), callback=self.parse)

        # parse comment
        raw_comments = response.xpath('//div[@class="comment u-anchorTarget"]').getall()
        for raw_comment in raw_comments:
            comments.append(self.__parse_comment_from_raw(raw_comment))
        return comments

    @staticmethod
    def __parse_comment_from_raw(raw_comment):
        comment_sel = scrapy.Selector(text=raw_comment, type="html")
        pattern = r"(?!.*\/).*?(?=-)"
        name = comment_sel.xpath('//a/@title').extract_first()
        user_id = re.findall(pattern, comment_sel.xpath('//a/@href').extract_first())[0]
        content = comment_sel.xpath('//div[@class = "mediumText reviewText"]/text()').extract()[1].strip()
        date = comment_sel.xpath('//div[@class = "right"]/@title').extract_first()
        return {
            'user_id': user_id,
            'user_name': name,
            'comment_content': content,
            'created_date': date
        }
