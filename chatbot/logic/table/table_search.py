from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot.models import Statement
from chatterbot.logic import LogicAdapter
from haystack.query import SearchQuerySet

from chatbot.const import const
from chatbot.logic.ir.search_engine import get_result_from_search_engine
from chatbot.logic.table.detect_column_type import Detector
from chatbot.logic.table.table_data import TableData
from chatbot.logic.unknown import get_unknown_response
from chatbot.models import TableColumnValue, TableColumn
from chatbot.settings import logger


class TableLogicAdapter(LogicAdapter):
    def __init__(self, chatbot: ChatBot, **kwargs):
        super().__init__(chatbot, **kwargs)
        self.response = Statement()
        self.table_data = TableData().tables
        self.seg_words = []
        self.results = {}

    def can_process(self, statement):
        query_text = statement.text.strip()

        if str(query_text).startswith('img'):
            return False

        self.seg_words = statement.search_text.split(const.SEG_SEPARATOR)

        if query_text:
            all_corpus = get_result_from_search_engine(statement.search_text, (TableColumnValue, TableColumn))

            self.merge_columns(all_corpus)

            # 获取比较信息，如A比B大多少
            operation = Detector().detect_operation(statement)
            response_text = ''

            for table_id in self.results.keys():
                table = self.results.get(table_id)
                all_columns = self.table_data[table_id]['columns']
                column_values = self.table_data[table_id]['values']
                condition_row = []
                target_columns = []
                for column_id in table.keys():
                    column = table.get(column_id)
                    column_name = column['column_name']
                    value = column.get('value', [])

                    if value:
                        for v in value:
                            target_value = column_values[column_values[column['column_name']] == v]
                            condition_row.append(
                                {
                                    'column_name': column_name,
                                    'value': v,
                                    v: target_value
                                }
                            )
                    else:
                        target_columns.append(column_name)

                if not target_columns:
                    target_columns = list(all_columns.keys())

                condition_len = len(condition_row)
                target_len = len(target_columns)

                if not len(operation):
                    col = target_columns[0]
                    for row in condition_row:
                        index_value = row['value']
                        value = row[index_value]

                        target_value = value[col].values

                        for v in target_value:
                            response_text += "<p><span style='font-weight:bolder;'>{}</span> : {}</p>".format(
                                index_value,
                                v)
                else:
                    op = operation['op']
                    slot_type = operation['slot_type']
                    op_word = operation['word']
                    unit = operation['unit']
                    import re

                    if condition_len == 2 and condition_row[0]['column_name'] == condition_row[1]['column_name']:
                        if op in ('GT', 'LT'):
                            # 处理A比B长多少的比较，同属性的比较
                            for col in target_columns:
                                column = all_columns[col]
                                if column.col_type != slot_type:
                                    continue

                                greater = condition_row[0]
                                less = condition_row[1]

                                greater_index = greater['value']
                                less_index = less['value']

                                # 用正则方式提取值中的小数
                                greater_value = float(
                                    re.search(r'(\d+(\.\d+)?)', greater[greater_index][col].values[0]).group())
                                less_value = float(
                                    re.search(r'(\d+(\.\d+)?)', less[less_index][col].values[0]).group())

                                # 计算比较的两个值谁大谁小，保证greater大于less
                                if greater_value < less_value:
                                    greater_index, less_index = less_index, greater_index
                                    greater_value, less_value = less_value, greater_value

                                # 生成话术
                                response_text += '{} 比 {} {}：{} {}'.format(greater_index, less_index, op_word,
                                                                           round(greater_value - less_value, 2), unit)

                    if condition_len == 1 and target_len == 1 or \
                            condition_len == 2 and condition_row[0]['column_name'] != condition_row[1]['column_name']:
                        # 处理比A长的有多少、比A长的B的C有多少
                        target_col = target_columns[0]
                        first_index_value = condition_row[0]['value']

                        first_row = condition_row[0][first_index_value]
                        first_col = condition_row[0]['column_name']

                        condition_index_value = first_index_value
                        more_condition_col = first_col
                        more_condition_value = first_index_value

                        row = first_row
                        if condition_len == 2:
                            second_index_value = condition_row[1]['value']
                            second_row = condition_row[1][second_index_value]
                            second_col = condition_row[1]['column_name']

                            if len(first_row) > len(second_row):
                                row = second_row
                                condition_index_value = second_index_value
                                more_condition_col = first_col
                                more_condition_value = first_index_value
                            else:
                                more_condition_col = second_col
                                more_condition_value = second_index_value

                        operation_value = row[target_col].values[0]

                        normalization = round(float(re.search(r'(\d+(\.\d+)?)', operation_value).group()), 2)

                        if op == 'LT':
                            condition = column_values[target_col].map(
                                lambda x: round(float(re.search(r'(\d+(\.\d+)?)', x).group()), 2) < normalization)
                        else:
                            condition = column_values[target_col].map(
                                lambda x: round(float(re.search(r'(\d+(\.\d+)?)', x).group()), 2) > normalization)

                        if condition_len == 1:
                            target_values = column_values[condition]
                        else:
                            temp_values = column_values[condition]
                            target_values = temp_values[temp_values[more_condition_col] == more_condition_value]

                        response_text += "<p>{}的{}是{}</p>".format(
                            condition_index_value, target_col, operation_value)

                        response_text += "<p>总计有 : {} 条</p>".format(
                            len(target_values))

                        if not len(target_values):
                            continue

                        response_text += '''<table class="layui-table">'''
                        response_text += '<thead><tr>'

                        final_col = []

                        for col in all_columns.keys():
                            if all_columns[col].is_primary_key:
                                final_col.append(col)
                                break
                        final_col.append(target_col)

                        for col in final_col:
                            response_text += '<th>{}</th>'.format(col)

                        response_text += '</tr></thead>'
                        response_text += '<tbody>'

                        for idx in target_values.index:
                            response_text += '<tr>'
                            for col in final_col:
                                response_text += '<td>{}</td>'.format(target_values.loc[idx][col])
                            response_text += '</tr>'
                        response_text += '</tbody></table>'

                if response_text:
                    self.response = Statement(text=response_text)
                    self.response.confidence = 1.0
                else:
                    self.response = get_unknown_response(query_text)

                logger.info("query_text: {}, answer is: {} ".format(query_text, self.response.text))

                if self.response.confidence:
                    return True

            return False

    def process(self, statement: Statement, additional_response_selection_parameters=None):
        return self.response

    def merge_columns(self, qs: SearchQuerySet):
        self.results = {}
        for search_result in qs:
            model_name = search_result.model_name
            score = search_result.score
            if score < 5.00:
                break

            if model_name == 'tablecolumn':
                column = search_result.object

                column_name = column.name

                # 控制列的精确匹配
                if column_name not in self.seg_words:
                    continue

                table_id = column.table.id
                column_id = column.id

                table = self.results.get(table_id, {})
                result = table.get(column_id, {})

                result['column_id'] = column.id
                result['column_name'] = column_name
                result['is_hit'] = True
                result['hit_num'] = result.get('hit_num', 0) + 1

            else:
                # TableColumnValue
                value = search_result.object

                # 控制值的精确匹配
                if value.value not in self.seg_words:
                    continue

                table_id = value.table.id
                column_id = value.col.id

                table = self.results.get(table_id, {})
                result = table.get(column_id, {})

                result['column_id'] = column_id
                result['column_name'] = value.col.name

                result['value'] = result.get('value', [])

                if value.value not in result['value']:
                    result['value'].append(value.value)

            table[column_id] = result
            self.results[table_id] = table
