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
        if not filter_str:
            return '', []

        clauses = []
        params = []

        for part in filter_str.split(','):
            parts = part.split(':', 2)
            if len(parts) < 3:
                continue
            key, op, value = parts[0], parts[1], parts[2]

            json_path = f"$.{key}"

            if op == 'isnull':
                clauses.append(f"JSON_VALUE(data, '{json_path}') IS NULL")
                continue

            if op in ('in', 'nin'):
                values = [v.strip() for v in value.split('|')]
                placeholders = ','.join(['%s'] * len(values))
                not_ = 'NOT' if op == 'nin' else ''
                clauses.append(f"JSON_VALUE(data, '{json_path}') {not_} IN ({placeholders})")
                params.extend(values)
                continue

            if op == 'contains':
                clauses.append(f"JSON_VALUE(data, '{json_path}') LIKE %s")
                params.append(f'%{value}%')
            elif op == 'startswith':
                clauses.append(f"JSON_VALUE(data, '{json_path}') LIKE %s")
                params.append(f'{value}%')
            else:
                sql_op = cls.OP_MAP.get(op, '=')
                clauses.append(f"JSON_VALUE(data, '{json_path}') {sql_op} %s")
                params.append(value)

        where = ' AND '.join(clauses)
        return f'({where})' if where else '', params

    @classmethod
    def build_select(cls, table_name, filter_str='', sort='', order='asc', page=1, page_size=20):
        where, params = cls.build_filter_clause(filter_str)

        deleted_filter = "(JSON_VALUE(data, '$._is_deleted') IS NULL OR JSON_VALUE(data, '$._is_deleted') = 'false')"
        if where:
            where = f"{where} AND {deleted_filter}"
        else:
            where = deleted_filter

        order_clause = ''
        if sort:
            direction = 'DESC' if order.lower() == 'desc' else 'ASC'
            order_clause = f"ORDER BY JSON_VALUE(data, '$.{sort}') {direction}"

        offset = (page - 1) * page_size

        count_sql = f"SELECT COUNT(*) FROM [{table_name}] WHERE {where}"
        select_sql = f"""
        SELECT id, data, created_at, updated_at
        FROM [{table_name}]
        WHERE {where}
        {order_clause}
        OFFSET {offset} ROWS
        FETCH NEXT {page_size} ROWS ONLY
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
