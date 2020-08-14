from haystack.query import SearchQuerySet

from chatbot.const import const
from chatbot.settings import logger


def get_result_from_search_engine(query_text, models=()) -> SearchQuerySet:
    if not query_text or not query_text.strip():
        return SearchQuerySet().none()

    try:
        all_corpus = SearchQuerySet().all()
        seg_words = query_text.split(const.SEG_SEPARATOR)
        for word in seg_words:
            all_corpus = all_corpus.filter_or(content=word)

        if models:
            all_corpus = all_corpus.models(*models)
        return all_corpus

    except Exception as e:
        logger.error(e, exc_info=True)
        return SearchQuerySet().none()
