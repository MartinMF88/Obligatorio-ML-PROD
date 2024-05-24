from typing import Iterator

from requests.utils import requote_uri
from scrapy import signals
from scrapy.http.response.html import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scrapers.items import PropertyItem


class AnimalesSpider(CrawlSpider):
    name = "animales"
    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ),
        "FEEDS": {
            "properties_animales.jl": {"format": "jsonlines"},
        },
        "CLOSESPIDER_ITEMCOUNT": 30,
    }
    start_urls = [
        "https://pixabay.com/es/photos/search/animales/",  # !cant=80
        "https://pixabay.com/es/photos/search/mundo%20animal/",  # !cant=80
    ]

    rules = (
    Rule(
        LinkExtractor(
            allow=(
                r"/es/photos/search/animales/\?pag=\d+",  
                r"/es/photos/search/mundo%20animal/\?pag=\d+",
            )
        )
    ),
    Rule(LinkExtractor(allow=(r"/es/photos/\w+-\d+/")), callback="parse_image"),
    )

    def parse_property(self, response: HtmlResponse) -> Iterator[dict]:
        def get_with_css(query: str) -> str:
            return response.css(query).get(default="").strip()

        def extract_with_css(query: str) -> list[str]:
            return [
                line for elem in response.css(query).extract() if (line := elem.strip())
            ]


        animal_id = None 
        img_urls = response.css("img[class='preview-img']::attr(src)").getall()
        possible_types = {
        "animales": "ANIMALS",
        "mundo animal": "ANIMAL WORLD",
        }


        fixed_details = extract_with_css("div.iconoDatos + p::text")
        animal_type = possible_types[fixed_details[0].lower()]

        animal = {
            "id": animal_id,
            "image_urls": img_urls,
            "source": "animales",
            "url": requote_uri(response.request.url),
            "link": requote_uri(response.request.url),
            "property_type": animal_type,
        }
        yield PropertyItem(**property)