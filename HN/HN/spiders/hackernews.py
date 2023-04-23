from pathlib import Path
import scrapy
import pandas as pd
import time


class HNSpider(scrapy.Spider):
    name = "hackernews"
    data = pd.DataFrame(columns=['title', 'link', 'hn_comments_link', 'date'])
    
    def start_requests(self):
        urls = [
            'https://news.ycombinator.com/front?day=2023-01-01',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.xpath('//span[@class="titleline"]/a/@href').getall()
        texts = response.xpath('//span[@class="titleline"]/a/text()').getall()
        hn_comment_links = response.xpath('//span[@class="subline"]/a[last()]/@href').getall()
        hn_comment_links = [f'news.ycombinator.com/{link}' for link in hn_comment_links]
        date = response.url.split('=')[1]
        dates = [date for _ in range(30)]
        today_data = pd.DataFrame({
            'title': texts,
            'link': links, 
            'hn_comment_link': hn_comment_links,
            'date': dates
        })
        self.data = pd.concat([self.data, today_data])
        if self.next_page(response):
            yield scrapy.Request(url = self.next_page(response), callback=self.parse)
            
    def next_page(self, response):
        more = response.xpath('//span[@class="hnmore"]')
        if len(more) < 5: 
            self.data.to_csv('hn_data.csv', index=False)
            return None
        tomorrow = response.xpath('//span[@class="hnmore"]/a/@href').getall()[3]
        time.sleep(1)
        return f'https://news.ycombinator.com/{tomorrow}'
        