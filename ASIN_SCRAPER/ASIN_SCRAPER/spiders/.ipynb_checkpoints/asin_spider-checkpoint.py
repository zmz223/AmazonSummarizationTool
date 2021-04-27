import scrapy
import re

class ASIN_Spider(scrapy.Spider):
    name = "ASIN_Spider"
    start_urls = ['https://www.amazon.com/s?k=water&ref=nb_sb_noss_2']

    def __int__(self, query):
        self.query = query

    def parse(self, response):
        ASIN_dict = {}
        for ind in range(2, 200):
            try:
                asin_div = response.xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div/span[3]/div[2]/div["+str(ind)+"]").re_first("<div data-asin=\"[A-Z0-9]+\"")
                ASIN = re.search("[A-Z0-9]+", asin_div)[0]
                ASIN_dict["item"+str(ind)] = ASIN
            except Exception:
                with open("../../asins.txt", "w") as f:
                    for item in ASIN_dict:
                        f.write(item+":\t" + ASIN_dict[item]+"\n")
                break




