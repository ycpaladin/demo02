"""生成测试数据：100个随机字段 + 100000条记录"""
import json
import uuid
import random
import string
import sys
from datetime import datetime, timedelta

# Django setup
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from metadata.models import List
from django.db import connection

FIELD_TYPES = ['text', 'number', 'date', 'boolean', 'select']
FIELD_PREFIXES = [
    'field', 'attr', 'prop', 'data', 'info', 'meta', 'param', 'cfg', 'opt', 'val',
    'score', 'rating', 'level', 'status', 'type', 'category', 'tag', 'label', 'note', 'desc',
]

def generate_random_field(i):
    prefix = random.choice(FIELD_PREFIXES)
    ft = random.choice(FIELD_TYPES)
    key = f"{prefix}_{i}"
    name = f"{prefix}_{i}"

    config = {}
    if ft == 'select':
        opts = [random.choice(['A', 'B', 'C', 'D', 'E']) for _ in range(random.randint(2, 5))]
        config = {'options': list(set(opts)), 'select_type': random.choice(['single', 'multiple']), 'select_display': random.choice(['radio', 'dropdown'])}
    elif ft == 'number':
        config = {'min_value': 0, 'max_value': random.randint(100, 10000), 'precision': random.choice([0, 1, 2])}
    elif ft == 'text':
        config = {'text_type': random.choice(['single_line', 'multi_line', 'long_text'])}

    return {
        'key': key,
        'name': name,
        'field_type': ft,
        'required': random.choice([True, False]),
        'unique': random.choice([False, False, False, True]),  # 25% unique
        'searchable': random.choice([True, False]),
        'search_type': random.choice(['exact', 'contains']),
        'order': i,
        'config': config,
        'validators': [],
    }

def rand_value(ft, config):
    if ft == 'text':
        text_type = config.get('text_type', 'single_line')
        if text_type == 'long_text':
            return ''.join(random.choices(string.ascii_letters + ' ', k=random.randint(20, 200)))
        return ''.join(random.choices(string.ascii_letters, k=random.randint(3, 20)))
    elif ft == 'number':
        mn = config.get('min_value', 0)
        mx = config.get('max_value', 1000)
        prec = config.get('precision', 0)
        v = random.uniform(mn, mx)
        return round(v, prec) if prec > 0 else int(v)
    elif ft == 'date':
        start = datetime(2020, 1, 1)
        end = datetime(2026, 5, 17)
        delta = end - start
        d = start + timedelta(days=random.randint(0, delta.days))
        return d.strftime('%Y-%m-%d')
    elif ft == 'boolean':
        return random.choice([True, False])
    elif ft == 'select':
        opts = config.get('options', ['A', 'B'])
        st = config.get('select_type', 'single')
        if st == 'multiple':
            return random.sample(opts, k=random.randint(1, min(3, len(opts))))
        return random.choice(opts)
    return ''

def main():
    list_id = sys.argv[1] if len(sys.argv) > 1 else '6eb18686-dfe1-42f1-b1df-0bf6b2a76876'

    try:
        lst = List.objects.get(id=list_id, is_deleted=False)
    except List.DoesNotExist:
        print(f"List {list_id} not found")
        return

    print(f"List: {lst.name} (table: {lst.table_name})")

    # 1. Generate and save 100 extension fields
    print("Generating 100 extension fields...")
    ext_fields = [generate_random_field(i) for i in range(100)]
    # Assign IDs to new fields
    for f in ext_fields:
        f['id'] = str(uuid.uuid4())

    # Get inherited field keys
    inherited_fields = []
    if lst.content_type:
        from metadata.managers import ContentTypeManager
        inherited_fields = [f['key'] for f in ContentTypeManager.resolve_fields(lst.content_type)]
    print(f"Inherited fields: {inherited_fields}")

    # Save schema
    schema = lst.schema or {}
    schema['fields'] = ext_fields
    lst.schema = schema
    lst.save(update_fields=['schema', 'updated_at'])
    print(f"Saved {len(ext_fields)} extension fields to schema")

    # 2. Generate 100,000 records in batches
    total = 100000
    batch_size = 500
    all_field_keys = inherited_fields + [f['key'] for f in ext_fields]
    all_field_types = {f['key']: (f['field_type'], f.get('config', {})) for f in ext_fields}
    # Add inherited field types (we only have 'title' as text)
    for k in inherited_fields:
        all_field_types[k] = ('text', {})

    print(f"Total fields: {len(all_field_keys)}")
    print(f"Generating {total} records in batches of {batch_size}...")

    table_name = lst.table_name
    conn = connection

    # Use bulk insert for speed
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        values_list = []
        params_list = []

        for _ in range(batch_start, batch_end):
            record_id = str(uuid.uuid4())
            data = {'_is_deleted': False, '_deleted_at': None}
            for key in all_field_keys:
                ft, cfg = all_field_types.get(key, ('text', {}))
                data[key] = rand_value(ft, cfg)

            values_list.append(f"(%s, %s)")
            params_list.extend([record_id, json.dumps(data, ensure_ascii=False, default=str)])

        sql = f'INSERT INTO "{table_name}" (id, data) VALUES ' + ', '.join(values_list)
        with conn.cursor() as cursor:
            cursor.execute(sql, params_list)

        pct = (batch_end / total) * 100
        print(f"  {batch_end:,}/{total:,} ({pct:.0f}%)")

    # Verify
    with conn.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}" WHERE data->>\'_is_deleted\' IS NULL OR data->>\'_is_deleted\' = \'false\'')
        count = cursor.fetchone()[0]
        print(f"\nDone! Total active records: {count:,}")

    # Show table size
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT pg_size_pretty(pg_total_relation_size('\"{table_name}\"'))")
        size = cursor.fetchone()[0]
        print(f"Table size: {size}")

if __name__ == '__main__':
    main()
