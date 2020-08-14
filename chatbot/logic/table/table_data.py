from collections import OrderedDict

from chatbot.component.singleton import singleton
from chatbot.models import Table, TableColumn, TableColumnValue
import pandas as pd


@singleton
class TableData(object):
    def __init__(self):
        self.tables = {}
        self.update_table_data()

    def update_table_data(self, table_id=None):

        if not table_id:
            tables = Table.objects.filter(state='Active')
        else:
            tables = Table.objects.filter(id=table_id).filter(state='Active')

        for table in tables:
            table_id = table.id
            table_columns = TableColumn.objects.filter(table__id=table_id)
            columns = OrderedDict()
            index = []
            values = {}
            for column in table_columns:
                column_id = column.id
                column_name = column.name
                columns[column_name] = column

                table_column_values = TableColumnValue.objects.filter(col__id=column_id).order_by('row_id')
                cells = []
                for v in table_column_values:
                    cells.append(v.value)

                values[column_name] = cells
                if column.is_primary_key:
                    index = cells
            if index:
                self.tables[table_id] = {'values': pd.DataFrame(values, index=index),
                                         'columns': columns,
                                         'table': table
                                         }
            else:
                self.tables[table_id] = {'values': pd.DataFrame(values),
                                         'columns': columns,
                                         'table': table
                                         }
