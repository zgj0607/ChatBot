import os

import jieba

from chatbot.component.singleton import singleton
from chatbot.settings import CHATTERBOT


@singleton
class Vocabulary(object):
    def __init__(self):
        self.stopwords_list = {}
        self.vocabulary_path = CHATTERBOT['vocabulary_path']
        self.cutter = jieba
        self.loading_user_dict()

    def _init_stop_words(self):
        if len(self.stopwords_list):
            return
        for line in open(self.vocabulary_path + '/StopWords.txt', 'r', encoding='utf-8').readlines():
            word = line.strip()
            if word:
                self.stopwords_list.setdefault(word, word)

    def loading_user_dict(self):
        file_path = self.vocabulary_path + '/UserWords.txt'
        if not os.path.exists(file_path):
            return
        with open(file_path, 'r', encoding='utf-8') as user_dict_file:
            self.cutter.load_userdict(user_dict_file)
        self.cutter.initialize()

    def get_user_dict_file(self):
        user_dict_file = self.vocabulary_path + '/UserWords.txt'
        if not os.path.exists(user_dict_file):
            with open(user_dict_file, 'w') as fin:
                pass
        return user_dict_file

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
