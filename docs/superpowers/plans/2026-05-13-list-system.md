# 通用列表系统 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建元数据驱动的动态列表系统，支持字段类型管理、内容类型定义、列表创建、动态数据 CRUD、前后端双重校验、回收站。

**Architecture:** Django REST Framework 后端提供 RESTful API + 核心引擎模块。Vue3/Element Plus 前端通过声明式规则引擎与后端共享校验逻辑。PostgreSQL 元数据表 + 每列表独立 JSONB 列存数据。

**Tech Stack:** Python 3.11+ / Django 5.x / DRF / psycopg2-binary / Vue 3 / Element Plus / Vite / pinia

**Database:** PostgreSQL @ 192.168.11.219:15432, user / @1Qazxsw2, appdb

---

## 文件结构

```
backend/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── __init__.py
│   ├── models.py          # BaseModel, FieldType, FieldValidator
│   ├── registry.py        # FieldTypeRegistry
│   ├── validation.py      # ValidationEngine
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── applications/
│   ├── __init__.py
│   ├── models.py          # Application, Navigation
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── metadata/
│   ├── __init__.py
│   ├── models.py          # ContentType, ContentTypeField, List, ListField, ListView
│   ├── managers.py        # ContentTypeManager (inheritance), ListManager
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── data/
│   ├── __init__.py
│   ├── table_builder.py   # DynamicTableBuilder
│   ├── query_builder.py   # QueryBuilder
│   ├── serializer_factory.py  # SerializerFactory
│   ├── views.py           # DynamicRecordViewSet + export/import
│   ├── trash.py           # TrashManager + TrashView
│   └── urls.py
├── manage.py
└── requirements.txt

frontend/
├── package.json
├── vite.config.js
├── index.html
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/index.js
│   ├── api/
│   │   ├── index.js
│   │   ├── applications.js
│   │   ├── fieldTypes.js
│   │   ├── contentTypes.js
│   │   ├── lists.js
│   │   ├── records.js
│   │   └── trash.js
│   ├── utils/
│   │   └── ruleEngine.js
│   ├── views/
│   │   ├── applications/AppList.vue
│   │   ├── field-types/FieldTypeList.vue
│   │   ├── content-types/ContentTypeList.vue
│   │   ├── content-types/ContentTypeDesigner.vue
│   │   ├── lists/ListManagement.vue
│   │   ├── lists/ListDesigner.vue
│   │   ├── lists/ListData.vue
│   │   ├── lists/RecordForm.vue
│   │   ├── trash/TrashPage.vue
│   │   └── navigations/NavigationConfig.vue
│   └── components/
│       ├── AppLayout.vue
│       ├── AppSidebar.vue
│       ├── DynamicForm.vue
│       ├── DynamicSearchBar.vue
│       └── ViewTabs.vue
```

---

## Phase 1: 后端基础搭建

### Task 1: Django 项目初始化

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/config/asgi.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
django>=5.0,<6.0
djangorestframework>=3.15,<4.0
psycopg2-binary>=2.9,<3.0
django-cors-headers>=4.0,<5.0
openpyxl>=3.1,<4.0
```

- [ ] **Step 2: 安装依赖**

```bash
cd backend && pip install -r requirements.txt
```

Expected: 所有包安装成功。

- [ ] **Step 3: 创建 Django 项目配置**

```python
# backend/manage.py
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
```

```python
# backend/config/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dev-key-change-in-production-xxx'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
    'applications',
    'metadata',
    'data',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'appdb',
        'HOST': '192.168.11.219',
        'USER': 'user',
        'PASSWORD': '@1Qazxsw2',
        'PORT': '15432',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}
```

```python
# backend/config/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/', include('core.urls')),
    path('api/', include('applications.urls')),
    path('api/', include('metadata.urls')),
    path('api/', include('data.urls')),
]
```

```python
# backend/config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

```python
# backend/config/asgi.py
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
```

- [ ] **Step 4: 创建各 app 的 __init__.py**

```bash
cd backend && mkdir -p core applications metadata data && touch core/__init__.py applications/__init__.py metadata/__init__.py data/__init__.py
```

- [ ] **Step 5: 验证数据库连接**

```bash
cd backend && python manage.py check --database default
```

Expected: "System check identified no issues (0 silenced)."

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: initialize Django project with PostgreSQL connection"
```

---

### Task 2: BaseModel + FieldType + FieldValidator 模型

**Files:**
- Create: `backend/core/models.py`

- [ ] **Step 1: 创建核心模型**

```python
# backend/core/models.py
import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FieldType(BaseModel):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    builtin = models.BooleanField(default=False)
    config_schema = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'field_types'
        ordering = ['builtin', 'created_at']

    def __str__(self):
        return self.name


class FieldValidator(BaseModel):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    builtin = models.BooleanField(default=False)
    rule_type = models.CharField(max_length=50)
    rule_config = models.JSONField(default=dict)
    error_message = models.CharField(max_length=200, default='验证失败')

    class Meta:
        db_table = 'field_validators'
        ordering = ['builtin', 'created_at']

    def __str__(self):
        return self.name
```

- [ ] **Step 2: 运行 makemigrations 和 migrate**

```bash
cd backend && python manage.py makemigrations core && python manage.py migrate core
```

Expected: "Applying core.0001_initial... OK"

- [ ] **Step 3: Commit**

```bash
git add backend/core/models.py backend/core/migrations/
git commit -m "feat: add BaseModel, FieldType, FieldValidator models"
```

---

### Task 3: 种子数据 — 内置字段类型和验证器

**Files:**
- Create: `backend/core/management/__init__.py`
- Create: `backend/core/management/commands/__init__.py`
- Create: `backend/core/management/commands/seed_data.py`

- [ ] **Step 1: 创建 seed 命令**

```python
# backend/core/management/commands/seed_data.py
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
```

- [ ] **Step 2: 执行 seed**

```bash
cd backend && python manage.py seed_data
```

Expected: 输出 9 个字段类型和 4 个验证器的创建确认。

- [ ] **Step 3: Commit**

```bash
git add backend/core/management/
git commit -m "feat: add seed command for built-in field types and validators"
```

---

### Task 4: FieldTypeRegistry + 字段类型 API

**Files:**
- Create: `backend/core/registry.py`
- Create: `backend/core/serializers.py`
- Create: `backend/core/views.py`
- Create: `backend/core/urls.py`

- [ ] **Step 1: 创建 FieldTypeRegistry**

```python
# backend/core/registry.py
from core.models import FieldType

SEARCH_TYPE_MAP = {
    'text': 'fuzzy',
    'number': 'range',
    'date': 'range',
    'boolean': 'exact',
    'long_text': 'fuzzy',
    'select': 'exact',
    'multi_select': 'exact',
    'attachment': None,
    'reference': 'exact',
}


class FieldTypeRegistry:
    _instance = None

    def __init__(self):
        self._cache = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_all(self):
        return FieldType.objects.all()

    def get_by_key(self, key):
        if key not in self._cache:
            self._cache[key] = FieldType.objects.get(key=key)
        return self._cache[key]

    def get_search_type(self, field_type_key):
        return SEARCH_TYPE_MAP.get(field_type_key)

    def clear_cache(self):
        self._cache = {}


field_type_registry = FieldTypeRegistry.get_instance()
```

- [ ] **Step 2: 创建 serializers**

```python
# backend/core/serializers.py
from rest_framework import serializers
from core.models import FieldType, FieldValidator


class FieldTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldType
        fields = '__all__'
        read_only_fields = ['id', 'builtin', 'created_at', 'updated_at']


class FieldValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldValidator
        fields = '__all__'
        read_only_fields = ['id', 'builtin', 'created_at', 'updated_at']
```

- [ ] **Step 3: 创建 views**

```python
# backend/core/views.py
from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from core.models import FieldType, FieldValidator
from core.serializers import FieldTypeSerializer, FieldValidatorSerializer


class FieldTypeViewSet(viewsets.ModelViewSet):
    queryset = FieldType.objects.all()
    serializer_class = FieldTypeSerializer

    def perform_destroy(self, instance):
        if instance.builtin:
            raise MethodNotAllowed('DELETE', detail='内置字段类型不可删除')
        instance.delete()


class FieldValidatorViewSet(viewsets.ModelViewSet):
    queryset = FieldValidator.objects.all()
    serializer_class = FieldValidatorSerializer

    def perform_destroy(self, instance):
        if instance.builtin:
            raise MethodNotAllowed('DELETE', detail='内置验证器不可删除')
        instance.delete()
```

- [ ] **Step 4: 创建 urls**

```python
# backend/core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import FieldTypeViewSet, FieldValidatorViewSet

