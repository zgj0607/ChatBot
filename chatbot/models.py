from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db.models import Model, CharField, DateTimeField, ForeignKey, IntegerField, CASCADE, FileField, \
    TextField, BooleanField, PROTECT
from django.utils import timezone

from chatbot.const import const


class Classification(Model):
    name = CharField('分类名称', max_length=100, unique=True)

    parent = ForeignKey('self', verbose_name='所属父级', related_name='parent_classification', on_delete=CASCADE, null=True,
                        blank=True)

    created_at = DateTimeField(default=timezone.now, verbose_name='创建时间')
    creator = ForeignKey(User, on_delete=CASCADE, related_name='classification_creator', null=True,
                         blank=False, verbose_name='创建者')
    modified_at = DateTimeField(default=timezone.now, verbose_name='最近修改时间')
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='classification_modifier', null=True,
                          verbose_name='修改人')

    class Meta:
        ordering = ['-modified_at', 'name']
        verbose_name = '知识分类'
        verbose_name_plural = '知识分类'

    def __str__(self):
        return self.name


class Vocabulary(Model):
    word = CharField('词', max_length=1000)
    word_type = CharField('词类型', choices=const.WORD_TYPE, default=const.NORMAL_WORD, max_length=100)
    word_from = CharField('来源', choices=const.WORD_FROM, default=const.CUSTOMER_ADD, max_length=100)
    weight = IntegerField('权重', default=70)
    parent = ForeignKey('self', verbose_name='所属主词', related_name='parent_word', on_delete=CASCADE, null=True,
                        blank=True)
    relation_type = CharField('关联类型', choices=const.WORD_RELATION_TYPE, max_length=100, null=True,
                              blank=True)
    creator = ForeignKey(User, verbose_name='创建者', on_delete=CASCADE, related_name='word_creator', null=True)
    created_at = DateTimeField(default=timezone.now, verbose_name='创建时间')
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='word_modifier', null=True, verbose_name='修改人')
    modified_at = DateTimeField(default=timezone.now, verbose_name='最近修改时间')

    def column_word_save(self, word, user):
        self.word_from = const.PROPERTY
        self._set_default_value(word, user)
        self._is_exists_in_db(word)

    def entity_word_save(self, word, user):
        self.word_from = const.ENTITY
        self._set_default_value(word, user)
        self._is_exists_in_db(word)

    def value_word_save(self, word, user, parent):

        self.word_from = const.VALUE
        self.word_type = const.HYPONYM
        self.parent = parent
        self._set_default_value(word, user)
        self._is_exists_in_db(word)

    def _is_exists_in_db(self, word):
        db_words = Vocabulary.objects.filter(word=word)
        if db_words:
            self.id = db_words[0].id
        else:
            super().save()

    def _set_default_value(self, word, user):
        self.word = word
        self.creator = user
        self.modifier = user

    class Meta:
        unique_together = [['word', 'word_type']]
        ordering = ['word_type', 'word', ]
        verbose_name = '语义库'
        verbose_name_plural = '语义库'
        db_table = 'chatbot_vocabulary'

    def __str__(self):
        return self.word


