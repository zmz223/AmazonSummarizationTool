import os
import re
import scrapy
import psycopg2

class ASIN_Spider(scrapy.Spider):

    if os.path.exists("../../asins.txt"):
        os.remove("../../asins.txt")

    name = "ASIN_Spider"
    start_urls = ['https://www.amazon.com/s?i=electronics&bbn=597566&rh=n%3A172282%2Cn%3A281407%2Cn%3A172532%2Cn%3A172540%2Cn%3A597566%2Cn%3A1288217011&dc&fs=true&qid=1616970663&rnid=597566&ref=sr_nr_n_2']
    def __int__(self, query):
        self.query = query

    def parse(self, response):
        asinList = []
        allASINDivs = response.xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div/span[3]/div[2]")
        pagination = allASINDivs.xpath('//li[@class="a-last"]')
        link = pagination.css('a::attr(href)').get()
        ASIN_dict = {}
        for ind in range(2, 200):
            try:
                asin_div = response.xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div/span[3]/div[2]/div["+str(ind)+"]").re_first("<div data-asin=\"[A-Z0-9]+\"")
                ASIN = re.search("[A-Z0-9]+", asin_div)[0]
                ASIN_dict["item"+str(ind)] = ASIN
            except Exception:

                with open("../../asins.txt", "a") as f:
                    for item in ASIN_dict:

                        asinList.append(ASIN_dict[item])
                        f.write(item+":\t" + ASIN_dict[item]+"\n")

                        #print(ASIN_dict[item])
                        f.write(ASIN_dict[item]+"\n")
                break

        next_page = link
        if next_page is not None:
            next_page = "https://www.amazon.com/" + link
            yield response.follow(next_page, callback=self.parse)

        con = psycopg2.connect(
            database="amazonProducts",
            user="postgres",
            password="$daxc8pofg!",
            host="localhost",
            port=5432
        )

        cur = con.cursor()

        for i in range(0, len(asinList)):
            cur.execute("insert into products (asin, department) values (%s, %s)", (asinList[i], "Electronics|Accessories & Supplies|Audio & Video Accessories|Cables & Interconnects|Audio Cables|Fiber Optic Cables"))
            con.commit()

        cur.close()