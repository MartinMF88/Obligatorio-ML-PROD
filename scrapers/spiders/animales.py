from typing import Iterator
import boto3
import requests
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
        "https://www.gallito.com.uy/inmuebles/casas",  # !cant=80
    ]

    rules = (
        Rule(LinkExtractor(allow=r"-\d{8}$"), callback="parse_property"),
    )
    
    def __init__(self):
        super().__init__()
        self.s3_bucket_name = "obligatoriomlprodmmmbfm"
        self.s3_client = boto3.client("s3")
        self.possible_types = {
            "casa": "HOUSE",
            "apartamento": "APARTMENT",
        }

    def parse_property(self, response):
        property_id = response.css("#HfCodigoAviso::attr('value')").get()
        img_urls = response.css("#HstrImg::attr('value')").get().split(",")
        details = response.css("div.iconoDatos + p::text").getall()
        property_type = self.possible_types.get(details[0].lower(), "UNKNOWN")

        jsonlines_data = []

        for img_url in img_urls:
            if img_url.endswith(".jpg"):
                img_data = requests.get(img_url).content
                object_key = f"images/{property_id}/{img_url.split('/')[-1]}"
                self.s3_client.put_object(Bucket=self.s3_bucket_name, Key=object_key, Body=img_data)

                image_info = {
                    "id": property_id,
                    "image_urls": [img_url],
                    "source": "gallito",
                    "url": response.url,
                    "link": response.url,
                    "property_type": property_type,
                }
                jsonlines_data.append(image_info)

        # Convertir las líneas de información en JSONL
        jsonlines_content = "\n".join(json.dumps(item, ensure_ascii=False) for item in jsonlines_data)

        # Crear o actualizar el archivo JSONL en S3
        jsonlines_file_key = f'properties_gallito/{property_id}.jsonl'
        try:
            existing_object = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=jsonlines_file_key)
            existing_jsonlines_content = existing_object['Body'].read().decode('utf-8')
            existing_jsonlines_content += "\n" + jsonlines_content  # Agregar nuevas líneas
            self.s3_client.put_object(Bucket=self.s3_bucket_name, Key=jsonlines_file_key, Body=existing_jsonlines_content)
        except self.s3_client.exceptions.NoSuchKey:
            # El archivo no existe, crearlo con las nuevas líneas
            self.s3_client.put_object(Bucket=self.s3_bucket_name, Key=jsonlines_file_key, Body=jsonlines_content)

    def closed(self, reason):
        super().closed(reason)