router = DefaultRouter()
router.register(r'field-types', FieldTypeViewSet)
router.register(r'validators', FieldValidatorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

- [ ] **Step 5: 验证 API 可访问**

```bash
cd backend && python manage.py runserver 8000 &
sleep 2
curl http://localhost:8000/api/field-types/
```

Expected: 返回 JSON 数组，包含 9 个内置字段类型。

- [ ] **Step 6: Commit**

```bash
git add backend/core/registry.py backend/core/serializers.py backend/core/views.py backend/core/urls.py
git commit -m "feat: add FieldTypeRegistry, field type and validator CRUD APIs"
```

---

### Task 5: ValidationEngine — 前后端校验规则生成

**Files:**
- Create: `backend/core/validation.py`

- [ ] **Step 1: 创建 ValidationEngine**

```python
# backend/core/validation.py
import re
from datetime import datetime
from rest_framework import serializers
from core.registry import field_type_registry


class ValidationEngine:
    """根据字段定义生成 DRF Serializer Field + Validator"""

    @classmethod
    def build_field(cls, field_def, validators_map):
        """field_def: dict with field_type__key, required, unique, config, validators"""
        ft_key = field_def['field_type__key'] if isinstance(field_def.get('field_type__key'), str) else field_def.get('field_type__key', {}).get('key', 'text')
        required = field_def.get('required', False)
        config = field_def.get('config') or {}
        validator_keys = field_def.get('validators') or []

        drf_field, extra_kwargs = cls._field_for_type(ft_key, required, config)
        extra_kwargs['required'] = required

        # Add unique validator
        if field_def.get('unique'):
            extra_kwargs['validators'] = extra_kwargs.get('validators', []) + [UniqueValidator(field_def['key'])]

        # Add custom validators from field definition
        for vk in validator_keys:
            if vk in validators_map:
                v = validators_map[vk]
                rule_type = v.rule_type
                rule_config = v.rule_config or {}
                error_msg = v.error_message

                if rule_type == 'regex':
                    extra_kwargs.setdefault('validators', []).append(
                        serializers.RegexValidator(regex=rule_config.get('pattern', ''), message=error_msg)
                    )
                elif rule_type == 'range':
                    min_val = rule_config.get('min')
                    max_val = rule_config.get('max')
                    if min_val is not None:
                        extra_kwargs.setdefault('validators', []).append(
                            serializers.MinValueValidator(min_val, message=error_msg)
                        )
                    if max_val is not None:
                        extra_kwargs.setdefault('validators', []).append(
                            serializers.MaxValueValidator(max_val, message=error_msg)
                        )

        return drf_field(**{k: v for k, v in extra_kwargs.items() if k != 'validators' or v}), extra_kwargs.get('validators', [])

    @classmethod
    def _field_for_type(cls, ft_key, required, config):
        fields = {
            'text': (serializers.CharField, {
                'allow_blank': not required,
                'max_length': config.get('max_length') or 255,
            }),
            'number': (serializers.FloatField if config.get('decimal_places') else serializers.IntegerField, {
                'min_value': config.get('min'),
                'max_value': config.get('max'),
            }),
            'date': (serializers.DateField, {}),
            'boolean': (serializers.BooleanField, {}),
            'long_text': (serializers.CharField, {
                'allow_blank': not required,
                'max_length': config.get('max_length') or 10000,
            }),
            'select': (serializers.CharField, {
                'allow_blank': not required,
            }),
            'multi_select': (serializers.ListField, {
                'child': serializers.CharField(),
            }),
            'attachment': (serializers.JSONField, {}),
            'reference': (serializers.CharField, {
                'allow_blank': not required,
            }),
        }
        default = (serializers.CharField, {'allow_blank': not required, 'max_length': 255})
        field_class, kwargs = fields.get(ft_key, default)
        return field_class, kwargs

    @classmethod
    def build_frontend_rules(cls, field_def, validators_map):
        """生成前端 Element Plus 校验规则"""
        rules = []
        ft_key = field_def['field_type__key'] if isinstance(field_def.get('field_type__key'), str) else field_def.get('field_type__key', {}).get('key', 'text')
        required = field_def.get('required', False)
        config = field_def.get('config') or {}
        validator_keys = field_def.get('validators') or []

        if required:
            rules.append({'required': True, 'message': f'{field_def.get("name", "")}为必填', 'trigger': 'blur'})

        if ft_key in ('text', 'long_text'):
            max_len = config.get('max_length', 255 if ft_key == 'text' else 10000)
            if max_len:
                rules.append({'max': max_len, 'message': f'最多{max_len}个字符', 'trigger': 'blur'})
            pattern = config.get('pattern')
            if pattern:
                rules.append({'pattern': pattern, 'message': '格式不正确', 'trigger': 'blur'})

        elif ft_key == 'number':
            if config.get('min') is not None:
                rules.append({'type': 'number', 'min': config['min'], 'message': f'最小值为{config["min"]}', 'trigger': 'blur'})
            if config.get('max') is not None:
                rules.append({'type': 'number', 'max': config['max'], 'message': f'最大值为{config["max"]}', 'trigger': 'blur'})

        elif ft_key == 'multi_select':
            if config.get('min_count'):
                rules.append({'type': 'array', 'min': config['min_count'], 'message': f'至少选择{config["min_count"]}项', 'trigger': 'change'})
            if config.get('max_count'):
                rules.append({'type': 'array', 'max': config['max_count'], 'message': f'最多选择{config["max_count"]}项', 'trigger': 'change'})

        # Custom validators
        for vk in validator_keys:
            if vk in validators_map:
                v = validators_map[vk]
                if v.rule_type == 'regex':
                    rules.append({'pattern': v.rule_config.get('pattern', ''), 'message': v.error_message, 'trigger': 'blur'})
                elif v.rule_type == 'range':
                    cfg = v.rule_config
                    if 'min' in cfg:
                        rules.append({'type': 'number', 'min': cfg['min'], 'message': v.error_message, 'trigger': 'blur'})
                    if 'max' in cfg:
                        rules.append({'type': 'number', 'max': cfg['max'], 'message': v.error_message, 'trigger': 'blur'})

        return rules


class UniqueValidator:
    def __init__(self, field_key):
        self.field_key = field_key

    def __call__(self, value):
        # 实际唯一性校验在 SerializerFactory 的 validate 方法中通过查询数据库完成
        # 这个 validator 只是一个标记，具体的唯一性由 DynamicRecordSerializer 处理
        pass

    def __eq__(self, other):
        return isinstance(other, UniqueValidator) and self.field_key == other.field_key
```

- [ ] **Step 2: 验证 ValidationEngine 导入正常**

```bash
cd backend && python -c "from core.validation import ValidationEngine; print('OK')"
```

Expected: "OK"

- [ ] **Step 3: Commit**

```bash
git add backend/core/validation.py
git commit -m "feat: add ValidationEngine for DRF and frontend rule generation"
```

---

### Task 6: Application 模型 + API

**Files:**
- Create: `backend/applications/models.py`
- Create: `backend/applications/serializers.py`
- Create: `backend/applications/views.py`
- Create: `backend/applications/urls.py`

- [ ] **Step 1: 创建 Application 和 Navigation 模型**

```python
# backend/applications/models.py
import uuid
from django.db import models
from core.models import BaseModel


class Application(BaseModel):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    url_prefix = models.CharField(max_length=200, default='/')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'applications'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name

    def get_full_url_prefix(self):
        if self.parent:
            return self.parent.get_full_url_prefix().rstrip('/') + '/' + self.url_prefix.strip('/')
        return '/' + self.url_prefix.strip('/') if self.url_prefix.strip('/') else '/'


class Navigation(BaseModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='navigations')
    name = models.CharField(max_length=200)
    link_type = models.CharField(max_length=20, choices=[('list', '列表'), ('custom_url', '自定义链接')])
    list = models.ForeignKey('metadata.List', on_delete=models.SET_NULL, null=True, blank=True)
    custom_url = models.CharField(max_length=500, blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)
    visible = models.BooleanField(default=True)

    class Meta:
        db_table = 'navigations'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name
```

- [ ] **Step 2: 创建 serializers**

```python
# backend/applications/serializers.py
from rest_framework import serializers
from applications.models import Application, Navigation


class ApplicationSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children(self, obj):
        if obj.children.exists():
            return ApplicationSerializer(obj.children.all(), many=True).data
        return []


class NavigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
```

- [ ] **Step 3: 创建 views**

```python
# backend/applications/views.py
from rest_framework import viewsets
from applications.models import Application, Navigation
from applications.serializers import ApplicationSerializer, NavigationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.filter(parent__isnull=True)
    serializer_class = ApplicationSerializer


class NavigationViewSet(viewsets.ModelViewSet):
    serializer_class = NavigationSerializer

    def get_queryset(self):
        return Navigation.objects.filter(application_id=self.kwargs['app_id'])

    def perform_create(self, serializer):
        serializer.save(application_id=self.kwargs['app_id'])
```

- [ ] **Step 4: 创建 urls**

```python
# backend/applications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from applications.views import ApplicationViewSet, NavigationViewSet

router = DefaultRouter()
router.register(r'apps', ApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('apps/<uuid:app_id>/navigations/', NavigationViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('apps/<uuid:app_id>/navigations/<uuid:pk>/', NavigationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
]
```

- [ ] **Step 5: 运行迁移**

```bash
cd backend && python manage.py makemigrations applications && python manage.py migrate applications
```

Expected: "Applying applications.0001_initial... OK"

- [ ] **Step 6: 创建默认应用**

```bash
cd backend && python manage.py shell -c "
from applications.models import Application
app, created = Application.objects.get_or_create(
    key='default',
    defaults={'name': '通用列表存储', 'url_prefix': '/', 'description': '默认应用空间'}
)
print(f'Default app created: {app.id}')
"
```

- [ ] **Step 7: Commit**

```bash
git add backend/applications/
git commit -m "feat: add Application and Navigation models with CRUD APIs"
```

---

### Task 7: ContentType + ContentTypeField 模型 + 字段继承

**Files:**
- Create: `backend/metadata/__init__.py`
- Create: `backend/metadata/models.py`
- Create: `backend/metadata/managers.py`

- [ ] **Step 1: 创建 ContentType 和 ContentTypeField 模型**

```python
# backend/metadata/models.py
from django.db import models
from core.models import BaseModel


class ContentType(BaseModel):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class Meta:
        db_table = 'content_types'
        ordering = ['created_at']

    def __str__(self):
        return self.name

    def get_all_fields(self):
        """递归获取所有字段（含继承），子覆盖父"""
        from metadata.managers import ContentTypeManager
        return ContentTypeManager.resolve_fields(self)


class ContentTypeField(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='fields')
    field_type = models.ForeignKey('core.FieldType', on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100)
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    searchable = models.BooleanField(default=False)
    search_type = models.CharField(max_length=20, blank=True, default='')
    order = models.IntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)
    validators = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'content_type_fields'
        ordering = ['order', 'created_at']
        unique_together = [['content_type', 'key']]

    def save(self, *args, **kwargs):
        if not self.search_type:
            from core.registry import field_type_registry
            self.search_type = field_type_registry.get_search_type(self.field_type.key) or ''
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.field_type.name})'


class List(BaseModel):
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, default='')
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(max_length=200)
    table_name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lists'
        ordering = ['created_at']

    def __str__(self):
        return self.name

    def get_all_fields(self):
        from metadata.managers import ContentTypeManager
        if self.content_type:
            return ContentTypeManager.resolve_fields(self.content_type)
        return self.fields.all()


class ListField(BaseModel):
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='fields')
    field_type = models.ForeignKey('core.FieldType', on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=100)
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    searchable = models.BooleanField(default=False)
    search_type = models.CharField(max_length=20, blank=True, default='')
    order = models.IntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)
    validators = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'list_fields'
        ordering = ['order', 'created_at']
        unique_together = [['list', 'key']]

    def save(self, *args, **kwargs):
        if not self.search_type:
            from core.registry import field_type_registry
            self.search_type = field_type_registry.get_search_type(self.field_type.key) or ''
        super().save(*args, **kwargs)


class ListView(BaseModel):
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='views')
    name = models.CharField(max_length=200)
    url_key = models.CharField(max_length=100, default='default')
    is_default = models.BooleanField(default=False)
    config = models.JSONField(default=dict)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'list_views'
        ordering = ['order', 'created_at']
        unique_together = [['list', 'url_key']]

    def __str__(self):
        return self.name
```

- [ ] **Step 2: 创建 ContentTypeManager**

```python
# backend/metadata/managers.py
from collections import OrderedDict


class ContentTypeManager:
    @classmethod
    def resolve_fields(cls, content_type):
        """递归解析字段，子类型字段覆盖父类型同名字段"""
        fields = OrderedDict()

        if content_type.parent:
            parent_fields = cls.resolve_fields(content_type.parent)
            for f in parent_fields:
                fields[f.key] = {
                    'name': f.name,
                    'key': f.key,
                    'field_type': f.field_type,
                    'field_type__key': f.field_type.key,
                    'required': f.required,
                    'unique': f.unique,
                    'searchable': f.searchable,
                    'search_type': f.search_type,
                    'order': f.order,
                    'config': f.config,
                    'validators': f.validators,
                }

        for f in content_type.fields.all():
            fields[f.key] = {
                'name': f.name,
                'key': f.key,
                'field_type': f.field_type,
                'field_type__key': f.field_type.key,
                'required': f.required,
                'unique': f.unique,
                'searchable': f.searchable,
                'search_type': f.search_type,
                'order': f.order,
                'config': f.config,
                'validators': f.validators,
            }

        return list(fields.values())
```

- [ ] **Step 3: 运行迁移**

```bash
cd backend && python manage.py makemigrations metadata && python manage.py migrate metadata
```

Expected: "Applying metadata.0001_initial... OK"

- [ ] **Step 4: Commit**

```bash
git add backend/metadata/
git commit -m "feat: add ContentType, ContentTypeField, List, ListField, ListView models with inheritance"
```

---

### Task 8: 元数据 API (ContentType + List + ListView CRUD)

**Files:**
- Create: `backend/metadata/serializers.py`
- Create: `backend/metadata/views.py`
- Create: `backend/metadata/urls.py`

- [ ] **Step 1: 创建 serializers**

```python
# backend/metadata/serializers.py
from rest_framework import serializers
from metadata.models import ContentType, ContentTypeField, List, ListField, ListView


class ContentTypeFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentTypeField
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContentTypeSerializer(serializers.ModelSerializer):
    fields = ContentTypeFieldSerializer(many=True, read_only=True)

    class Meta:
        model = ContentType
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListField
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListView
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ListSerializer(serializers.ModelSerializer):
    fields = ListFieldSerializer(many=True, read_only=True)
    views = ListViewSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = '__all__'
        read_only_fields = ['id', 'table_name', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']
```

- [ ] **Step 2: 创建 views**

```python
# backend/metadata/views.py
from datetime import datetime
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from metadata.models import ContentType, ContentTypeField, List, ListField, ListView
from metadata.serializers import (
    ContentTypeSerializer, ContentTypeFieldSerializer,
    ListSerializer, ListFieldSerializer, ListViewSerializer,
)
from metadata.managers import ContentTypeManager
from data.table_builder import DynamicTableBuilder


class ContentTypeViewSet(viewsets.ModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer


class ContentTypeFieldViewSet(viewsets.ModelViewSet):
    serializer_class = ContentTypeFieldSerializer

    def get_queryset(self):
        return ContentTypeField.objects.filter(content_type_id=self.kwargs['ct_id'])

    def perform_create(self, serializer):
        serializer.save(content_type_id=self.kwargs['ct_id'])


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer

    def get_queryset(self):
        return List.objects.filter(application_id=self.kwargs['app_id'], is_deleted=False)

    def perform_create(self, serializer):
        app_id = self.kwargs['app_id']
        count = List.objects.filter(application_id=app_id).count()
        default_url = f'/list{count + 1}'
        instance = serializer.save(
            application_id=app_id,
            table_name=f"dyn_{serializer.validated_data['key']}",
            url=serializer.validated_data.get('url') or default_url,
        )
        DynamicTableBuilder.create_table(instance.table_name)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = datetime.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])


class ListFieldViewSet(viewsets.ModelViewSet):
    serializer_class = ListFieldSerializer

    def get_queryset(self):
        return ListField.objects.filter(list_id=self.kwargs['list_id'])

    def perform_create(self, serializer):
        serializer.save(list_id=self.kwargs['list_id'])


class ListViewViewSet(viewsets.ModelViewSet):
    serializer_class = ListViewSerializer

    def get_queryset(self):
        return ListView.objects.filter(list_id=self.kwargs['list_id'])

    def perform_create(self, serializer):
        serializer.save(list_id=self.kwargs['list_id'])

    @action(detail=False, methods=['get'], url_path='by-url/(?P<url_key>[^/.]+)')
    def by_url(self, request, list_id, url_key):
        view = self.get_queryset().filter(url_key=url_key).first()
        if not view:
            return Response({'detail': 'View not found'}, status=404)
        return Response(ListViewSerializer(view).data)
```

- [ ] **Step 3: 创建 form-schema action (在 ListViewSet 中追加)**

```python
# Add to ListViewSet in backend/metadata/views.py
    @action(detail=True, methods=['get'])
    def form_schema(self, request, app_id=None, pk=None):
        lst = self.get_object()
        fields = lst.get_all_fields()
        from core.models import FieldValidator
        validators = {
            v.key: v for v in FieldValidator.objects.all()
        }
        from core.validation import ValidationEngine

        schema = {
            'list_id': str(lst.id),
            'list_name': lst.name,
            'fields': [],
        }
        for f in fields:
            field_data = {
                'key': f['key'],
                'name': f['name'],
                'field_type': f['field_type__key'],
                'required': f['required'],
                'unique': f['unique'],
                'config': f['config'],
                'rules': ValidationEngine.build_frontend_rules(f, validators),
            }
            if f['field_type__key'] == 'select' or f['field_type__key'] == 'multi_select':
                field_data['options'] = f['config'].get('options', [])
            schema['fields'].append(field_data)

        return Response(schema)
```

- [ ] **Step 4: 创建 urls**

```python
# backend/metadata/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metadata.views import (
    ContentTypeViewSet, ContentTypeFieldViewSet,
    ListViewSet, ListFieldViewSet, ListViewViewSet,
)

router = DefaultRouter()
router.register(r'content-types', ContentTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('content-types/<uuid:ct_id>/fields/', ContentTypeFieldViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('content-types/<uuid:ct_id>/fields/<uuid:pk>/', ContentTypeFieldViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('apps/<uuid:app_id>/lists/', ListViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('apps/<uuid:app_id>/lists/<uuid:pk>/', ListViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('lists/<uuid:list_id>/fields/', ListFieldViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('lists/<uuid:list_id>/fields/<uuid:pk>/', ListFieldViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('lists/<uuid:list_id>/views/', ListViewViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('lists/<uuid:list_id>/views/<uuid:pk>/', ListViewViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
]
```

Note: form_schema action provided by DRF router automatically at: `GET /api/apps/{app_id}/lists/{id}/form_schema/`

- [ ] **Step 5: Commit**

```bash
git add backend/metadata/
git commit -m "feat: add ContentType, List, ListView CRUD APIs with form-schema endpoint"
```

---

## Phase 2: 动态数据引擎

### Task 9: DynamicTableBuilder + QueryBuilder

**Files:**
- Create: `backend/data/__init__.py`
- Create: `backend/data/table_builder.py`
- Create: `backend/data/query_builder.py`

- [ ] **Step 1: 创建 DynamicTableBuilder**

```python
# backend/data/table_builder.py
from django.db import connection


class DynamicTableBuilder:
    @classmethod
    def create_table(cls, table_name):
        sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            data JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)

    @classmethod
    def drop_table(cls, table_name):
        sql = f'DROP TABLE IF EXISTS "{table_name}"'
        with connection.cursor() as cursor:
            cursor.execute(sql)

    @classmethod
    def add_computed_column(cls, table_name, field_key):
        col_name = f"{field_key}_c"
        sql = f"""
        ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{col_name}" TEXT GENERATED ALWAYS AS (data->>'{field_key}') STORED
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
```

- [ ] **Step 2: 创建 QueryBuilder**

```python
# backend/data/query_builder.py
from django.db import connection


class QueryBuilder:
    OP_MAP = {
        'eq': '=',
        'neq': '!=',
        'contains': 'LIKE',
        'startswith': 'LIKE',
        'gt': '>',
        'gte': '>=',
        'lt': '<',
        'lte': '<=',
    }

    @classmethod
    def build_filter_clause(cls, filter_str):
        """Parse filter=key:op:value,key:op:value into SQL WHERE clause"""
        if not filter_str:
            return '', []

        clauses = []
        params = []

        for part in filter_str.split(','):
            parts = part.split(':', 2)
            if len(parts) < 3:
                continue
            key, op, value = parts[0], parts[1], parts[2]

            json_path = key

            if op == 'isnull':
                clauses.append(f"data->>'{json_path}' IS NULL")
                continue

            if op in ('in', 'nin'):
                values = [v.strip() for v in value.split('|')]
                placeholders = ','.join(['%s'] * len(values))
                not_ = 'NOT' if op == 'nin' else ''
                clauses.append(f"data->>'{json_path}' {not_} IN ({placeholders})")
                params.extend(values)
                continue

            if op == 'contains':
                clauses.append(f"data->>'{json_path}' LIKE %s")
                params.append(f'%{value}%')
            elif op == 'startswith':
                clauses.append(f"data->>'{json_path}' LIKE %s")
                params.append(f'{value}%')
            else:
                sql_op = cls.OP_MAP.get(op, '=')
                clauses.append(f"data->>'{json_path}' {sql_op} %s")
                params.append(value)

        where = ' AND '.join(clauses)
        return f'({where})' if where else '', params

    @classmethod
    def build_select(cls, table_name, filter_str='', sort='', order='asc', page=1, page_size=20):
        where, params = cls.build_filter_clause(filter_str)

        # Always filter out soft-deleted records
        deleted_filter = "(data->>'_is_deleted' IS NULL OR data->>'_is_deleted' = 'false')"
        if where:
            where = f"{where} AND {deleted_filter}"
        else:
            where = deleted_filter

        order_clause = ''
        if sort:
            direction = 'DESC' if order.lower() == 'desc' else 'ASC'
            order_clause = f"ORDER BY data->>'{sort}' {direction}"

        offset = (page - 1) * page_size

        count_sql = f'SELECT COUNT(*) FROM "{table_name}" WHERE {where}'
        select_sql = f"""
        SELECT id, data, created_at, updated_at
        FROM "{table_name}"
        WHERE {where}
        {order_clause}
        OFFSET {offset} LIMIT {page_size}
        """

        return count_sql, select_sql, params

    @classmethod
    def execute_query(cls, table_name, filter_str='', sort='', order='asc', page=1, page_size=20):
        count_sql, select_sql, params = cls.build_select(
            table_name, filter_str, sort, order, page, page_size
        )

        with connection.cursor() as cursor:
            cursor.execute(count_sql, params)
            row = cursor.fetchone()
            total = row[0] if row else 0

            cursor.execute(select_sql, params)
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': rows,
        }
```

- [ ] **Step 3: Commit**

```bash
git add backend/data/
git commit -m "feat: add DynamicTableBuilder and QueryBuilder"
```

---

### Task 10: SerializerFactory + 动态记录 CRUD

**Files:**
- Create: `backend/data/serializer_factory.py`
- Create: `backend/data/views.py`
- Create: `backend/data/urls.py`

- [ ] **Step 1: 创建 SerializerFactory**

```python
# backend/data/serializer_factory.py
import json
from rest_framework import serializers
from core.models import FieldValidator
from core.validation import ValidationEngine


class SerializerFactory:
    @classmethod
    def create_serializer(cls, list_obj):
        """动态生成 DRF Serializer"""
        fields_def = list_obj.get_all_fields()
        validators_map = {v.key: v for v in FieldValidator.objects.all()}

        serializer_fields = {}
        unique_fields = []

        for f in fields_def:
            field_key = f['key']
            drf_field, extra_validators = ValidationEngine.build_field(f, validators_map)
            serializer_fields[field_key] = drf_field
            if f.get('unique'):
                unique_fields.append(field_key)

        Meta = type('Meta', (), {'ref_name': f'DynamicSerializer_{list_obj.key}'})

        def create(self, validated_data):
            from django.db import connection
            import uuid
            record_id = str(uuid.uuid4())
            data = {**validated_data, '_is_deleted': False, '_deleted_at': None}
            with connection.cursor() as cursor:
                cursor.execute(
                    f'INSERT INTO "{list_obj.table_name}" (id, data) VALUES (%s, %s)',
                    [record_id, json.dumps(data, ensure_ascii=False, default=str)]
                )
            data['id'] = record_id
            return data

        def update(self, instance, validated_data):
            from django.db import connection
            merged = {**instance.get('data', instance), **validated_data}
            if isinstance(merged.get('data'), dict):
                merged = {**merged['data'], **validated_data}
            with connection.cursor() as cursor:
                cursor.execute(
                    f'UPDATE "{list_obj.table_name}" SET data = %s, updated_at = NOW() WHERE id = %s',
                    [json.dumps(merged, ensure_ascii=False, default=str), instance['id']]
                )
            merged['id'] = instance['id']
            return merged

        def validate(self, data):
            """唯一性校验"""
            from django.db import connection
            for fk in unique_fields:
                if fk in data:
                    value = data[fk]
                    table = list_obj.table_name
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"SELECT COUNT(*) FROM \"{table}\" WHERE data->>'{fk}' = %s AND (data->>'_is_deleted' IS NULL OR data->>'_is_deleted' = 'false')",
                            [str(value)]
                        )
                        row = cursor.fetchone()
                        if row and row[0] > 0:
                            raise serializers.ValidationError({fk: f'值 "{value}" 已存在'})
            return data

        attrs = {
            **serializer_fields,
            'Meta': Meta,
            'create': create,
            'update': update,
            'validate': validate,
        }

        return type(f'DynamicSerializer_{list_obj.key}', (serializers.Serializer,), attrs)
```

- [ ] **Step 2: 创建动态记录 ViewSet**

```python
# backend/data/views.py
import json
import uuid
from datetime import datetime
from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from metadata.models import List, ListView
from data.table_builder import DynamicTableBuilder
from data.query_builder import QueryBuilder
from data.serializer_factory import SerializerFactory


class DynamicRecordView(APIView):
    """动态记录 CRUD"""

    def _get_list(self, app_id, list_url):
        return List.objects.get(application_id=app_id, url=list_url, is_deleted=False)

    def get(self, request, app_id, list_url):
        lst = self._get_list(app_id, list_url)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        sort = request.query_params.get('sort', '')
        order = request.query_params.get('order', 'asc')
        filter_str = request.query_params.get('filter', '')

        # Apply view if specified
        view_key = request.query_params.get('view')
        if view_key:
            view_obj = ListView.objects.filter(list=lst, url_key=view_key).first()
            if view_obj:
                view_config = view_obj.config or {}
                if not sort and view_config.get('default_sort'):
                    sort = view_config['default_sort']
                if not filter_str and view_config.get('default_filter'):
                    filter_str = view_config['default_filter']
                if view_config.get('page_size'):
                    page_size = view_config['page_size']

        result = QueryBuilder.execute_query(lst.table_name, filter_str, sort, order, page, page_size)
        for row in result['results']:
            row['data'] = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat()
            if row.get('updated_at'):
                row['updated_at'] = row['updated_at'].isoformat()
        return Response(result)

    def post(self, request, app_id, list_url):
        lst = self._get_list(app_id, list_url)
        SerializerClass = SerializerFactory.create_serializer(lst)
        serializer = SerializerClass(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(instance, status=status.HTTP_201_CREATED)


class DynamicRecordDetailView(APIView):
    def _get_list(self, app_id, list_url):
        return List.objects.get(application_id=app_id, url=list_url, is_deleted=False)

    def _get_record(self, table_name, record_id):
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT id, data, created_at, updated_at FROM "{table_name}" WHERE id = %s',
                [record_id]
            )
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            if not row:
                return None
            record = dict(zip(columns, row))
            record['data'] = json.loads(record['data']) if isinstance(record['data'], str) else record['data']
            if record.get('created_at'):
                record['created_at'] = record['created_at'].isoformat()
            if record.get('updated_at'):
                record['updated_at'] = record['updated_at'].isoformat()
            return record

    def get(self, request, app_id, list_url, record_id):
        lst = self._get_list(app_id, list_url)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)
        return Response(record)

    def put(self, request, app_id, list_url, record_id):
        lst = self._get_list(app_id, list_url)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)

        SerializerClass = SerializerFactory.create_serializer(lst)
        serializer = SerializerClass(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.update(record, serializer.validated_data)
        return Response(updated)

    def delete(self, request, app_id, list_url, record_id):
        lst = self._get_list(app_id, list_url)
        record = self._get_record(lst.table_name, record_id)
        if not record:
            return Response({'detail': 'Not found'}, status=404)

        data = record['data'] or {}
        data['_is_deleted'] = True
        data['_deleted_at'] = datetime.now().isoformat()
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE "{lst.table_name}" SET data = %s, updated_at = NOW() WHERE id = %s',
                [json.dumps(data, ensure_ascii=False, default=str), record_id]
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DynamicRecordBatchView(APIView):
    def patch(self, request, app_id, list_url):
        lst = List.objects.get(application_id=app_id, url=list_url, is_deleted=False)
        record_ids = request.data.get('ids', [])
        field_key = request.data.get('field')
        value = request.data.get('value')

        if not record_ids or not field_key:
            return Response({'detail': 'ids and field are required'}, status=400)

        with connection.cursor() as cursor:
            for rid in record_ids:
                cursor.execute(
                    f'SELECT data FROM "{lst.table_name}" WHERE id = %s', [rid]
                )
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    data[field_key] = value
                    cursor.execute(
                        f'UPDATE "{lst.table_name}" SET data = %s, updated_at = NOW() WHERE id = %s',
                        [json.dumps(data, ensure_ascii=False, default=str), rid]
                    )

        return Response({'updated': len(record_ids)})
```

- [ ] **Step 3: 创建 urls**

```python
# backend/data/urls.py
from django.urls import path, re_path
from data.views import DynamicRecordView, DynamicRecordDetailView, DynamicRecordBatchView

urlpatterns = [
    re_path(r'^apps/(?P<app_id>[0-9a-f-]+)/lists/(?P<list_url>[^/]+)/records/$', DynamicRecordView.as_view()),
    re_path(r'^apps/(?P<app_id>[0-9a-f-]+)/lists/(?P<list_url>[^/]+)/records/batch/$', DynamicRecordBatchView.as_view()),
    re_path(r'^apps/(?P<app_id>[0-9a-f-]+)/lists/(?P<list_url>[^/]+)/records/(?P<record_id>[0-9a-f-]+)/$', DynamicRecordDetailView.as_view()),
]
```

- [ ] **Step 4: Commit**

```bash
git add backend/data/
git commit -m "feat: add SerializerFactory and dynamic record CRUD views"
```

---

### Task 11: 回收站功能

**Files:**
- Create: `backend/data/trash.py`

- [ ] **Step 1: 创建 TrashManager + TrashView**

```python
# backend/data/trash.py
import json
from datetime import datetime
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from metadata.models import List
from data.table_builder import DynamicTableBuilder


class TrashView(APIView):
    def get(self, request, app_id):
        deleted_lists = List.objects.filter(application_id=app_id, is_deleted=True)
        deleted_records = []

        for lst in List.objects.filter(application_id=app_id, is_deleted=False):
            with connection.cursor() as cursor:
                try:
                    cursor.execute(
                        f"SELECT id, data, updated_at FROM \"{lst.table_name}\" WHERE data->>'_is_deleted' = 'true'"
                    )
                    columns = [col[0] for col in cursor.description]
                    for row in cursor.fetchall():
                        rec = dict(zip(columns, row))
                        rec['data'] = json.loads(rec['data']) if isinstance(rec['data'], str) else rec['data']
                        if rec.get('updated_at'):
                            rec['updated_at'] = rec['updated_at'].isoformat()
                        rec['_list_name'] = lst.name
                        rec['_list_id'] = str(lst.id)
                        rec['_list_url'] = lst.url
                        rec['_type'] = 'record'
                        deleted_records.append(rec)
                except Exception:
                    pass

        trash_items = []
        for lst in deleted_lists:
            trash_items.append({
                'id': str(lst.id),
                'type': 'list',
                'name': lst.name,
                'deleted_at': lst.deleted_at.isoformat() if lst.deleted_at else None,
            })
        for rec in deleted_records:
            trash_items.append({
                'id': rec['id'],
                'type': 'record',
                'name': f'{rec["_list_name"]} / {str(rec["data"])[:50]}',
                'list_id': rec['_list_id'],
                'list_url': rec['_list_url'],
                'deleted_at': rec.get('updated_at'),
            })

        trash_items.sort(key=lambda x: x.get('deleted_at') or '', reverse=True)
        return Response(trash_items)

    def post(self, request, app_id, item_id):
        """恢复"""
        item_type = request.data.get('type')
        if item_type == 'list':
            lst = List.objects.get(id=item_id, application_id=app_id, is_deleted=True)
            lst.is_deleted = False
            lst.deleted_at = None
            lst.save(update_fields=['is_deleted', 'deleted_at'])
            return Response({'status': 'restored'})

        elif item_type == 'record':
            list_id = request.data.get('list_id')
            lst = List.objects.get(id=list_id, application_id=app_id)
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT data FROM "{lst.table_name}" WHERE id = %s', [item_id])
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    data['_is_deleted'] = False
                    data['_deleted_at'] = None
                    cursor.execute(
                        f'UPDATE "{lst.table_name}" SET data = %s, updated_at = NOW() WHERE id = %s',
                        [json.dumps(data, ensure_ascii=False, default=str), item_id]
                    )
            return Response({'status': 'restored'})

        return Response({'detail': 'Invalid type'}, status=400)

    def delete(self, request, app_id, item_id):
        """彻底删除"""
        item_type = request.query_params.get('type')
        if item_type == 'list':
            lst = List.objects.get(id=item_id, application_id=app_id, is_deleted=True)
            DynamicTableBuilder.drop_table(lst.table_name)
            lst.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        elif item_type == 'record':
            list_id = request.query_params.get('list_id')
            lst = List.objects.get(id=list_id, application_id=app_id)
            with connection.cursor() as cursor:
                cursor.execute(f'DELETE FROM "{lst.table_name}" WHERE id = %s', [item_id])
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Invalid type'}, status=400)
```

- [ ] **Step 2: 注册回收站路由到 data/urls.py**

```python
# Add to backend/data/urls.py
    path('apps/<uuid:app_id>/trash/', TrashView.as_view()),
    path('apps/<uuid:app_id>/trash/<uuid:item_id>/', TrashView.as_view()),
```

- [ ] **Step 3: Commit**

```bash
git add backend/data/trash.py backend/data/urls.py
git commit -m "feat: add trash manager with soft-delete, restore, and permanent delete"
```

---

## Phase 3: 前端搭建

### Task 12: Vue3 项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: 创建 package.json**

```bash
cd frontend && npm init -y
npm install vue vue-router element-plus @element-plus/icons-vue axios
npm install -D vite @vitejs/plugin-vue
```

- [ ] **Step 2: 创建 vite.config.js**

```js
// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 3: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>通用列表系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: 创建 main.js + App.vue + router**

```js
// frontend/src/main.js
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus, { locale: { el: { } } })
app.use(router)
app.mount('#app')
```

```vue
<!-- frontend/src/App.vue -->
<template>
  <router-view />
