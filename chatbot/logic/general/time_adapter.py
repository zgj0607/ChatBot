import logging
from datetime import datetime

import jieba
from chatterbot import ChatBot

from chatterbot.conversation import Statement
from chatterbot.logic import TimeLogicAdapter


class TimeAdapter(TimeLogicAdapter):
    """
    The TimeLogicAdapter returns the current time.

    :kwargs:
        * *positive* (``list``) --
          The time-related questions used to identify time questions.
          Defaults to a list of English sentences.
        * *negative* (``list``) --
          The non-time-related questions used to identify time questions.
          Defaults to a list of English sentences.
    """

    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.contain_key_word = (
            'time',
            'now',
            'datetime',
            '时间',
            '几点',
        )

    def can_process(self, statement: Statement):
        cut_words = jieba.cut(statement.text)
        for word in cut_words:
            if word in self.contain_key_word:
                return True
        return False
