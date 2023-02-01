from scrapy.crawler import CrawlerProcess
from spiders.spider import BitcoinRichListSpider


if __name__ == "__main__":
    spider = BitcoinRichListSpider()
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(BitcoinRichListSpider)
    process.start()
