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
