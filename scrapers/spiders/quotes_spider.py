import scrapy

from scrapers.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    custom_settings = {
        "FEEDS": {
            "quotes.jl": {"format": "jsonlines"},
        },
        "CLOSESPIDER_ITEMCOUNT": 30,
    }
    def start_requests(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):      
        quotes = response.css(".quote")
        for quote in quotes:
            text = quote.css(".text::text").get()
            id = hash(text) # hash creates a unique id for the quote
            author = quote.css(".author::text").get()
            yield QuoteItem(id=id, text=text, author=author)
