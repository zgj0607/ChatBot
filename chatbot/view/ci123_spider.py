import json
import re

import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse

from chatbot.component.table_utils import ExcelWriteUtil
from chatbot.settings import logger

host = 'info.ci123.com'


def spider_product_info_ci123(headers):
    headers['Host'] = host
    first_page = '/Users/zhou/Documents/PycharmProject/ChatBot/ci123.html'

    # url = 'http://info.ci123.com/brand/brand/brands.php'
    #
    # r = requests.get(url, stream=True, verify=False, headers=headers)

    f = open(first_page, 'r')

    soup = BeautifulSoup(f.read(), 'html.parser', from_encoding='utf-8')
    total_brands = soup.find_all('ul', class_='brand_detail')
    result = []

    excel_headers = ['产品', '品牌', 'URL', '参考价格', '适用年龄', '综合评分', '浏览量', '点评数', '产品介绍']
    url = 'http://info.ci123.com/brand/list/all.php?brand_id='
    excel = ExcelWriteUtil('/Users/zhou/Documents/PycharmProject/ChatBot/ci123.xlsx', 'xlsx')
    excel.set_header(excel_headers)
    base_url = 'http://info.ci123.com/brand'
    for alpha_brands in total_brands:
        for brand in alpha_brands.find_all('a'):
            link = brand.get('href')
            matcher = re.search(r'id=(\w+?)$', link)
            brand = brand.get_text()
            if not matcher:
                continue
            brand_id = matcher.groups()[0]
            brand_url = url + brand_id
            print(brand, brand_id, brand_url)

            r = requests.get(brand_url, verify=False, headers=headers)
            product_page = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')

            for product in product_page.find_all('div', class_='p_con'):
                try:
                    row = {}
                    product_name = product.a.get_text().strip()
                    row['产品'] = product_name
                    row['品牌'] = brand

                    product_url = base_url + product.a.get('href').replace('..', '')
                    row['URL'] = product_url

                    price_info = product.div.div
                    price_info = price_info.get_text().split('\u3000')
                    product_price = price_info[0].split('：')[1]
                    row['参考价格'] = product_price

                    product_for_age = price_info[1].split('：')[1]
                    row['适用年龄'] = product_for_age

                    product_star = product.find('span', class_='red').get_text()
                    row['综合评分'] = product_star

                    product_view_num = product.find('div', class_='num').span.get_text()
                    product_star_num = product.find('div', class_='num').span.fetchNextSiblings('span')[0].get_text()
                    product_desc = product.p.get_text()
                    row['浏览量'] = product_view_num
                    row['点评数'] = product_star_num
                    row['产品介绍'] = product_desc
                    print(row)

                    excel.append_row(row)
                except Exception as e:
                    logger.error(e, exc_info=True)
                    excel.save()
                    continue
            excel.save()
        excel.save()
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")
