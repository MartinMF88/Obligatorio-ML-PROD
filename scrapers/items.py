import scrapy

class QuoteItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    text = scrapy.Field()
    author = scrapy.Field()

class PropertyItem(scrapy.Item):
    id = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    link = scrapy.Field()
    property_type = scrapy.Field()
