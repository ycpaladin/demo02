from django.db import connection


class DynamicTableBuilder:
    @classmethod
    def create_table(cls, table_name):
        sql = f"""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U')
        BEGIN
            CREATE TABLE [{table_name}] (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWSEQUENTIALID(),
                data NVARCHAR(MAX) NOT NULL,
                created_at DATETIME2 DEFAULT GETDATE(),
                updated_at DATETIME2 DEFAULT GETDATE()
            )
        END
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)

    @classmethod
    def drop_table(cls, table_name):
        sql = f"""
        IF EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U')
        BEGIN
            DROP TABLE [{table_name}]
        END
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)

    @classmethod
    def add_computed_column(cls, table_name, field_key):
        col_name = f"{field_key}_c"
        sql = f"""
        IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name='{col_name}' AND Object_ID=Object_ID('{table_name}'))
        BEGIN
            ALTER TABLE [{table_name}] ADD [{col_name}] AS JSON_VALUE(data, '$.{field_key}')
        END
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
