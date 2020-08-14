import json
import re

import requests
from bs4 import BeautifulSoup, Tag
from django.contrib.auth.models import User
from django.http import HttpResponse

from chatbot.component.table_utils import ExcelWriteUtil
from chatbot.models import Classification, QuestionAnswer, Knowledge

host = 'www.vivo.com.cn'


def spider_faq_vivo(headers):
    url = 'https://www.vivo.com.cn/service/questions/all'
    headers['Host'] = host

    r = requests.get(url, stream=True, verify=False, headers=headers)

    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')

    menus = soup.find_all('div', class_="menuItemBox")

    parent_cls = []
    cls_pattern = r'(\d{2,3})'
    user = User.objects.get(id=1)

    root_classification = Classification.objects.filter(name='Vivo')
    if not root_classification:
        root_classification = Classification()
        root_classification.name = 'Vivo'
        root_classification.parent = None
        root_classification.creator = user
        root_classification.modifier = user
        root_classification.save()
    else:
        root_classification = root_classification[0]
    root_id = root_classification.id

    for menu in menus:
        sub_class = []
        parent = menu.div.get_text().strip()
        submenus = menu.find_all('div', class_='underMenuItem')

        pc = Classification.objects.filter(name=parent).filter(parent__id=root_id)

        if pc:
            parent_classification = pc[0]
        else:
            parent_classification = Classification()
            parent_classification.parent = root_classification
            parent_classification.name = parent
            parent_classification.creator = user
            parent_classification.modifier = user
            parent_classification.save()
        parent_id = parent_classification.id

        if submenus:
            for submenu in submenus:
                sub_cls = submenu.get_text().strip()
                sub_class.append(sub_cls)
                onclick = str(submenu['onclick'])

                sc = Classification.objects.filter(name=sub_cls).filter(parent__id=parent_id)

                if sc:
                    sub_classification = sc[0]
                else:
                    sub_classification = Classification()
                    sub_classification.parent = parent_classification
                    sub_classification.name = sub_cls
                    sub_classification.creator = user
                    sub_classification.modifier = user
                    sub_classification.save()

                match = re.search(cls_pattern, onclick)
                if match:
                    category_id = match.group()

                    q_url = url + '?categoryId={}&scroll=0'.format(category_id)

                    q_req = requests.get(q_url, stream=True, verify=False, headers=headers)

                    q_soap = BeautifulSoup(q_req.content, 'html.parser', from_encoding='utf-8')

                    questions = q_soap.find_all('div', class_='listBox')

                    for question in questions:
                        qu = question.div.div.get_text()

                        q = Knowledge.objects.filter(title=qu)
                        if not q:
                            q = Knowledge()
                            q.title = qu
                            q.classification = sub_classification
                            q.modifier = user
                            q.creator = user
                            q.save()
                        else:
                            q = q[0]

                        print(q)
                        answer = question.find(class_='richText')
                        a = QuestionAnswer.objects.filter(knowledge__id=q.id)
                        if not a:
                            a = QuestionAnswer()
                            a.knowledge = q
                            a.creator = user
                            a.modifier = user
                            answer = ''.join([str(x) for x in answer.contents])
                            a.answer = answer
                            a.save()

                        print(answer)

            parent_cls.append({parent: sub_class})
        else:
            questions = soup.find_all('div', class_='listBox')

            for question in questions:
                qu = question.div.div.get_text()

                q = Knowledge.objects.filter(title=qu)
                if not q:
                    q = Knowledge()
                    q.title = qu
                    q.classification = parent_classification
                    q.modifier = user
                    q.creator = user
                    q.save()
                else:
                    q = q[0]

                print(q)
                answer = question.find(class_='richText')
                a = QuestionAnswer.objects.filter(knowledge__id=q.id)
                if not a:
                    a = QuestionAnswer()
                    a.knowledge = q
                    a.creator = user
                    a.modifier = user
                    answer = ''.join([str(x) for x in answer.contents])
                    a.answer = answer
                    a.save()
                print(answer)

    return HttpResponse(json.dumps({'result': parent_cls}), content_type="application/json")


def spider_product_info_vivo(headers):
    headers['Host'] = host

    url = 'http://www.vivo.com.cn/vivo/param/'
    r = requests.get(url, stream=True, verify=False, headers=headers)

    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
    menus = soup.find_all('ul', class_='vp-head-series-products')
    result = []

    excel = ExcelWriteUtil('/vivo.xlsx', 'xlsx')
    for menu in menus:
        serial_name = menu.get('data-series')
        for li in menu.find_all('li'):
            paras = {}
            if li.get('class'):
                continue
            brand_name = li.a.p.get_text()
            serial_url = li.a.get('href')

            brand_eng = serial_url.split('/')[-2]

            serial_url = url + brand_eng

            paras.setdefault('系列', serial_name)
            paras.setdefault('品牌', brand_name)
            paras.setdefault('地址', serial_url)
            print('整在处理:{}'.format(brand_name))

            r = requests.get(serial_url, stream=True, verify=False, headers=headers)

            para_soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')

            colors = []
            for color in para_soup.find_all('div', class_='color'):
                colors.append(color.get('data-colorname'))

            paras.setdefault('产品颜色', ','.join(colors))

            for para in para_soup.find_all('div', class_='productColor'):
                left = para.find(class_='leftBox')
                middle = para.find(class_='middleBox')
                right = para.find(class_='rightBox')

                super_para = left.get_text().strip()

                if super_para == '产品颜色':
                    continue

                if not middle:
                    paras.setdefault(super_para, right.get_text().strip())
                    continue

                if super_para == '物理规格':
                    for spec in middle.find_all('div', class_=''):
                        seg = spec.get_text().split(":")
                        paras.setdefault(seg[0].strip(), seg[1].strip())
                    continue
                print(middle.div.contents)
                middle_contents = list(filter(lambda x: isinstance(x, Tag), middle.div.contents))
                print(right.div.contents)
                right_contents = list(filter(lambda x: isinstance(x, Tag), right.div.contents))

                for index, tag in enumerate(middle_contents):
                    paras.setdefault(tag.get_text().strip(), right_contents[index].get_text().strip())

            result.append(paras)
            excel.append_row(paras)
            excel.save()
            print('{}处理完成'.format(brand_name))
        excel.save()
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")
