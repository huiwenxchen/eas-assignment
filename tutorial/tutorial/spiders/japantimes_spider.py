"""
A Scrapy spider for scraping data 
"""

import scrapy
from datetime import datetime

class PeoplesSpider(scrapy.Spider):
    """
    Starter spider for scraping data from Japan Times
    """
    name = "japan"

    start_urls = [
        'https://www.japantimes.co.jp/news_category/world/page/150/'
        ]
    
    page = 150
    start_date = '2023-01-01'
    end_date = '2023-02-28'
    def parse(self, response):
        """
        scrape article links and next page
        """
        page_info = response.css('article')

        for info in page_info:
            link = info.css('a::attr(href)').get()
            # get date and validate time range
            # Split the URL by '/' and get the date parts from the 4th index
            date_parts = link.split('/')[4:7]
            # Join the date parts with '-' separator
            article_date = '-'.join(date_parts)
            if article_date > self.end_date:
                continue
            elif article_date >= self.start_date and article_date <= self.end_date:
                print('article date', article_date)
                link = info.css('a::attr(href)').get()
                yield response.follow(link, callback=self.parse_article)
            else:
                print('break')
                break

            # next_page = response.css('span.pages a::attr(href)').get()\
        self.page -= 1
        next_page = 'https://www.japantimes.co.jp/news_category/world/page/' + str(self.page) + '/'
        print('next link', next_page)
        yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        """
        scrape article content
        """
        def extract_with_css(query):
            etext = response.css(query).getall()
            content = ""
            for line in etext:
                n_line = line.strip()
                end_line = "This could be due to a conflict with your ad-blocking or security software."
                if n_line in end_line:
                    break
                content += n_line
            print('content', content)
            return content
        def get_author(query):
            if response.css(query).get() is None:
                return "Unkown Author - Japan Times"
            else:
                return response.css(query).get()
        yield {
            'date': response.css('div.meta-right ul li time::attr(datetime)').get(),
            'author': get_author('div.meta-left ul li a::text'),
            'title': response.css('div.main div.padding_block h1::text').get(),
            'content': extract_with_css('div.entry p::text')
        }