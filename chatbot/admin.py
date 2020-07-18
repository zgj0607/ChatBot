from django.contrib.admin import StackedInline, ModelAdmin, site, TabularInline
from django.http import HttpRequest
from django.utils import timezone

from chatbot.component.table_utils import ExcelUtil
from chatbot.logic.table.detect_column_type import Detector
from chatbot.models import Knowledge, SimilarQuestion, QuestionAnswer, TableColumn, TableColumnValue, Table
from chatbot.settings import logger
from chatbot.vocabulary import Vocabulary


class SimilarQuestionAdmin(StackedInline):
    model = SimilarQuestion
    extra = 1
    fields = ('question',)

    list_display = ('question',)
    list_filter = ('question',)
    search_fields = ('question',)


class QuestionAnswerAdmin(StackedInline):
    model = QuestionAnswer
    extra = 0
    fields = ('answer',)
    list_display = ('answer',)
    search_fields = ('answer',)


class KnowledgeAdmin(ModelAdmin):
    fields = ('title',)
    list_display = ('title', 'creator', 'created_at', 'modifier', 'modified_at', 'similar_question_count')
    list_filter = ('title', 'modified_at',)
    search_fields = ('title',)
    inlines = [SimilarQuestionAdmin, QuestionAnswerAdmin]

    def get_fields(self, request, obj=None):
        if not obj:
            return self.fields
        return self.fields + ('creator', 'created_at', 'modifier', 'modified_at')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ('creator', 'created_at', 'modifier', 'modified_at')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.modifier = request.user
        obj.modified_at = timezone.now()
        super().save_model(request, obj, form, change)


class TableColumnAdmin(TabularInline):
    model = TableColumn
    extra = 0
    fields = ('seq', 'name', 'col_type', 'clarify_words', 'searchable')
    show_change_link = True


class TableColumnValueInlineAdmin(TabularInline):
    model = TableColumnValue
    extra = 0
    fields = ('row_id', 'value')
    show_change_link = True


class TableAdmin(ModelAdmin):
    fields = ('name', 'file')
    list_display = ('name', 'name', 'creator', 'created_at', 'modifier', 'modified_at')
    list_filter = ('name', 'modified_at',)
    search_fields = ('name',)
    inlines = [TableColumnAdmin]

    def get_fields(self, request, obj=None):
        if not obj:
            return self.fields
        return self.fields + ('creator', 'created_at', 'modifier', 'modified_at')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ('creator', 'created_at', 'modifier', 'modified_at')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.modifier = request.user
        obj.modified_at = timezone.now()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        if request.method == 'POST' and request.FILES:
            excel_file = request.FILES['file']

            file_type = str(excel_file.name).split('.')[1]
            excel = ExcelUtil(excel_file, file_type)

            col_header = excel.get_table_header()
            columns = []
            detector = Detector()

            for index, header in enumerate(col_header):
                column = TableColumn()
                column.name = header
                column.col_type = detector.detect_type_column(header)
                column.clarify_words = '请提供一下' + header
                column.seq = index + 1
                if column.col_type in ('Date', 'Enum', 'Person', 'Integer', 'Price', 'Org', 'City'):
                    column.searchable = True
                column.table = form.instance
                column.save()
                columns.append(column)
            values = []
            for row_num in range(excel.content_start_row, excel.row_num + 1):
                for col_num in range(1, excel.header_end_col + 1):
                    column_value = TableColumnValue()
                    column_value.value = excel.get_cell_value(row_num, col_num)
                    column_value.table = form.instance
                    column_value.col = columns[col_num - 1]
                    column_value.row_id = row_num
                    values.append(column_value)

            TableColumnValue.objects.bulk_create(values)
            vocabulary = Vocabulary()
            with open(vocabulary.get_user_dict_file(), 'a') as user_dict_file:
                for header in col_header:
                    user_dict_file.write(header + '\n')
                for v in values:
                    if v.col.searchable:
                        user_dict_file.write(v.value + '\n')
                vocabulary.loading_user_dict()

        super().save_related(request, form, formsets, change)


class TableColumnValueAdmin(ModelAdmin):
    fields = ('table', 'col', 'row_id', 'value')
    list_display = ('table', 'col', 'row_id', 'value')
    list_filter = ('table', 'col', 'row_id')
    search_fields = ('table', 'col', 'value')
    list_display_links = ('value',)


class TableColumnNoInLineAdmin(ModelAdmin):
    fields = ('table', 'seq', 'name', 'col_type', 'clarify_words', 'searchable', 'is_primary_key')
    list_display = ('table', 'seq', 'name', 'col_type', 'clarify_words', 'searchable', 'is_primary_key')
    list_filter = ['table', 'searchable']
    search_fields = ('table', 'name')
    list_display_links = ('name',)
    inlines = [TableColumnValueInlineAdmin]


site.site_header = 'ChatBot Administration'

site.register(Knowledge, KnowledgeAdmin)
site.register(Table, TableAdmin)
site.register(TableColumnValue, TableColumnValueAdmin)
site.register(TableColumn, TableColumnNoInLineAdmin)