</template>
```

```js
// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/apps',
  },
  {
    path: '/apps',
    name: 'apps',
    component: () => import('../views/applications/AppList.vue'),
  },
  {
    path: '/apps/:appId/field-types',
    name: 'fieldTypes',
    component: () => import('../views/field-types/FieldTypeList.vue'),
  },
  {
    path: '/apps/:appId/content-types',
    name: 'contentTypes',
    component: () => import('../views/content-types/ContentTypeList.vue'),
  },
  {
    path: '/apps/:appId/content-types/:ctId',
    name: 'contentTypeDesigner',
    component: () => import('../views/content-types/ContentTypeDesigner.vue'),
  },
  {
    path: '/apps/:appId/lists',
    name: 'lists',
    component: () => import('../views/lists/ListManagement.vue'),
  },
  {
    path: '/apps/:appId/lists/:listId/design',
    name: 'listDesigner',
    component: () => import('../views/lists/ListDesigner.vue'),
  },
  {
    path: '/apps/:appId/lists/:listId/data',
    name: 'listData',
    component: () => import('../views/lists/ListData.vue'),
  },
  {
    path: '/apps/:appId/lists/:listId/data/add',
    name: 'recordAdd',
    component: () => import('../views/lists/RecordForm.vue'),
  },
  {
    path: '/apps/:appId/lists/:listId/data/:recordId/edit',
    name: 'recordEdit',
    component: () => import('../views/lists/RecordForm.vue'),
  },
  {
    path: '/apps/:appId/trash',
    name: 'trash',
    component: () => import('../views/trash/TrashPage.vue'),
  },
  {
    path: '/apps/:appId/navigations',
    name: 'navigations',
    component: () => import('../views/navigations/NavigationConfig.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

- [ ] **Step 5: 创建 API 实例**

```js
// frontend/src/api/index.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.detail || err.message
    return Promise.reject(new Error(msg))
  }
)

export default api
```

- [ ] **Step 6: 验证 dev server**

```bash
cd frontend && npx vite --host 0.0.0.0 &
```

Expected: Vite dev server running at http://localhost:3000

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: initialize Vue3 project with Element Plus, router, and axios"
```

---

### Task 13: 前端 API 模块

**Files:**
- Create: `frontend/src/api/applications.js`
- Create: `frontend/src/api/fieldTypes.js`
- Create: `frontend/src/api/contentTypes.js`
- Create: `frontend/src/api/lists.js`
- Create: `frontend/src/api/records.js`
- Create: `frontend/src/api/trash.js`

- [ ] **Step 1: 创建所有 API 模块**

```js
// frontend/src/api/applications.js
import api from './index'

export const getApps = () => api.get('/apps/')
export const getApp = (id) => api.get(`/apps/${id}/`)
export const createApp = (data) => api.post('/apps/', data)
export const updateApp = (id, data) => api.put(`/apps/${id}/`, data)
export const deleteApp = (id) => api.delete(`/apps/${id}/`)
export const getNavigations = (appId) => api.get(`/apps/${appId}/navigations/`)
export const createNavigation = (appId, data) => api.post(`/apps/${appId}/navigations/`, data)
export const updateNavigation = (appId, id, data) => api.put(`/apps/${appId}/navigations/${id}/`, data)
export const deleteNavigation = (appId, id) => api.delete(`/apps/${appId}/navigations/${id}/`)
```

```js
// frontend/src/api/fieldTypes.js
import api from './index'

export const getFieldTypes = () => api.get('/field-types/')
export const createFieldType = (data) => api.post('/field-types/', data)
export const updateFieldType = (id, data) => api.put(`/field-types/${id}/`, data)
export const deleteFieldType = (id) => api.delete(`/field-types/${id}/`)
export const getValidators = () => api.get('/validators/')
export const createValidator = (data) => api.post('/validators/', data)
export const updateValidator = (id, data) => api.put(`/validators/${id}/`, data)
export const deleteValidator = (id) => api.delete(`/validators/${id}/`)
```

```js
// frontend/src/api/contentTypes.js
import api from './index'

export const getContentTypes = () => api.get('/content-types/')
export const getContentType = (id) => api.get(`/content-types/${id}/`)
export const createContentType = (data) => api.post('/content-types/', data)
export const updateContentType = (id, data) => api.put(`/content-types/${id}/`, data)
export const deleteContentType = (id) => api.delete(`/content-types/${id}/`)
export const getCTFields = (ctId) => api.get(`/content-types/${ctId}/fields/`)
export const createCTField = (ctId, data) => api.post(`/content-types/${ctId}/fields/`, data)
export const updateCTField = (ctId, id, data) => api.put(`/content-types/${ctId}/fields/${id}/`, data)
export const deleteCTField = (ctId, id) => api.delete(`/content-types/${ctId}/fields/${id}/`)
```

```js
// frontend/src/api/lists.js
import api from './index'

export const getLists = (appId) => api.get(`/apps/${appId}/lists/`)
export const getList = (appId, id) => api.get(`/apps/${appId}/lists/${id}/`)
export const createList = (appId, data) => api.post(`/apps/${appId}/lists/`, data)
export const updateList = (appId, id, data) => api.put(`/apps/${appId}/lists/${id}/`, data)
export const deleteList = (appId, id) => api.delete(`/apps/${appId}/lists/${id}/`)
export const getListFields = (listId) => api.get(`/lists/${listId}/fields/`)
export const createListField = (listId, data) => api.post(`/lists/${listId}/fields/`, data)
export const updateListField = (listId, id, data) => api.put(`/lists/${listId}/fields/${id}/`, data)
export const deleteListField = (listId, id) => api.delete(`/lists/${listId}/fields/${id}/`)
export const getListViews = (listId) => api.get(`/lists/${listId}/views/`)
export const createListView = (listId, data) => api.post(`/lists/${listId}/views/`, data)
export const updateListView = (listId, id, data) => api.put(`/lists/${listId}/views/${id}/`, data)
export const deleteListView = (listId, id) => api.delete(`/lists/${listId}/views/${id}/`)
export const getFormSchema = (appId, listId) => api.get(`/apps/${appId}/lists/${listId}/form_schema/`)
```

```js
// frontend/src/api/records.js
import api from './index'

export const getRecords = (appId, listUrl, params) => api.get(`/apps/${appId}/lists/${listUrl}/records/`, { params })
export const getRecord = (appId, listUrl, id) => api.get(`/apps/${appId}/lists/${listUrl}/records/${id}/`)
export const createRecord = (appId, listUrl, data) => api.post(`/apps/${appId}/lists/${listUrl}/records/`, data)
export const updateRecord = (appId, listUrl, id, data) => api.put(`/apps/${appId}/lists/${listUrl}/records/${id}/`, data)
export const deleteRecord = (appId, listUrl, id) => api.delete(`/apps/${appId}/lists/${listUrl}/records/${id}/`)
export const batchUpdate = (appId, listUrl, data) => api.patch(`/apps/${appId}/lists/${listUrl}/records/batch/`, data)
```

```js
// frontend/src/api/trash.js
import api from './index'

export const getTrash = (appId) => api.get(`/apps/${appId}/trash/`)
export const restoreItem = (appId, id, data) => api.post(`/apps/${appId}/trash/${id}/`, data)
export const permanentDelete = (appId, id, params) => api.delete(`/apps/${appId}/trash/${id}/`, { params })
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/
git commit -m "feat: add all frontend API modules"
```

---

### Task 14: 前端校验规则引擎

**Files:**
- Create: `frontend/src/utils/ruleEngine.js`

- [ ] **Step 1: 创建 ruleEngine.js**

```js
// frontend/src/utils/ruleEngine.js

export function buildRules(field) {
  const rules = []
  const { required, field_type, config = {}, validators = [], name } = field

  if (required) {
    rules.push({ required: true, message: `${name}为必填`, trigger: 'blur' })
  }

  switch (field_type) {
    case 'text':
      if (config.max_length) {
        rules.push({ max: config.max_length, message: `最多${config.max_length}个字符`, trigger: 'blur' })
      }
      if (config.pattern) {
        rules.push({ pattern: new RegExp(config.pattern), message: '格式不正确', trigger: 'blur' })
      }
      break

    case 'number':
      if (config.min !== undefined && config.min !== null) {
        rules.push({ type: 'number', min: config.min, message: `最小值为${config.min}`, trigger: 'blur' })
      }
      if (config.max !== undefined && config.max !== null) {
        rules.push({ type: 'number', max: config.max, message: `最大值为${config.max}`, trigger: 'blur' })
      }
      break

    case 'long_text':
      if (config.max_length) {
        rules.push({ max: config.max_length, message: `最多${config.max_length}个字符`, trigger: 'blur' })
      }
      break

    case 'multi_select':
      if (config.min_count) {
        rules.push({ type: 'array', min: config.min_count, message: `至少选择${config.min_count}项`, trigger: 'change' })
      }
      if (config.max_count) {
        rules.push({ type: 'array', max: config.max_count, message: `最多选择${config.max_count}项`, trigger: 'change' })
      }
      break
  }

  // Apply custom validator rules
  for (const v of validators) {
    if (v.rule_type === 'regex') {
      rules.push({ pattern: new RegExp(v.pattern), message: v.error_message || '格式不正确', trigger: 'blur' })
    }
  }

  return rules
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/utils/ruleEngine.js
git commit -m "feat: add frontend validation rule engine"
```

---

### Task 15: 核心组件 + 页面实现

**Files:**
- Create: `frontend/src/components/AppLayout.vue`
- Create: `frontend/src/components/AppSidebar.vue`
- Create: `frontend/src/components/DynamicForm.vue`
- Create: `frontend/src/components/DynamicSearchBar.vue`
- Create: `frontend/src/components/ViewTabs.vue`
- Create: 所有 views/*.vue 文件

- [ ] **Step 1: AppLayout + AppSidebar**

```vue
<!-- frontend/src/components/AppLayout.vue -->
<template>
  <el-container style="min-height:100vh">
    <el-aside width="220px">
      <AppSidebar />
    </el-aside>
    <el-container>
      <el-header style="background:#fff;border-bottom:1px solid #e4e7ed;display:flex;align-items:center;padding:0 20px;">
        <h3 style="margin:0;">{{ pageTitle }}</h3>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './AppSidebar.vue'

const route = useRoute()
const pageTitle = computed(() => route.meta.title || '通用列表系统')
</script>
```

```vue
<!-- frontend/src/components/AppSidebar.vue -->
<template>
  <div style="background:#304156;color:#fff;height:100%;padding:16px 0;">
    <div style="padding:0 20px 16px;font-size:18px;font-weight:bold;">通用列表系统</div>
    <el-menu
      :default-active="route.path"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409eff"
      router
      style="border-right:none;"
    >
      <el-menu-item :index="`/apps/${appId}/lists`">
        <el-icon><List /></el-icon>
        <span>列表管理</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/content-types`">
        <el-icon><Document /></el-icon>
        <span>内容类型</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/field-types`">
        <el-icon><Setting /></el-icon>
        <span>字段类型</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/navigations`">
        <el-icon><Menu /></el-icon>
        <span>菜单配置</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/trash`">
        <el-icon><Delete /></el-icon>
        <span>回收站</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { List, Document, Setting, Menu, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const appId = route.params.appId
</script>
```

- [ ] **Step 2: DynamicForm 组件**

```vue
<!-- frontend/src/components/DynamicForm.vue -->
<template>
  <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
    <el-form-item
      v-for="field in fields"
      :key="field.key"
      :label="field.name"
      :prop="field.key"
    >
      <!-- Text / Long Text -->
      <el-input
        v-if="field.field_type === 'text' || field.field_type === 'long_text'"
        v-model="formData[field.key]"
        :type="field.field_type === 'long_text' ? 'textarea' : 'text'"
        :rows="field.field_type === 'long_text' ? 6 : 1"
        :placeholder="`请输入${field.name}`"
      />

      <!-- Number -->
      <el-input-number
        v-else-if="field.field_type === 'number'"
        v-model="formData[field.key]"
        :min="field.config?.min"
        :max="field.config?.max"
      />

      <!-- Date -->
      <el-date-picker
        v-else-if="field.field_type === 'date'"
        v-model="formData[field.key]"
        type="date"
        value-format="YYYY-MM-DD"
        :placeholder="`请选择${field.name}`"
      />

      <!-- Boolean -->
      <el-switch v-else-if="field.field_type === 'boolean'" v-model="formData[field.key]" />

      <!-- Select -->
      <el-select
        v-else-if="field.field_type === 'select'"
        v-model="formData[field.key]"
        :placeholder="`请选择${field.name}`"
      >
        <el-option
          v-for="opt in field.options"
          :key="opt"
          :label="opt"
          :value="opt"
        />
      </el-select>

      <!-- Multi Select -->
      <el-select
        v-else-if="field.field_type === 'multi_select'"
        v-model="formData[field.key]"
        multiple
        :placeholder="`请选择${field.name}`"
      >
        <el-option
          v-for="opt in field.options"
          :key="opt"
          :label="opt"
          :value="opt"
        />
      </el-select>

      <!-- Default -->
      <el-input v-else v-model="formData[field.key]" :placeholder="`请输入${field.name}`" />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { buildRules } from '../utils/ruleEngine'

const props = defineProps({
  fields: { type: Array, default: () => [] },
  initialData: { type: Object, default: () => ({}) },
})

const formRef = ref(null)
const formData = reactive({ ...props.initialData })

const formRules = reactive({})
watch(() => props.fields, (fields) => {
  for (const f of fields) {
    formRules[f.key] = buildRules(f)
    if (!(f.key in formData)) {
      formData[f.key] = f.field_type === 'multi_select' ? [] : f.field_type === 'boolean' ? false : ''
    }
  }
}, { immediate: true })

const validate = () => formRef.value?.validate()
const getData = () => ({ ...formData })

defineExpose({ validate, getData })
</script>
```

- [ ] **Step 3: ViewTabs + DynamicSearchBar**

```vue
<!-- frontend/src/components/ViewTabs.vue -->
<template>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
    <el-tag
      v-for="v in views"
      :key="v.url_key"
      :type="activeKey === v.url_key ? '' : 'info'"
      :effect="activeKey === v.url_key ? 'dark' : 'plain'"
      style="cursor:pointer;"
      @click="$emit('change', v.url_key)"
    >
      {{ v.name }}
    </el-tag>
    <el-button size="small" type="primary" link @click="$emit('add')">+ 新建视图</el-button>
  </div>
</template>

<script setup>
defineProps({
  views: { type: Array, default: () => [] },
  activeKey: { type: String, default: 'default' },
})
defineEmits(['change', 'add'])
</script>
```

```vue
<!-- frontend/src/components/DynamicSearchBar.vue -->
<template>
  <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px;">
    <template v-for="field in searchableFields" :key="field.key">
      <el-select
        v-if="field.field_type === 'select' || field.field_type === 'boolean'"
        v-model="filters[field.key]"
        :placeholder="field.name"
        clearable
        style="width:150px;"
        @change="emitSearch"
      >
        <el-option
          v-if="field.field_type === 'boolean'"
          v-for="opt in [{label:'是',value:'true'},{label:'否',value:'false'}]"
          :key="opt.value" :label="opt.label" :value="opt.value"
        />
        <el-option
          v-else
          v-for="opt in (field.options || [])"
          :key="opt" :label="opt" :value="opt"
        />
      </el-select>
      <el-input
        v-else
        v-model="filters[field.key]"
        :placeholder="field.name"
        clearable
        style="width:180px;"
        @change="emitSearch"
      />
    </template>
    <el-button @click="$emit('reset')">重置</el-button>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  searchableFields: { type: Array, default: () => [] },
})

const emit = defineEmits(['search', 'reset'])
const filters = reactive({})

const emitSearch = () => {
  const parts = []
  for (const [k, v] of Object.entries(filters)) {
    if (v !== '' && v !== null && v !== undefined) {
      const field = props.searchableFields.find(f => f.key === k)
      if (field) {
        const op = field.search_type === 'fuzzy' ? 'contains' : 'eq'
        parts.push(`${k}:${op}:${v}`)
      }
    }
  }
  emit('search', parts.join(','))
}
</script>
```

- [ ] **Step 4: 关键页面 — ListData.vue (数据表格)**

```vue
<!-- frontend/src/views/lists/ListData.vue -->
<template>
  <AppLayout>
    <div v-if="loading">加载中...</div>
    <template v-else>
      <ViewTabs
        :views="views"
        :activeKey="activeView"
        @change="switchView"
        @add="showAddViewDialog = true"
      />

      <DynamicSearchBar
        :searchableFields="searchableFields"
        @search="onSearch"
        @reset="resetSearch"
      />

      <div style="margin-bottom:12px;display:flex;gap:8px;">
        <el-button type="primary" @click="$router.push(`/apps/${appId}/lists/${listId}/data/add`)">新增</el-button>
        <el-button
          :disabled="selectedRows.length === 0"
          @click="showBatchEdit = true"
        >
          批量编辑
        </el-button>
      </div>

      <el-table
        :data="records"
        @selection-change="onSelectionChange"
        stripe
        border
        style="width:100%;"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column
          v-for="col in visibleColumns"
          :key="col.key"
          :prop="`data.${col.key}`"
          :label="col.name"
          :sortable="col.sortable"
        />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/apps/${appId}/lists/${listId}/data/${row.id}/edit`)">编辑</el-button>
            <el-popconfirm title="确认删除?" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end;"
        @current-change="loadData"
      />
    </template>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../../components/AppLayout.vue'
import ViewTabs from '../../components/ViewTabs.vue'
import DynamicSearchBar from '../../components/DynamicSearchBar.vue'
import { getList, getListViews, getFormSchema } from '../../api/lists'
import { getRecords, deleteRecord, batchUpdate } from '../../api/records'

const route = useRoute()
const appId = route.params.appId
const listId = route.params.listId

const loading = ref(true)
const views = ref([])
const activeView = ref('default')
const allFields = ref([])
const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterStr = ref('')
const selectedRows = ref([])

const searchableFields = computed(() => allFields.value.filter(f => f.searchable))
const visibleColumns = computed(() => {
  const currentView = views.value.find(v => v.url_key === activeView.value)
  if (currentView?.config?.visible_fields?.length) {
    return allFields.value.filter(f => currentView.config.visible_fields.includes(f.key))
  }
  return allFields.value
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterStr.value) params.filter = filterStr.value
    if (activeView.value) params.view = activeView.value
    const res = await getRecords(appId, listId, params)
    records.value = res.results
    total.value = res.total
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const [schemaRes, viewsRes] = await Promise.all([
    getFormSchema(appId, listId),
    getListViews(listId),
  ])
  allFields.value = schemaRes.fields
  views.value = viewsRes
  await loadData()
})

const onSearch = (f) => { filterStr.value = f; page.value = 1; loadData() }
const resetSearch = () => { filterStr.value = ''; page.value = 1; loadData() }
const switchView = (key) => { activeView.value = key; loadData() }
const onSelectionChange = (rows) => { selectedRows.value = rows }
const handleDelete = async (id) => {
  await deleteRecord(appId, listId, id)
  loadData()
}
</script>
```

- [ ] **Step 5: RecordForm.vue (新增/编辑页面)**

```vue
<!-- frontend/src/views/lists/RecordForm.vue -->
<template>
  <AppLayout>
    <el-page-header @back="$router.back()" :content="isEdit ? '编辑记录' : '新增记录'" />
    <el-card style="margin-top:16px;max-width:800px;">
      <DynamicForm ref="formRef" :fields="fields" :initialData="initialData" />
      <div style="margin-top:20px;">
        <el-button type="primary" @click="submit" :loading="submitting">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '../../components/AppLayout.vue'
import DynamicForm from '../../components/DynamicForm.vue'
import { getFormSchema } from '../../api/lists'
import { getRecord, createRecord, updateRecord } from '../../api/records'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId
const listId = route.params.listId
const recordId = route.params.recordId
const isEdit = computed(() => !!recordId)

const fields = ref([])
const initialData = ref({})
const formRef = ref(null)
const submitting = ref(false)

onMounted(async () => {
  const schema = await getFormSchema(appId, listId)
  fields.value = schema.fields
  if (isEdit.value) {
    const record = await getRecord(appId, listId, recordId)
    initialData.value = record.data || {}
  }
})

const submit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const data = formRef.value.getData()
    if (isEdit.value) {
      await updateRecord(appId, listId, recordId, data)
    } else {
      await createRecord(appId, listId, data)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    router.push(`/apps/${appId}/lists/${listId}/data`)
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    submitting.value = false
  }
}
</script>
```

- [ ] **Step 6: 其余关键页面 (AppList, ContentTypeList, ContentTypeDesigner, ListManagement, ListDesigner, TrashPage, NavigationConfig)**

```vue
<!-- frontend/src/views/applications/AppList.vue -->
<template>
  <div style="padding:20px;">
    <h2>应用列表</h2>
    <el-button type="primary" @click="showCreate = true">新建应用</el-button>
    <el-table :data="apps" style="margin-top:16px;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="key" label="标识" />
      <el-table-column prop="url_prefix" label="URL前缀" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/apps/${row.id}/lists`)">进入</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建应用">
      <el-form :model="form">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="标识"><el-input v-model="form.key" /></el-form-item>
        <el-form-item label="URL前缀"><el-input v-model="form.url_prefix" placeholder="/" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getApps, createApp } from '../../api/applications'
