import scrapy
import re
from AmazonCloth.items import AmazonclothItem

class Amazon(scrapy.Spider):
    name = "amazon_product"
    START_URL = 'https://amazon.com'
    HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/57.0.2987.133 Safari/537.36"}

    def start_requests(self):
        yield scrapy.Request(url=self.START_URL, callback=self.parse_link, headers=self.HEADER)

    def parse_link(self, response):
        category_links = ['/Mens-Fashion/b/ref=nav_shopall_sft_men?ie=UTF8&node=7147441011',
                          '/Womens-Fashion/b/ref=nav_shopall_sft_women?ie=UTF8&node=7147440011',
                          '/Girls-Fashion/b/ref=nav_shopall_sft_girls?ie=UTF8&node=7147442011',
                          '/Boys-Fashion/b/ref=nav_shopall_sft_boys?ie=UTF8&node=7147443011'
                          ]

        for category in category_links:
            if 'https' in category:
                link = category
            else:
                link = self.START_URL + category
            yield scrapy.Request(url=link, callback=self.parse_division, dont_filter=True, headers=self.HEADER)

    # click clothing link
    def parse_division(self, response):
        clothing_link = response.xpath('//div[contains(@class, "categoryRefinementsSection")]'
                                       '/ul[@class="root"]/li/ul/li/a/@href')[0].extract()
        if 'https' in clothing_link:
            cloth_link = clothing_link
        else:
            cloth_link = self.START_URL + clothing_link
        yield scrapy.Request(url=cloth_link, callback=self.parse_department, dont_filter=True, headers=self.HEADER)

    # click Dress
    def parse_department(self, response):
        href_links = response.xpath('//div[contains(@class, "categoryRefinementsSection")]'
                                    '/ul[@class="root"]/li/ul/li/ul/li/a/@href').extract()
        for href in href_links:
            if 'https' in href:
                depart_link = href
            else:
                depart_link = self.START_URL + href
            yield scrapy.Request(url=depart_link, callback=self.parse_sub_department, dont_filter=True, headers=self.HEADER)

    # click Casual
    def parse_sub_department(self, response):
        sub_links = response.xpath('//div[contains(@class, "categoryRefinementsSection")]'
                                   '/ul[@class="root"]/li/ul/li/ul/li/ul/li/a/@href').extract()
        for sub_link in sub_links:
            if 'https' in sub_link:
                s_link = sub_link
            else:
                s_link = self.START_URL + sub_link
            yield scrapy.Request(url=s_link, callback=self.parse_page, dont_filter=True, headers=self.HEADER)

    # click pagenation
    def parse_page(self, response):
        page_links = []
        page_link = response.xpath('//span[@class="pagnLink"]/a/@href')[0].extract()
        page_link_num = response.xpath('//span[@class="pagnLink"]/a/text()')[0].extract()
        page_count = response.xpath('//span[@class="pagnDisabled"]/text()')[0].extract()

        for page_num in range(1, int(page_count)):
            page_list = page_link.replace('page={page_link_num}'.format(page_link_num=int(page_link_num)),
                                          'page={page_num}'.format(page_num=page_num))
            page_list = self.START_URL + page_list
            page_links.append(page_list)

        for p_link in page_links:
            if 'https' in p_link:
                sub_link = p_link
            else:
                sub_link = self.START_URL + p_link
            yield scrapy.Request(url=sub_link, callback=self.parse_product_link, dont_filter=True, headers=self.HEADER)

    # click product
    def parse_product_link(self, response):
        product_links = set(response.xpath('//div[@id="mainResults"]/ul//a[contains(@class, "a-link-normal")]'
                                           '/@href').extract())

        for product_link in product_links:
            if 'https' in product_link:
                pro_link = product_link
            else:
                pro_link = self.START_URL + product_link
            yield scrapy.Request(url=pro_link, callback=self.parse_product,
                                 dont_filter=True, headers=self.HEADER)

    #@staticmethod
    def parse_product(self, response):
        item = AmazonclothItem()

        price = response.xpath('//span[contains(@id,"priceblock")]/text()').extract()
        if '-' in price:
            price = price.split('-')[0]

        item["Wholesale_Price"] = price

        vsn = re.search('dp/(.*)/ref', response.url, re.DOTALL).group(1)
        item["VSN"] = vsn

        size_desc = response.xpath('//select/option[@class="dropdownAvailable"]/text()').extract()
        for i in range(0, len(size_desc)):
            size_desc[i] = remove_spaces(size_desc[i])
        item["Size_Desc"] = size_desc

        color_desc = response.xpath('//ul[contains(@class, "a-unordered-list")]'
                                    '/li[contains(@id, "color_name")]//img/@alt').extract()
        for i in range(0, len(color_desc)-1):
            color_desc[i] = remove_spaces(color_desc[i])
        item["Color_Desc"] = color_desc

        division_desc = response.xpath('//ul[contains(@class, "a-unordered-list")]'
                                       '/li/span/a/text()')[0].extract()
        item["Division_Description"] = remove_spaces(division_desc)

        department_desc = response.xpath('//ul[contains(@class, "a-unordered-list")]'
                                         '/li/span/a/text()')[1].extract()
        item["Department_Description"] = remove_spaces(department_desc)

        sub_department_desc = response.xpath('//ul[contains(@class, "a-unordered-list")]'
                                             '/li/span/a/text()')[2].extract()
        item["Sub_Department_Description"] = remove_spaces(sub_department_desc)

        brand = response.xpath('//a[@id="brand"]/@href')[0].extract()
        item['Brand_Desc'] = brand.split('/')[1].split('/')[0]

        yield item

    #@staticmethod
def remove_spaces(str):
    return ' '.join(str.split())
