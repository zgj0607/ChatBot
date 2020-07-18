from chatbot.vocabulary import Vocabulary


class Detector(object):
    def __init__(self):
        self.vocabulary = Vocabulary()
        self.enum_type_key_word = ('类型', '等级', '方式', '分类', '模式', 'type', 'class')
        self.text_type_key_word = ('简介', '描述', '简称', '备注', '说明',)
        self.date_type_key_word = ('日期', '时间', '日', '年', '月',)
        self.person_type_key_word = ('创办人', '负责人', '经理', '经手人', '经办人')
        self.org_type_key_word = ('托管方', '保管方',)

    def detect_type_column(self, col_name) -> str:
        seg_words = self.vocabulary.get_seg_words(col_name)

        last_word = str(seg_words[-1]).lower()

        if last_word in self.enum_type_key_word:
            return 'Enum'

        if last_word in self.date_type_key_word:
            return 'Date'

        if last_word in self.person_type_key_word:
            return 'Person'

        if last_word in self.org_type_key_word:
            return 'Org'

        return 'Text'
