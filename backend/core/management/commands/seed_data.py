from django.core.management.base import BaseCommand
from core.models import FieldType, FieldValidator


BUILTIN_FIELD_TYPES = [
    {'key': 'text', 'name': '文本', 'icon': 'text', 'config_schema': {
        'max_length': {'type': 'number', 'default': 255, 'label': '最大长度'},
        'pattern': {'type': 'string', 'default': '', 'label': '正则表达式'},
    }},
    {'key': 'number', 'name': '数字', 'icon': 'number', 'config_schema': {
        'min': {'type': 'number', 'default': None, 'label': '最小值'},
        'max': {'type': 'number', 'default': None, 'label': '最大值'},
        'decimal_places': {'type': 'number', 'default': 0, 'label': '小数位数'},
    }},
    {'key': 'date', 'name': '日期', 'icon': 'date', 'config_schema': {
        'min_date': {'type': 'date', 'default': None, 'label': '最早日期'},
        'max_date': {'type': 'date', 'default': None, 'label': '最晚日期'},
    }},
    {'key': 'boolean', 'name': '布尔', 'icon': 'boolean', 'config_schema': {}},
    {'key': 'long_text', 'name': '长文本', 'icon': 'longtext', 'config_schema': {
        'max_length': {'type': 'number', 'default': 10000, 'label': '最大长度'},
    }},
    {'key': 'select', 'name': '下拉选项', 'icon': 'select', 'config_schema': {
        'options': {'type': 'array', 'default': [], 'label': '选项列表'},
    }},
    {'key': 'multi_select', 'name': '多选', 'icon': 'multiselect', 'config_schema': {
        'options': {'type': 'array', 'default': [], 'label': '选项列表'},
        'min_count': {'type': 'number', 'default': None, 'label': '最少选择数'},
        'max_count': {'type': 'number', 'default': None, 'label': '最多选择数'},
    }},
    {'key': 'attachment', 'name': '附件', 'icon': 'attachment', 'config_schema': {
        'max_size': {'type': 'number', 'default': 10485760, 'label': '文件大小上限(字节)'},
        'allowed_types': {'type': 'array', 'default': [], 'label': '允许的文件类型'},
    }},
    {'key': 'reference', 'name': '关联引用', 'icon': 'reference', 'config_schema': {
        'target_list': {'type': 'string', 'default': '', 'label': '目标列表ID'},
    }},
]

BUILTIN_VALIDATORS = [
    {'key': 'required', 'name': '必填', 'rule_type': 'required', 'rule_config': {}, 'error_message': '此字段为必填'},
    {'key': 'phone', 'name': '手机号', 'rule_type': 'regex', 'rule_config': {'pattern': r'^1[3-9]\d{9}$'}, 'error_message': '无效的手机号'},
    {'key': 'email', 'name': '邮箱', 'rule_type': 'regex', 'rule_config': {'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'}, 'error_message': '无效的邮箱地址'},
    {'key': 'id_card', 'name': '身份证号', 'rule_type': 'regex', 'rule_config': {'pattern': r'^\d{17}[\dXx]$'}, 'error_message': '无效的身份证号'},
]


class Command(BaseCommand):
    help = 'Seed built-in field types and validators'

    def handle(self, *args, **options):
        for ft_data in BUILTIN_FIELD_TYPES:
            ft, created = FieldType.objects.update_or_create(
                key=ft_data['key'],
                defaults={**ft_data, 'builtin': True}
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} field type: {ft.name}")

        for fv_data in BUILTIN_VALIDATORS:
            fv, created = FieldValidator.objects.update_or_create(
                key=fv_data['key'],
                defaults={**fv_data, 'builtin': True}
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} validator: {fv.name}")

        self.stdout.write(self.style.SUCCESS('Seed completed'))
