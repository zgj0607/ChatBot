from __future__ import absolute_import
from xadmin.sites import register
from django.utils import timezone
from xadmin.views import CommAdminView, BaseAdminView
from chatbot.models import Knowledge, SimilarQuestion, QuestionAnswer
from xadmin.plugins.batch import BatchChangeAction


@register(BaseAdminView)
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


@register(CommAdminView)
class GlobalSetting(object):
    menu_style = 'default'  # 'accordion'


class SimilarQuestionAdmin(object):
    model = SimilarQuestion
    extra = 1
    style = "accordion"
    fields = ('question',)

    list_display = ('question',)
    list_filter = ('question',)
    search_fields = ('question',)


class QuestionAnswerAdmin(object):
    model = QuestionAnswer
    extra = 1
    style = "accordion"
    fields = ('answer',)
    list_display = ('answer',)
    list_filter = ('answer',)
    search_fields = ('answer',)


@register(Knowledge)
class KnowledgeAdmin(object):
    fields = ('title',)
    readonly_fields = ('creator', 'created_at', 'modifier', 'modified_at')
    list_display = ('title', 'creator', 'created_at', 'modifier', 'modified_at')
    list_filter = ('title', 'modified_at',)
    search_fields = ('title',)
    inlines = [SimilarQuestionAdmin, QuestionAnswerAdmin]
    actions = [BatchChangeAction, ]

    # def get_fields(self, request, obj=None):
    #     if not obj:
    #         return self.fields
    #     return self.fields + ('creator', 'created_at', 'modifier', 'modified_at')

    # def get_readonly_fields(self, obj=None):
    #     if obj is not None:
    #         return self.readonly_fields + ('creator', 'created_at', 'modifier', 'modified_at')
    #     return self.readonly_fields

    def instance_forms(self):
        super().instance_forms()
        user = self.request.user
        # 判断是否为新建操作，新建操作才会设置creator的默认值
        if not self.form_obj:
            self.form_obj.instance.creator = self.request.user
            self.form_obj.instance.creator_id = user.id

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.modifier = request.user
        obj.modified_at = timezone.now()
        super().save_model(request, obj, form, change)
