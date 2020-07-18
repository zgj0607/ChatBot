from chatterbot.ext.django_chatterbot.models import Statement

from chatbot.vocabulary import Vocabulary


def tokenizer(statement: Statement):
    """
    tokenize statement text into statement search_text
    """

    vocabulary = Vocabulary()
    # tokenize the query text
    seg_words_with_stopwords = vocabulary.get_seg_words(statement.text, False)

    seg_words_without_stopwords = vocabulary.remove_stopwords(seg_words_with_stopwords)

    # serialize it by space and  fill into search_text and search_in_response_to
    statement.search_in_response_to = ' '.join(seg_words_with_stopwords)
    statement.search_text = ' '.join(seg_words_without_stopwords)

    return statement
