import json

from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from fake_useragent import UserAgent

from chatbot.view.ci123_spider import spider_product_info_ci123
from chatbot.view.vivo_spider import spider_faq_vivo, spider_product_info_vivo


class Spider(TemplateView):
    template_name = 'spider/spider.html'


class FAQSpider(View):
    def get(self, request, *args, **kwargs):
        brand = request.GET['brand'].strip()

        if not brand:
            return HttpResponse(json.dumps({'result': None}))

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        }

        brand = brand.lower()

        if brand == 'vivo faq':
            return spider_faq_vivo(headers)

        if brand == 'vivo para':
            return spider_product_info_vivo(headers)

        if brand == 'ci123 brand':
            return spider_product_info_ci123(headers)
