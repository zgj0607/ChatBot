from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db.models import Model, CharField, DateTimeField, ForeignKey, IntegerField, CASCADE, FileField, \
    FilePathField, TextField, BooleanField
from django.utils import timezone

from chatbot.const import SLOT_TYPE


class Knowledge(Model):
    title = CharField('标准问', max_length=200, unique=True)
    created_at = DateTimeField(default=timezone.now, verbose_name='创建时间')
    creator = ForeignKey(User, on_delete=CASCADE, related_name='knowledge_creator', null=True,
                         blank=False, verbose_name='创建者')
    modified_at = DateTimeField(default=timezone.now, verbose_name='最近修改时间')
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='knowledge_modifier', null=True,
                          verbose_name='修改人')

    def similar_question_count(self):
        self.similarquestion_set.filter(knowledge=self.id)
        return self.similarquestion_set.count()

    similar_question_count.short_description = '相似问数量'

    class Meta:
        ordering = ['-modified_at', 'title']
        db_table = 'chatbot_knowledge'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'

    def __str__(self):
        return self.title


class SimilarQuestion(Model):
    question = CharField('Q', max_length=200, unique=True)
    knowledge = ForeignKey(Knowledge, on_delete=CASCADE)
    created_at = DateTimeField(default=timezone.now)
    creator = ForeignKey(User, on_delete=CASCADE, related_name='similar_question_creator', null=True)
    modified_at = DateTimeField(default=timezone.now)
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='similar_question_modifier',
                          null=True)

    class Meta:
        ordering = ['-modified_at', 'question']
        db_table = 'chatbot_similar_question'
        verbose_name = '相似问'
        verbose_name_plural = '相似问'

    def __str__(self):
        return self.question


class QuestionAnswer(Model):
    answer = RichTextUploadingField('A', max_length=20000)

    knowledge = ForeignKey(Knowledge, on_delete=CASCADE)
    creator = ForeignKey(User, on_delete=CASCADE, related_name='question_answer_creator', null=True)
    created_at = DateTimeField(default=timezone.now)
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='question_answer_modifier', null=True)
    modified_at = DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-modified_at']
        db_table = 'chatbot_question_answer'
        verbose_name = '答案'
        verbose_name_plural = '答案'


class Table(Model):
    name = CharField('表格名称', max_length=200, unique=True)
    file = FileField('文件', upload_to='upload/%Y/%m/%d/', max_length=200, null=False, blank=False)
    creator = ForeignKey(User, on_delete=CASCADE, related_name='table_creator', null=True)
    created_at = DateTimeField(default=timezone.now)
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='table_modifier', null=True)
    modified_at = DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-modified_at', 'name']
        verbose_name = '表格'
        verbose_name_plural = '表格'
        db_table = 'chatbot_kg_table'

    def __str__(self):
        return self.name


class TableColumn(Model):
    name = CharField('属性名称', max_length=400)
    table = ForeignKey(Table, on_delete=CASCADE, related_name='table_of_column', verbose_name='表格名称')
    seq = IntegerField('属性序号')
    col_type = CharField('属性类型', choices=SLOT_TYPE, default='Text', max_length=100)
    searchable = BooleanField('是否检索', default=False)
    clarify_words = CharField('反问话术', max_length=200)
    is_primary_key = BooleanField('是否主键', default=False)

    class Meta:
        unique_together = [['table', 'name']]
        ordering = ['seq']
        verbose_name = '表格属性'
        verbose_name_plural = '表格属性'
        db_table = 'chatbot_kg_table_column'

    def __str__(self):
        return self.name


class TableColumnValue(Model):
    value = TextField('值', max_length=20000, null=True, blank=True)
    table = ForeignKey(Table, on_delete=CASCADE, related_name='value_of_table', verbose_name='表格名称')
    col = ForeignKey(TableColumn, on_delete=CASCADE, related_name='value_of_column', verbose_name='属性名称')
    row_id = IntegerField('行序号')

    class Meta:
        unique_together = [['col', 'row_id']]
        ordering = ['table', 'row_id', 'col', 'value']
        verbose_name = '表格属性值'
        verbose_name_plural = '表格属性值'
        db_table = 'chatbot_kg_table_column_value'
