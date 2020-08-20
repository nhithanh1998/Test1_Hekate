# Hekate Test1
Crawl data from [Goodreads](https://www.goodreads.com/book/show/10925109-cho-t-i-xin-m-t-v-i-tu-i-th) page
### Desire output data:
  - Book
  - Review
  - Comment

### Install requirement package
This project use **Python** base with [**Scrapy**](https://docs.scrapy.org/en/latest/) framework and **pymongo** package.
- `pip install scrapy`
- `pip install pymongo`


### Solution

Take adavantage of *standard structured data* [**schema.org**](https://schema.org/) which carefully implemented by GoodRead with some custom parser to get the desire data.
To get all the language comments from **BookDetailPage** we need to figure out the pattern in their **GET** method (?language=&page=?) to travel through out the entire page. 

### Start crawl data

Running the script file in `test1/script.js`

```sh
$ python test1/script.js
```

### Using your own mongo environment to save crawl data
Declare `MONGO_URI` and `MONGO_DATABASE` in the `test1/settings.py` with your desire environment

```
# sample
MONGO_URI = 'mongodb+srv://nhithanh123vnn:nhithanh123@cluster0.gwjou.mongodb.net'
MONGO_DATABASE = 'test1'
```


### Backup database
You can use `book.json`, `review.json`, and `comment.json` to do back up inside your **Mongo Compass**

### Overview total data after crawl
![alt text](https://raw.githubusercontent.com/nhithanh1998/Test1_Hekate/master/overview.png "Logo Title Text 1")
