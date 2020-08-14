from chatterbot.conversation import Statement


def get_unknown_response(query_text: str) -> Statement:
    response = Statement(text='I will repeat your question: ' + query_text)
    response.confidence = 0
    return response
