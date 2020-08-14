from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot.models import Statement
from chatterbot.logic import LogicAdapter

from chatbot.logic.ir.search_engine import get_result_from_search_engine
from chatbot.logic.unknown import get_unknown_response
from chatbot.models import SimilarQuestion, Knowledge
from chatbot.settings import logger


def knowledge(args):
    pass


class IRLogicAdapter(LogicAdapter):
    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.all_search_result = None
        self.result_count = 0
        self.best_result = None
        self.query_text = ''

    def can_process(self, statement):
        self.query_text = statement.text.strip()
        if self.query_text:
            self.all_search_result = get_result_from_search_engine(statement.search_text, (Knowledge, SimilarQuestion))
            self.result_count = self.all_search_result.count()
            if not self.result_count:
                return False
            self.best_result = self.all_search_result.best_match()
            if self.best_result.score < 4.00:
                return False
            return True
        else:
            return False

    def process(self, statement: Statement, additional_response_selection_parameters=None):
        response = get_unknown_response(self.query_text)

        model_name = self.best_result.model_name

        for result in self.all_search_result:
            logger.info('pk: {} score: {}'.format(result.object.id, result.score))

        answer = None
        if model_name == 'knowledge':
            # by standard question title
            knowledge_id = self.best_result.object.id
            answer = self.best_result.object.questionanswer_set.filter(knowledge=knowledge_id)

        if model_name == 'similarquestion':
            # by similar question
            kn = self.best_result.object.knowledge
            answer = kn.questionanswer_set.filter(knowledge=kn.id)

        if answer:
            response_text = str(answer[0].answer)
            response = Statement(text=response_text)
            response.confidence = 1.0

        return response
