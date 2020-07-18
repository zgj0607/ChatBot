from chatterbot import ChatBot
from chatterbot.logic import LogicAdapter

from chatbot.logic.ir.answer_fetcher import get_answer_from_search_engine
from chatbot.models import SimilarQuestion, Knowledge
from chatbot.vocabulary import Vocabulary


class WeatherLogicAdapter(LogicAdapter):
    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.vocabulary = Vocabulary()

    def can_process(self, statement):
        return True

    def process(self, statement, additional_response_selection_parameters=None):
        return get_answer_from_search_engine(statement, (Knowledge, SimilarQuestion))
