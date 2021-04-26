import os
import re
import numpy as np
import scrapy
import psycopg2
import pandas as pd

def get_asins(csv_path):
    data = pd.read_csv(csv_path)
    return list(np.array(data)[:, 0])


class ASIN_Spider(scrapy.Spider):
    name = "Review_Spider"
    ASINS = get_asins("links, asins, and categories.csv")
    start_urls = [
        'https://www.amazon.com/Hamilton-Beach-73400-Popcorn-Popper/dp/'+asin+'/ref=sr_1_51?dchild=1&keywords'
        '=popcorn+maker&qid=1619199982&sr=8-51#customerReviews' for asin in ASINS]

    row_list = []
    productInfoData = []

    def __int__(self, query):
        self.query = query

    def parse(self, response):
        FiveStar = ""
        FourStar = ""
        ThreeStar = ""
        TwoStar = ""
        OneStar = ""
        BestSellerRank = None

        try:
            index = ASIN_Spider.start_urls.index(response.request.url)
            ASIN = ASIN_Spider.ASINS[index]
            title = response.xpath("//span[@id='productTitle']/text()").get()
            title = title.strip()
            price = response.xpath("//span[@id='priceblock_ourprice']/text()").get()
            if price is None:
                price = response.xpath("//span[@id='priceblock_saleprice']/text()").get()
            producttableList = response.xpath(
                "//table[@id='productDetails_detailBullets_sections1']//th/text()").getall()
            for temp in producttableList:
                index = producttableList.index(temp)
                producttableList[index] = temp.strip()
                if producttableList[index] == 'Best Sellers Rank':
                    tempString = "//table[@id='productDetails_detailBullets_sections1']//tr[" + str(
                        index + 1) + "]/td/span/span[2]/text()"
                    string1 = response.xpath(tempString).get()
                    tempString2 = "//table[@id='productDetails_detailBullets_sections1']//tr[" + str(
                        index + 1) + "]/td/span/span[2]/a/text()"
                    string2 = response.xpath(tempString2).get()
                    BestSellerRank = string1 + string2

            aTag = response.xpath("//a[@data-hook='see-all-reviews-link-foot']")
            link = aTag.xpath("@href").extract()[0]
            allReviews = "https://www.amazon.com/" + str(link)
            yield response.follow(allReviews, callback=self.parse,
                                  meta={'ASIN': ASIN, 'title': title, 'price': price, 'BestSellerRank': BestSellerRank})
        except:
            productStar = response.xpath("//span[@data-hook='rating-out-of-text']/text()").get()
            numRatings = response.xpath("//span[@class='a-size-base a-color-secondary']/text()").get()
            starTableList = None
            percentages = []
            for table in response.xpath("//table[@id='histogramTable']"):
                if table.xpath("@class").extract()[0] == 'a-normal a-align-center a-spacing-base':
                    starTableList = response.xpath("//table[@id='histogramTable']/tr/td/span/a/text()").extract()
            if starTableList is not None:
                for string in starTableList:
                    string = string.strip()
                    if string.find('%') != -1:
                        percentages.append(string)
                FiveStar = percentages[0]
                FourStar = percentages[1]
                ThreeStar = percentages[2]
                TwoStar = percentages[3]
                OneStar = percentages[4]
            else:
                print('Logic Error')

            reviewIDList = response.xpath("//div[@data-hook='review']/@id").getall()
            for ID in reviewIDList:
                reviewTitle = response.xpath(
                    "//div[@id=\'" + ID + "\']//a[@data-hook='review-title']/span/text()").get()
                reviewStars = response.xpath(
                    "//div[@id=\'" + ID + "\']//i[@data-hook='review-star-rating']/span/text()").get()
                reviewDate = response.xpath("//div[@id=\'" + ID + "\']//span[@data-hook='review-date']/text()").get()
                reviewNumHelp = response.xpath(
                    "//div[@id=\'" + ID + "\']//span[@data-hook='helpful-vote-statement']/text()").get()
                reviewVerified = None
                try:
                    reviewVerified = response.xpath(
                        "//div[@id=\'" + ID + "\']//span[@data-hook='avp-badge']/text()").get()
                except:
                    reviewVerified = None
                reviewComment = response.xpath(
                    "//div[@id=\'" + ID + "\']//span[@data-hook='review-body']/span/text()").get()
                reviewComment = reviewComment.strip()
                temp_row = {}
                temp_row["path"] = response.meta['ASIN']
                temp_row["id"] = ID
                temp_row["review_title"] = reviewTitle
                temp_row["stars"] = reviewStars
                temp_row["reviewDate"] = reviewDate
                temp_row["reviewNumHelp"] = reviewNumHelp
                temp_row["reviewVerified"] = reviewVerified
                temp_row["reviewComment"] = reviewComment

                self.row_list.append(temp_row)
            # print(response.meta['ASIN'])
            # print(response.meta['title'])
            # print(response.meta['price'])
            # print(productStar)
            # print(numRatings)
            # print(response.meta['BestSellerRank'])
            # print(FiveStar)
            # print(FourStar)
            # print(ThreeStar)
            # print(TwoStar)
            # print(OneStar)

            pagination = response.xpath('//li[@class="a-last"]')
            link = pagination.css('a::attr(href)').get()
            next_page = link
            if next_page is not None:
                next_page = "https://www.amazon.com/" + link
                csv = pd.DataFrame(self.row_list).to_csv("reviews.csv")
                yield response.follow(next_page, callback=self.parse,
                                      meta={'ASIN': response.meta['ASIN'], 'title': response.meta['title'],
                                            'price': response.meta['price'],
                                            'BestSellerRank': response.meta['BestSellerRank']})


