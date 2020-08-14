from django.contrib.admin import StackedInline, ModelAdmin, site, TabularInline
from django.http import HttpResponse
from django.utils import timezone
from import_export import resources
from openpyxl import Workbook

from chatbot.component.table_utils import ExcelReadUtil
from chatbot.const import const
from chatbot.logic.table.detect_column_type import Detector
from chatbot.logic.table.table_data import TableData
from chatbot.models import Knowledge, SimilarQuestion, QuestionAnswer, TableColumn, TableColumnValue, Table, \
    Classification
from chatbot.models import Vocabulary
from chatbot.vocabulary import Word


class ExportExcelMixin(object):
    def export_as_excel(self, request, queryset):
        meta = self.model._meta
        if not self.export_fields:
            self.export_fields = [field.name for field in meta.fields]
        field_names = [field for field in self.export_fields]
        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = f'attachment; filename={meta}.xlsx'
        wb = Workbook()
        ws = wb.active
        ws.append(field_names)
        for obj in queryset:
            data = [f'{getattr(obj, field)}' for field in field_names]
            ws.append(data)
        wb.save(response)
        return response

    export_as_excel.short_description = '导出Excel'


class ClassificationAdmin(ModelAdmin):
    fields = ('name', 'parent')
    list_display = ('name', 'parent', 'creator', 'created_at', 'modifier', 'modified_at')
    list_filter = ('parent', 'name', 'modified_at',)
    search_fields = ('name',)

    def get_fields(self, request, obj=None):
        if not obj:
            return self.fields
        return self.fields + ('creator', 'created_at', 'modifier', 'modified_at')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + ('creator', 'created_at', 'modifier', 'modified_at')
        return self.readonly_fields


class VocabularyInline(StackedInline):
    model = Vocabulary
    extra = 1
    fields = ('word', 'relation_type')

    list_display = ('word',)
    list_filter = ('word',)
    search_fields = ('word',)


class VocabularyAdmin(ModelAdmin):
    fields = ('word', 'word_type', 'word_from', 'weight', 'parent', 'relation_type')
    list_display = (
        'word', 'word_type', 'word_from', 'weight', 'parent', 'relation_type', 'creator', 'created_at', 'modifier',
        'modified_at'
    )
    list_filter = ('relation_type', 'word_from', 'modified_at',)
    search_fields = ('word',)
    autocomplete_fields = ['parent']
    inlines = [VocabularyInline]

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

        word = Word()
        word.cutter.add_word(obj.word.strip())

        if obj.relation_type == const.SYNONYM:
            word.add_synonym_word(obj.parent.word, obj.word)

    def save_related(self, request, form, formsets, change):
        m_word = form.instance
        user = request.user
        word = Word()
        for formset in formsets:
            for f in formset.extra_forms:
                if not f.has_changed():
                    continue
                if formset.can_delete and f.cleaned_data.get('DELETE', False):
                    continue
                obj = f.instance
                obj.creator = user
                obj.modifier = user
                obj.word_type = m_word.word_type
                word.cutter.add_word(obj.word.strip())
                if obj.relation_type == const.SYNONYM:
                    word.add_synonym_word(m_word.word, obj.word.strip())

            for f in formset.initial_forms:
                obj = form.instance
                if obj.pk is None:
                    continue
                if form in formset.deleted_forms:
                    continue

                if form.has_changed():
                    obj = f.instance
                    obj.modifier = user
                    obj.modified_at = timezone.now()
                    obj.word_type = m_word.word_type

        super().save_related(request, form, formsets, change)


class SimilarQuestionAdmin(StackedInline):
    model = SimilarQuestion
    extra = 1
    fields = ('question',)

    list_display = ('question',)
    list_filter = ('question',)
    search_fields = ('question',)


class QuestionAnswerAdmin(StackedInline):
    model = QuestionAnswer
    extra = 1
    fields = ('answer',)
    list_display = ('answer',)
    search_fields = ('answer',)


class KnowledgeAdmin(ModelAdmin, ExportExcelMixin):
    fields = ('title', 'classification')
    list_display = (
        'title', 'classification', 'answer', 'creator', 'created_at', 'modifier', 'modified_at',
        'similar_question_count')
    list_filter = ('classification', 'title', 'modified_at',)
    search_fields = ('title',)
    inlines = [QuestionAnswerAdmin, SimilarQuestionAdmin]
    actions = ['export_as_excel']

    export_fields = ('title', 'classification', 'answer',)

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
    list_display = ('name', 'creator', 'created_at', 'modifier', 'modified_at')
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
            user = request.user
            table = form.instance

            file_type = str(excel_file.name).split('.')[1]
            excel = ExcelReadUtil(excel_file, file_type)

            col_header = excel.get_table_header()
            columns = []
            cutter = Word().cutter
            detector = Detector()

            for index, header in enumerate(col_header):
                column = TableColumn()
                col_type = detector.detect_type_column(header)
                if header.strip():
                    cutter.add_word(header.strip())
                column.save_from_header(header, col_type, user, index + 1, table)
                columns.append(column)

            values = []
            for row_num in range(excel.content_start_row, excel.row_num + 1):
                for col_num in range(1, excel.header_end_col + 1):
                    column_value = TableColumnValue()
                    value = excel.get_cell_value(row_num, col_num)

                    if not value or not value.strip():
                        value = ''
                    else:
                        value = value.strip()
                        value = str(value).replace(' ', '')
                    column_value.value = value
                    column_value.table = table
                    column = columns[col_num - 1]
                    column_value.col = columns[col_num - 1]
                    column_value.row_id = row_num
                    values.append(column_value)
                    if column.searchable and value:
                        word = Vocabulary()
                        word.value_word_save(value.strip(), user, column.word)
                        column_value.word = word
                        cutter.add_word(column_value.value)

            TableColumnValue.objects.bulk_create(values)

        TableData().update_table_data(form.instance.id)
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

site.register(Vocabulary, VocabularyAdmin)
site.register(Classification, ClassificationAdmin)
site.register(Knowledge, KnowledgeAdmin)
site.register(Table, TableAdmin)
site.register(TableColumnValue, TableColumnValueAdmin)
site.register(TableColumn, TableColumnNoInLineAdmin)
