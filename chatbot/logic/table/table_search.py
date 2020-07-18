from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot.models import Statement
from chatterbot.logic import LogicAdapter

from chatbot.logic.ir.answer_fetcher import get_unknown_response, \
    get_answer_from_search_engine
from chatbot.models import SimilarQuestion, Knowledge, TableColumnValue, TableColumn


class TableLogicAdapter(LogicAdapter):
    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)

        self.response = Statement()

    def can_process(self, statement):
        query_text = statement.text.strip()
        if query_text:
            self.response = get_answer_from_search_engine(statement, (TableColumn, TableColumnValue))

            if self.response.confidence:
                return True
        return False

    def process(self, statement: Statement, additional_response_selection_parameters=None):
        return self.response
