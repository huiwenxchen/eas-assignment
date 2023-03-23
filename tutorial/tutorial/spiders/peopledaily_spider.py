"""
A Scrapy spider for scraping data 
"""

import scrapy
from datetime import datetime

class PeoplesSpider(scrapy.Spider):
    """
    Starter spider for scraping data
    """
    name = "peoples"

    start_urls = [
        'http://en.people.cn/90777/index.html'
        ]
    
    def parse(self, response):
        """
        scrape article links and next page
        """
        def extract_date(datetime_str):
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            date_str = datetime_obj.strftime("%Y-%m-%d")
            return date_str
        article_info = response.css("ul.foreign_list8 li")
        start_date = '2023-01-01'
        end_date = '2023-02-28'

        for info in article_info:
            article_date = extract_date(info.css('span::text').get())
            if article_date > end_date:
                continue
            elif article_date >= start_date and article_date <= end_date:
                print('article date', article_date)
                link = info.css('a::attr(href)').get()
                yield response.follow(link, callback=self.parse_article)
            else:
                break

        curr = response.css("div.page_n a.common_current_page::text").get()
        if curr is not None:
            num = int(curr) + 1
            next_page = 'http://en.people.cn/90777/' + 'index' + str(num) + '.html'
            print('next link', next_page)
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        """
        scrape article content
        """
        def extract_with_css(query):
            etext = response.css(query).getall()[1:]
            content = ""
            for line in etext:
                content += line.strip()
            return content

        yield {
            'date': response.css('div.origin span::text').get(),
            'author': response.css('div.origin a::text').get(),
            'title': response.css('div.w860 h1::text').get(),
            'content': extract_with_css('div.w860 p::text')
        }