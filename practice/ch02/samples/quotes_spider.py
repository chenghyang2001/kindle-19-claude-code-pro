"""範例：有問題的 Scrapy 爬蟲（情境 A 用；本機未安裝 scrapy，僅供提示詞內容）"""
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["http://quotes.toscrape.com/page/1/"]

    def parse(self, response):
        for q in response.css("div.quote"):
            yield {
                "text": q.css("span.text::text").get(),
                "author": q.css("small.author::text").extract()[0],
            }
        next_page = response.css("li.next a::attr(href)").get()
        yield scrapy.Request(next_page, callback=self.parse)