class Knowledge(Model):
    title = CharField('标准问', max_length=200, unique=True)

    classification = ForeignKey(Classification, on_delete=CASCADE, related_name='knowledge_classification', null=True,
                                blank=False, verbose_name='所属分类')

    created_at = DateTimeField(default=timezone.now, verbose_name='创建时间')
    creator = ForeignKey(User, verbose_name='创建者', on_delete=CASCADE, related_name='knowledge_creator', null=True,
                         blank=False)
    modified_at = DateTimeField(default=timezone.now, verbose_name='最近修改时间')
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='knowledge_modifier', null=True,
                          verbose_name='修改人')

    def similar_question_count(self):
        self.similarquestion_set.filter(knowledge=self.id)
        return self.similarquestion_set.count()

    similar_question_count.short_description = '相似问数量'

    @property
    def answer(self):
        answers = self.questionanswer_set.all()
        if answers:
            return answers[0].answer
        return ""

    # answer.short_description = '答案'

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
    created_at = DateTimeField(default=timezone.now, verbose_name='创建时间')
    creator = ForeignKey(User, verbose_name='创建者', on_delete=CASCADE, related_name='similar_question_creator',
                         null=True)
    modified_at = DateTimeField(default=timezone.now, verbose_name='最近修改时间')
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='similar_question_modifier',
                          null=True, verbose_name='修改人')

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
    creator = ForeignKey(User, verbose_name='创建者', on_delete=CASCADE, related_name='question_answer_creator', null=True)
    created_at = DateTimeField(default=timezone.now, verbose_name='创建时间')
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='question_answer_modifier', null=True,
                          verbose_name='修改人')
    modified_at = DateTimeField(default=timezone.now, verbose_name='最近修改时间')

    class Meta:
        ordering = ['-modified_at']
        db_table = 'chatbot_question_answer'
        verbose_name = '答案'
        verbose_name_plural = '答案'


class Table(Model):
    name = CharField('表格名称', max_length=200, unique=True)
    file = FileField('文件', upload_to='upload/%Y/%m/%d/', max_length=200, null=False, blank=False)
    creator = ForeignKey(User, verbose_name='创建者', on_delete=CASCADE, related_name='table_creator', null=True)
    state = CharField('状态', choices=const.STATE, default=const.ACTIVE, max_length=100)
    created_at = DateTimeField(default=timezone.now, verbose_name='创建时间')
    modifier = ForeignKey(User, on_delete=CASCADE, related_name='table_modifier', null=True, verbose_name='修改人')
    modified_at = DateTimeField(default=timezone.now, verbose_name='最近修改时间')

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
    col_type = CharField('属性类型', choices=const.SLOT_TYPE, default=const.TEXT, max_length=100)
    searchable = BooleanField('是否检索', default=False)
    clarify_words = CharField('反问话术', max_length=200)
    is_primary_key = BooleanField('是否主键', default=False)
    word = ForeignKey(Vocabulary, related_name='column_vocabulary', on_delete=PROTECT, null=True)

    class Meta:
        unique_together = [['table', 'name']]
        ordering = ['seq']
        verbose_name = '表格属性'
        verbose_name_plural = '表格属性'
        db_table = 'chatbot_kg_table_column'

    def __str__(self):
        return self.name

    def save_from_header(self, header, col_type, user, index, table):
        self.name = header
        self.col_type = col_type
        self.clarify_words = '请提供一下' + header
        self.seq = index
        if index == 1:
            self.is_primary_key = True
            self.searchable = True
        if self.col_type in (
                const.DATE, const.ENUM, const.PERSON, const.INTEGER, const.PRICE, const.ORG, const.CITY,
                const.BRAND
        ):
            self.searchable = True
        self.table = table
        word = Vocabulary()
        word.column_word_save(header, user)
        self.word = word
        super().save()


class TableColumnValue(Model):
    value = TextField('值', max_length=20000, null=True, blank=True)
    table = ForeignKey(Table, on_delete=CASCADE, related_name='value_of_table', verbose_name='表格名称')
    col = ForeignKey(TableColumn, on_delete=CASCADE, related_name='value_of_column', verbose_name='属性名称')
    row_id = IntegerField('行序号')
    word = ForeignKey(Vocabulary, related_name='value_vocabulary', on_delete=PROTECT, null=True, blank=True)

    class Meta:
        unique_together = [['col', 'row_id']]
        ordering = ['table', 'row_id', 'col', 'value']
        verbose_name = '表格属性值'
        verbose_name_plural = '表格属性值'
        db_table = 'chatbot_kg_table_column_value'

    def __str__(self):
        if self.value:
            return self.value
        else:
            return str(self.id)

    def save_from_value(self, value, user, row_num, table, column):
        self.value = value
        self.table = table
        self.col = column
        self.row_id = row_num
        if value:
            word = Vocabulary()
            word.column_word_save(value, user)
            self.word = word
        super().save()
