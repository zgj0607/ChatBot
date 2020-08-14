import re

import jieba

from chatbot.component.singleton import singleton
from chatbot.const import const
from chatbot.models import Vocabulary
from chatbot.settings import CHATTERBOT


@singleton
class Word(object):
    def __init__(self):
        self.stopwords_list = {}
        self.vocabulary_path = CHATTERBOT['vocabulary_path']
        self.cutter = jieba

        # 定义中文识别的范围，用于实现带空格词的识别
        self.cutter.re_han_default = re.compile(
            r'([\u4E00-\u9FD5a-zA-Z0-9+#&\.\\/_%\s\-\'\"\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u2018\u2019]+)',
            re.U)

        self.synonyms = {}
        self.loading_user_dict()
        self._init_synonym_words()
        self._init_stop_words()

    def _init_stop_words(self):
        if len(self.stopwords_list):
            return
        for word in Vocabulary.objects.filter(word_type=const.STOP_WORD):
            word = word.word.strip()
            if word:
                self.stopwords_list.setdefault(word, word)

        with open(self.vocabulary_path + '/StopWords.txt') as f:
            for w in f.readlines():
                word = w.strip()
                if word:
                    self.stopwords_list.setdefault(word, word)

    def _init_synonym_words(self):
        if len(self.synonyms):
            return
        for word in Vocabulary.objects.filter(relation_type=const.SYNONYM):
            s_word = word.word.strip()
            m_word = word.parent.word.strip()
            self.synonyms.setdefault(s_word, m_word)

    def add_synonym_word(self, m_word, s_word):
        if m_word and s_word:
            self.synonyms.setdefault(s_word, m_word)

    def get_synonym_word(self, s_word):
        return self.synonyms.get(s_word, '')

    def loading_user_dict(self):
        all_words = Vocabulary.objects.all()
        for word in all_words:
            self.cutter.add_word(word.word.strip())

    def get_stopwords_list(self):
        self._init_stop_words()

        return self.stopwords_list.copy()

    def remove_stopwords(self, words):
        if not self.stopwords_list:
            self._init_stop_words()
        new_words = []
        for word in words:
            word_striped = word.strip()
            if word_striped and word_striped != '\t' and not self.stopwords_list.get(word_striped, None):
                new_words.append(word_striped)
        return new_words

    def is_stop_word(self, word):
        return True and self.stopwords_list.get(word.strip, None)

    def has_synonym_word(self, word: str):
        return self.synonyms.__contains__(word)

    def get_seg_words(self, utterance: str, remove_stopwords=True) -> list:
        striped_utterance = utterance.strip()
        if not striped_utterance:
            return []
        seg_words = self.cutter.cut(striped_utterance, HMM=False)

        if remove_stopwords:
            return self.remove_stopwords(seg_words)

        new_words = []
        for word in seg_words:
            word_striped = word.strip()
            if word_striped:
                new_words.append(word_striped)

        return new_words
