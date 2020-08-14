import re

from PIL import Image
from chatterbot import ChatBot
from chatterbot.logic import LogicAdapter
from pytesseract import pytesseract

from chatbot.logic.unknown import get_unknown_response
from chatbot.processor import tokenizer
from chatbot.settings import logger, BASE_DIR
from chatbot.vocabulary import Word


class ImageLogicAdapter(LogicAdapter):
    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.vocabulary = Word()

    def can_process(self, statement):
        text = statement.text
        match_result = re.search(r'img\[(.+\.(jpg|png|jpeg|bmp|gif|BMP|JPG|JPEG|PNG|GIF))\]$', text)

        if match_result:
            return True
        return False

    def process(self, statement, additional_response_selection_parameters=None):
        file_path = re.search(r'img\[(.+\.(jpg|png|jpeg|bmp|gif|BMP|JPG|JPEG|PNG|GIF))\]$', statement.text).groups()[0]
        full_saved_path = BASE_DIR + file_path

        image = Image.open(full_saved_path)

        # 识别中文和英文文字
        query_text = pytesseract.image_to_string(image, timeout=2, lang='chi_sim+eng')
        query_text = query_text.replace('\n', '').replace('\t', '').replace(' ', '')

        if not query_text:
            return get_unknown_response(statement.text)

        try:

            # pattern = re.compile('[^\u4e00-\u9fa50-9A-Za-z]+')  # 中文的编码范围是：\u4e00到\u9fa5
            statement.text = query_text
            statement.search_text = tokenizer(statement).search_text

            return get_unknown_response(query_text)

        except Exception as e:
            logger.error(e, exc_info=True)
            return get_unknown_response(query_text)
