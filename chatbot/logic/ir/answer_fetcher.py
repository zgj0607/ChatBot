from chatterbot.ext.django_chatterbot.models import Statement
from haystack.query import SearchQuerySet

from chatbot.models import Knowledge, SimilarQuestion, TableColumnValue, TableColumn
from chatbot.settings import logger


def get_answer_from_search_engine(statement: Statement, models=()) -> Statement:
    query_text = statement.text.strip()
    response = get_unknown_response(query_text)
    if not query_text:
        return get_unknown_response(statement.text)

    try:
        all_corpus = SearchQuerySet().all().filter(content=query_text)
        seg_words = statement.search_text.split()
        for word in seg_words:
            all_corpus = all_corpus.filter_or(content=word)

        if models:
            all_corpus = all_corpus.models(*models)

        result_count = all_corpus.count()

        if Knowledge in models or SimilarQuestion in models:
            if result_count >= 1:
                search_result = all_corpus.best_match()
                model_name = search_result.model_name

                for result in all_corpus:
                    logger.info('pk: {} score: {}'.format(result.object.id, result.score))

                if search_result.score < 5.00:
                    return get_unknown_response(query_text)

                answer = None
                if model_name == 'knowledge':
                    # by standard question title
                    knowledge_id = search_result.object.id
                    answer = search_result.object.questionanswer_set.filter(knowledge=knowledge_id)

                if model_name == 'similarquestion':
                    # by similar question
                    knowledge = search_result.object.knowledge
                    answer = knowledge.questionanswer_set.filter(knowledge=knowledge.id)

                if answer:
                    response_text = str(answer[0].answer)
                    response = Statement(text=response_text)
                    response.confidence = 1.0

        if TableColumn in models or TableColumnValue in models:
            results = {}
            columns = []
            values = []
            for search_result in all_corpus:
                model_name = search_result.model_name
                score = search_result.score
                # if score < 1.00:
                #     continue
                if model_name == 'tablecolumn':
                    column = search_result.object
                    table_id = column.table.id
                    column_id = column.id
                    table = results.get(table_id, {})

                    result = table.get(column_id, {})

                    result['table_id'] = column.table.id
                    result['table'] = column.table
                    result['column_id'] = column.id
                    result['column_name'] = column.name
                    result['is_primary_key'] = column.is_primary_key
                    result['col_type'] = column.col_type
                    result['is_hit'] = True
                    result['hit_num'] = result.get('hit_num', 0) + 1

                    table = results.get(table_id, {})
                    table[column_id] = result
                    results[table_id] = table

                    columns.append((column, search_result.score))

                if model_name == 'tablecolumnvalue':
                    value = search_result.object
                    values.append((value, search_result.score))

                    table_id = value.table.id
                    column_id = value.col.id
                    table = results.get(table_id, {})
                    result = table.get(column_id, {})

                    result['table_id'] = table_id
                    result['table'] = value.table
                    result['column_id'] = column_id
                    result['column_name'] = value.col.name
                    result['is_primary_key'] = value.col.is_primary_key
                    result['col_type'] = value.col.col_type
                    result['value'] = result.get('value', [])
                    if value.value not in result['value']:
                        result['value'].append(value.value)

                    table = results.get(table_id, {})
                    table[column_id] = result
                    results[table_id] = table
            response_text = ''
            for table_id in results.keys():
                table = results.get(table_id)
                all_columns = TableColumn.objects.filter(table__id=table_id)
                condition_row = []
                target_columns = []
                for column_id in table.keys():
                    column = table.get(column_id)
                    value = column.get('value', [])

                    if value:
                        target_value = TableColumnValue.objects.filter(col__id=column_id).filter(value=value[0])
                        temp_row = []
                        for v in target_value:
                            temp_row.append(v.row_id)
                        if not condition_row:
                            condition_row = set(temp_row)
                        else:
                            if temp_row:
                                condition_row = set(temp_row) & set(condition_row)
                    else:
                        target_columns.append(column_id)

                if not target_columns:
                    target_columns = all_columns.values_list(id)

                result_values = TableColumnValue.objects.filter(table__id=table_id).filter(
                    row_id__in=condition_row).filter(col_id__in=target_columns)

                for v in result_values:
                    response_text += "<p><span style='font-weight:bolder;'>{}</span> : {}</p>".format(v.col.name,
                                                                                                      v.value)
                response_text += '<br/>'
            response = Statement(text=response_text)
            response.confidence = 1.0

        logger.info("query_text: {}, answer is: {} ".format(query_text, response.text))
    except Exception as e:
        logger.error(e, exc_info=True)
        response = get_unknown_response(query_text)
    return response


def get_unknown_response(query_text: str) -> Statement:
    response = Statement(text='I will repeat your question: ' + query_text)
    response.confidence = 0
    return response


def get_operation():
    pass
