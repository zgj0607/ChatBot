from chatbot.component.singleton import singleton


@singleton
class Const(object):
    def __init__(self):
        print(111)
        self.SLOT_TYPE = (
            ('Integer', '数值'),
            ('Float', '小数'),
            ('Text', '文本'),
            ('Enum', '枚举'),
            ('Date', '日期'),
            ('DateTime', '日期时间'),
            ('Time', '时间'),
            ('TimeInterval', '时间区间'),
            ('URL', '地址'),
            ('Price', '价格'),
            ('Country', '国家'),
            ('City', '城市'),
            ('Person', '人名'),
            ('Org', '机构名'),
            ('AirPort', '机场'),
            ('Phone', '电话号码'),
            ('Software', '软件'),
            ('Unit', '单位'),
            ('Brand', '品牌'),
            ('Length', '长度'),
            ('Mass', '重量'),
            ('Volume', '体积/容积'),
            ('Temperature', '温度'),
            ('Area', '面积'),

        )
        self.INTEGER = 'Integer'
        self.FLOAT = 'Float'
        self.TEXT = 'Text'
        self.ENUM = 'Enum'
        self.DATE = 'Date'
        self.DATE_TIME = 'DateTime'
        self.TIME = 'Time'
        self.TIME_INTERVAL = 'TimeInterval'
        self.U_R_L = 'URL'
        self.PRICE = 'Price'
        self.COUNTRY = 'Country'
        self.CITY = 'City'
        self.PERSON = 'Person'
        self.ORG = 'Org'
        self.AIR_PORT = 'AirPort'
        self.PHONE = 'Phone'
        self.SOFTWARE = 'Software'
        self.UNIT = 'Unit'
        self.BRAND = 'Brand'
        self.LENGTH = 'Length'
        self.MASS = 'Mass'
        self.VOLUME = 'Volume'
        self.TEMPERATURE = 'Temperature'
        self.AREA = 'Area'
        print(222)
        self.WORD_TYPE = (
            ('NormalWord', '普通词'),
            ('BannedWord', '敏感词'),
            ('StopWord', '停止词'),
        )
        self.NORMAL_WORD = 'NormalWord'
        self.BANNED_WORD = 'BannedWord'
        self.STOP_WORD = 'StopWord'

        self.WORD_FROM = (
            ('CustomerAdd', '自定义添加'),
            ('Entity', '实体'),
            ('Property', '属性'),
            ('Value', '值'),
        )
        self.CUSTOMER_ADD = 'CustomerAdd'
        self.ENTITY = 'Entity'
        self.PROPERTY = 'Property'
        self.VALUE = 'Value'

        self.WORD_RELATION_TYPE = (
            ('Synonym', '同义词'),
            ('Hyponym', '下位词'),
            ('Similarity', '关联词'),
        )

        self.SYNONYM = 'Synonym'
        self.HYPONYM = 'Hyponym'
        self.SIMILARITY = 'Similarity'

        self.COMPARISON_PATTERN = {
            'GT': (('比(.+?)贵', 'Price', '贵', '元'),
                   ('比(.+?)高', 'Length', '高', 'mm'),
                   ('比(.+?)重', 'Mass', '大', 'g'),
                   ('比(.+?)大', 'Volume', '大', '平米'),
                   ('比(.+?)长', 'Length', '长', 'mm'),
                   ('比(.+?)宽', 'Length', '宽', 'mm'),
                   ),
            'LT': (('比(.+?)便宜', 'Price', '便宜', '元'),
                   ('比(.+?)矮', 'Length', '矮', 'mm'),
                   ('比(.+?)轻', 'Mass', '轻', 'g'),
                   ('比(.+?)小', 'Volume', '小', '平米'),
                   ('比(.+?)短', 'Length', '短', 'mm'),
                   ('比(.+?)窄', 'Length', '窄', 'mm'),
                   ),
            'AROUND': (('在(.+?)之间', 'Length', '', ''),
                       ('在(.+?)上下', 'Length', '', ''),
                       ('在(.+?)左右', 'Length', '', ''),
                       ),

        }

        self.STATE = (
            ("Active", "生效中"),
            ("Deactivated", "已失效"),
            ("Debugging", "调试中"),
            ("Training", "训练中"),
        )
        self.ACTIVE = 'Active'
        self.DEACTIVATED = 'Deactivated'
        self.DEBUGGING = 'Debugging'
        self.TRAINING = 'Training'

        self.OPERATION = (
            'LT', 'GT', 'LTE', 'GTE', 'BETWEEN', 'AROUND',
        )
        self.LESS_THEN = 'LT'
        self.GREATER_THEN = 'GT'
        self.LESS_THEN_OR_EQUAL = 'LTE'
        self.GREATER_THEN_OR_EQUAL = 'GTE'
        self.AROUND = 'AROUND'

        self.SUMMARY = 'SUM'
        self.AVERAGE = 'AVG'
        self.MAXIMUM = 'MAX'
        self.MINIMUM = 'MIN'
        self.COUNT = 'COUNT'
        self.FIRST = 'FIRST'
        self.LAST = 'LAST'

        self.AGGREGATION = (
            'SUM', 'AVG', 'MAX', 'MIN', 'COUNT', 'FIRST', 'LAST',
        )

        self.SEG_SEPARATOR = '#'

    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, key, value):
        print()
        if key in self.__dict__.keys():
            # 存在性验证
            raise self.ConstError("Can't change a self variable: '%s'" % key)

        if not key.isupper():
            # 语法规范验证
            raise self.ConstCaseError("self variable must be combined with upper letters:'%s'" % key)

        self.__dict__[key] = value