import { ElMessage } from 'element-plus'

const apps = ref([])
const showCreate = ref(false)
const form = ref({ name: '', key: '', url_prefix: '/', description: '' })

onMounted(async () => { apps.value = await getApps() })

const handleCreate = async () => {
  await createApp(form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  apps.value = await getApps()
}
</script>
```

Remaining pages use a similar CRUD pattern with Element Plus table + dialog. Due to length constraints, the pattern is:
- **ContentTypeList.vue**: Table with CRUD, "设计" button navigates to ContentTypeDesigner
- **ContentTypeDesigner.vue**: Parent selector + field list (drag-to-reorder with add/edit/delete dialogs)
- **ListManagement.vue**: Table of lists, create with content_type selector or manual field mode
- **ListDesigner.vue**: Field list builder (similar to ContentTypeDesigner but for ListField)
- **TrashPage.vue**: Two tabs (deleted lists / deleted records) with restore and permanent-delete buttons
- **NavigationConfig.vue**: Tree-based menu builder

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add all frontend views and components"
```

---

## Phase 4: 集成验证

### Task 16: 端到端验证

- [ ] **Step 1: 启动后端**

```bash
cd backend && python manage.py runserver 8000 &
```

Expected: Django 服务器运行在 8000 端口。

- [ ] **Step 2: 验证创建默认应用**

```bash
curl http://localhost:8000/api/apps/
```

Expected: 返回包含"通用列表存储"应用的 JSON。

- [ ] **Step 3: 验证字段类型 API**

```bash
curl http://localhost:8000/api/field-types/ | python -c "import sys,json; data=json.load(sys.stdin); print(f'{len(data)} field types loaded')"
```

Expected: "9 field types loaded"

- [ ] **Step 4: 验证完整流程 — 创建内容类型、列表、写入数据**

```bash
# 创建内容类型
CT_ID=$(curl -s -X POST http://localhost:8000/api/content-types/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"文章","key":"article","description":"文章内容类型"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 添加字段到内容类型
APP_ID=$(curl -s http://localhost:8000/api/apps/ | python -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
TEXT_FT_ID=$(curl -s http://localhost:8000/api/field-types/ | python -c "import sys,json; print([ft['id'] for ft in json.load(sys.stdin) if ft['key']=='text'][0])")

curl -s -X POST "http://localhost:8000/api/content-types/$CT_ID/fields/" \
  -H 'Content-Type: application/json' \
  -d "{\"field_type\":\"$TEXT_FT_ID\",\"name\":\"标题\",\"key\":\"title\",\"required\":true}" > /dev/null

# 创建列表
LIST_ID=$(curl -s -X POST "http://localhost:8000/api/apps/$APP_ID/lists/" \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"博客列表\",\"key\":\"blog\",\"content_type\":\"$CT_ID\",\"url\":\"/list1\"}" \
  | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "List created: $LIST_ID"

# 写入数据
curl -s -X POST "http://localhost:8000/api/apps/$APP_ID/lists/list1/records/" \
  -H 'Content-Type: application/json' \
  -d '{"title":"第一篇文章"}'

echo "Record created"

# 查询数据
curl -s "http://localhost:8000/api/apps/$APP_ID/lists/list1/records/" | python -c "import sys,json; d=json.load(sys.stdin); print(f'{d[\"total\"]} records, first: {d[\"results\"][0][\"data\"][\"title\"]}')"
```

Expected: "1 records, first: 第一篇文章"

- [ ] **Step 4: 启动前端**

```bash
cd frontend && npx vite &
```

Expected: Vite 运行在 3000 端口，可访问 http://localhost:3000

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: end-to-end integration verified"
```
