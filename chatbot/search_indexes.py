from chatterbot.ext.django_chatterbot.models import Statement
from haystack import indexes

from chatbot.models import Knowledge, SimilarQuestion, TableColumn, TableColumnValue


class KnowledgeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return Knowledge

    def index_queryset(self, using=None):
        return self.get_model().objects.all().filter(title__isnull=False)


class SimilarQuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    question = indexes.CharField(model_attr='question')

    def get_model(self):
        return SimilarQuestion

    def index_queryset(self, using=None):
        return self.get_model().objects.all().filter(question__isnull=False)


class TableColumnIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')

    def get_model(self):
        return TableColumn

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class TableColumnValueIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    value = indexes.CharField(model_attr='value')
    row_id = indexes.IntegerField(model_attr='row_id', stored=True)

    def get_model(self):
        return TableColumnValue

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(col__searchable=True)
