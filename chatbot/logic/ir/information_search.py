from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot.models import Statement
from chatterbot.logic import LogicAdapter

from chatbot.logic.ir.answer_fetcher import get_unknown_response, \
    get_answer_from_search_engine
from chatbot.models import SimilarQuestion, Knowledge


def knowledge(args):
    pass


class IRLogicAdapter(LogicAdapter):
    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        return True

    def process(self, statement: Statement, additional_response_selection_parameters=None):
        query_text = statement.text.strip()
        if query_text:
            return get_answer_from_search_engine(statement, (Knowledge, SimilarQuestion))
        return get_unknown_response(query_text)
