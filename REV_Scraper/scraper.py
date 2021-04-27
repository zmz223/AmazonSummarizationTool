import scrapy 

class REV_Scraper(scrapy.Spider):
	name="rev_scraper"
	start_urls = ["https://www.amazon.com/dp/B007TUQF9O"]
