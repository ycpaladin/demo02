import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FieldType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, default='', max_length=500)),
                ('icon', models.CharField(blank=True, default='', max_length=50)),
                ('builtin', models.BooleanField(default=False)),
                ('config_schema', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'db_table': 'field_types',
                'ordering': ['builtin', 'created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FieldValidator',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, default='', max_length=500)),
                ('builtin', models.BooleanField(default=False)),
                ('rule_type', models.CharField(max_length=50)),
                ('rule_config', models.JSONField(default=dict)),
                ('error_message', models.CharField(default='验证失败', max_length=200)),
            ],
            options={
                'db_table': 'field_validators',
                'ordering': ['builtin', 'created_at'],
                'abstract': False,
            },
        ),
    ]
