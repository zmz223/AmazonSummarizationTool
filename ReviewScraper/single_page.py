import requests
from bs4 import BeautifulSoup
import pandas as pd

#Input number of pages
no_pages = 2


def get_data(pageNo, asin):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r = requests.get('https://www.amazon.com/product-reviews/' + asin +
                     '/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=' + str(pageNo),
                     headers=headers)
    content = r.content
    soup = BeautifulSoup(content, features="lxml")
    # print(soup)

    alls = []

    for d in soup.findAll('div', attrs={'a-section review aok-relative'}):
        print(d)
        rating = d.find('span', attrs={'class': 'a-link-normal'})
        reviews = d.find('span', attrs={'class': 'a-size-base review-text review-text-content'})

        single = []

        if rating is not None:
            single.append(rating.text)

        if reviews is not None:
            single.append(reviews.text)

        alls.append(single)
    return alls


results = []
for i in range(1, no_pages + 1):
    print(get_data(i, "B00PFDH0IC"))
    results.append(get_data(i, "B00PFDH0IC"))

print(results)
