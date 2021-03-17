import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sutorbank.items import Article


class SutorbankSpider(scrapy.Spider):
    name = 'sutorbank'
    start_urls = ['https://www.sutorbank.de/magazin/themen?tx_news_pi1%5BoverwriteDemand%5D%5Bcategories%5D=&cHash=a4423a1522dcb768c0b1df1da32648b3']

    def parse(self, response):
        links = response.xpath('//a[@class="teaser-feature__link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//nav[@class="pagination"]/a/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('(//main//div)[4]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
