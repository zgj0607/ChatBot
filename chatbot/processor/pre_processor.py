from chatterbot.ext.django_chatterbot.models import Statement

from chatbot.const import const
from chatbot.vocabulary import Word


def tokenizer(statement: Statement):
    """
    tokenize statement text into statement search_text
    """

    vocabulary = Word()
    # tokenize the query text
    seg_words_with_stopwords = vocabulary.get_seg_words(statement.text, False)

    seg_words_without_stopwords = vocabulary.remove_stopwords(seg_words_with_stopwords)

    # serialize it by space and  fill into search_text and search_in_response_to
    statement.search_in_response_to = const.SEG_SEPARATOR.join(seg_words_with_stopwords)

    search_text = const.SEG_SEPARATOR.join(seg_words_without_stopwords)

    # add segment word and synonym word after query
    for w in seg_words_with_stopwords:
        synonym_word = vocabulary.get_synonym_word(w)
        if synonym_word:
            search_text += const.SEG_SEPARATOR
            search_text += synonym_word

    statement.search_text = statement.text + const.SEG_SEPARATOR + search_text

    return statement
