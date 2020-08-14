from chatterbot import ChatBot
from chatterbot.logic import LogicAdapter

from chatbot.logic.ir.search_engine import get_result_from_search_engine
from chatbot.models import SimilarQuestion, Knowledge
from chatbot.vocabulary import Word


class WeatherLogicAdapter(LogicAdapter):
    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.vocabulary = Word()

    def can_process(self, statement):
        return True

    def process(self, statement, additional_response_selection_parameters=None):
        return get_result_from_search_engine(statement, (Knowledge, SimilarQuestion))
