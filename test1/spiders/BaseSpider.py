from abc import ABC
import scrapy
import pprint

from test1.items import Book
from test1.utils.utils import extract_data

pp = pprint.PrettyPrinter(indent=2)

# https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh?page=1&per_page=30

class BaseSpider(scrapy.Spider, ABC):
    name = 'base'
    start_url = 'https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh?page=1&per_page=30'

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse)

    def parse(self, response, **kwargs):
        next_book_links = extract_data(raw=response.css('html').get(), url=response.url, wanted_value='next_book_link')
        # for link in next_book_links:
        #     yield scrapy.Request(url=link['url'], callback=self.parse_book_data)
        yield scrapy.Request(url=next_book_links[0]['url'], callback=self.parse_book_data)

    def parse_book_data(self, response):
        book = extract_data(raw=response.css('html').get(), url=response.url, wanted_value='book')[0]
        book['id'] = ''
        book['link'] = response.url

        book['description'] = response.xpath('//div[@id="description"]/span[2]/text()').get()
        pp.pprint(book)


# (?!.*\/).+
