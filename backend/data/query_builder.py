from django.db import connection


class QueryBuilder:
    OP_MAP = {
        'eq': '=', 'neq': '!=', 'contains': 'LIKE',
        'startswith': 'LIKE', 'gt': '>', 'gte': '>=', 'lt': '<', 'lte': '<=',
    }

    COMPARISON_SQL = {
        '=': '=', '!=': '!=', '<>': '!=',
        '>': '>', '>=': '>=', '<': '<', '<=': '<=',
        '包含': 'LIKE',
    }

    @classmethod
    def _build_where_node(cls, node):
        if not node:
            return '', []

        if 'logic' in node and 'left' in node:
            left_clause, left_params = cls._build_where_node(node['left'])
            right_clause, right_params = cls._build_where_node(node.get('right', {}))
            logic = node['logic']
            if right_clause:
                return f"({left_clause} {logic} {right_clause})", left_params + right_params
            return left_clause, left_params
        elif 'field' in node:
            field = node['field']
            comparison = node.get('comparison', '=')
            value = node.get('value', '')
            sql_op = cls.COMPARISON_SQL.get(comparison, '=')

            if sql_op == 'LIKE':
                return f"data->>'{field}' LIKE %s", [f'%{value}%']
            elif comparison in ('!=', '<>'):
                return f"(data->>'{field}' IS NULL OR data->>'{field}' != %s)", [str(value)]
            else:
                return f"data->>'{field}' {sql_op} %s", [str(value)]

        return '', []

    @classmethod
    def build_where_from_json(cls, where):
        if not where:
            return '', []
        return cls._build_where_node(where)

    @classmethod
    def build_filter_clause(cls, filter_str):
        if not filter_str:
            return '', []

        clauses, params = [], []
        for part in filter_str.split(','):
            parts = part.split(':', 2)
            if len(parts) < 3:
                continue
            key, op, value = parts[0], parts[1], parts[2]
            if op == 'isnull':
                clauses.append(f"data->>'{key}' IS NULL")
                continue
            if op in ('in', 'nin'):
                values = [v.strip() for v in value.split('|')]
                placeholders = ','.join(['%s'] * len(values))
                not_ = 'NOT' if op == 'nin' else ''
                clauses.append(f"data->>'{key}' {not_} IN ({placeholders})")
                params.extend(values)
                continue
            if op == 'contains':
                clauses.append(f"data->>'{key}' LIKE %s")
                params.append(f'%{value}%')
            elif op == 'startswith':
                clauses.append(f"data->>'{key}' LIKE %s")
                params.append(f'{value}%')
            else:
                sql_op = cls.OP_MAP.get(op, '=')
                clauses.append(f"data->>'{key}' {sql_op} %s")
                params.append(value)

        where = ' AND '.join(clauses)
        return f'({where})' if where else '', params

    @classmethod
    def _extract_or_branches(cls, node):
        """从 JSON 顶层 OR 提取各个分支的 (clause, params)"""
        if not node or 'logic' not in node:
            return None

        branches = []

        def collect(node):
            if node.get('logic') == 'OR':
                collect(node['left'])
                if node.get('right'):
                    collect(node['right'])
            else:
                clause, params = cls._build_where_node(node)
                if clause:
                    branches.append((clause, params))

        collect(node)
        return branches if len(branches) >= 2 else None

    @classmethod
    def _build_union_select(cls, table_name, branches, order_clause, offset, limit):
        deleted = 'is_deleted = FALSE'
        subqueries = [
            f'SELECT id, data, created_at, updated_at FROM "{table_name}" WHERE {clause} AND {deleted}'
            for clause, _ in branches
        ]
        union = ' UNION ALL '.join(subqueries)
        return f'SELECT * FROM ({union}) t {order_clause} OFFSET {offset} LIMIT {limit}'

    @classmethod
    def _build_union_count(cls, table_name, branches):
        deleted = 'is_deleted = FALSE'
        subqueries = [
            f'SELECT id FROM "{table_name}" WHERE {clause} AND {deleted}'
            for clause, _ in branches
        ]
        union = ' UNION ALL '.join(subqueries)
        return f'SELECT COUNT(DISTINCT id) FROM ({union}) t'

    @classmethod
    def build_select(cls, table_name, filter_str='', sort='', order='asc',
                     page=1, page_size=20, where_json=None):
        # 排序
        SYSTEM_COLUMNS = {'id', 'created_at', 'updated_at'}
        if sort:
            sort_parts = []
            for s in sort.split(','):
                s = s.strip()
                if ':' in s:
                    fk, sd = s.split(':', 1)
                else:
                    fk, sd = s, order
                dir_sql = 'DESC' if sd.strip().upper() == 'DESC' else 'ASC'
                if fk in SYSTEM_COLUMNS:
                    sort_parts.append(f'"{fk}" {dir_sql}')
                else:
                    sort_parts.append(f"data->>'{fk}' {dir_sql}")
            order_clause = "ORDER BY " + ", ".join(sort_parts)
        else:
            order_clause = 'ORDER BY "id" ASC'

        offset = (page - 1) * page_size
        deleted_filter = 'is_deleted = FALSE'

        # 顶层 OR → UNION ALL
        or_branches = cls._extract_or_branches(where_json) if where_json else None
        if or_branches:
            count_sql = cls._build_union_count(table_name, or_branches)
            select_sql = cls._build_union_select(table_name, or_branches, order_clause, offset, page_size)
            params = [p for _, bp in or_branches for p in bp]
            return count_sql, select_sql, params

        # 标准 WHERE
        if where_json:
            where, params = cls.build_where_from_json(where_json)
        else:
            where, params = cls.build_filter_clause(filter_str)

        if where:
            where = f"{where} AND {deleted_filter}"
        else:
            where = deleted_filter

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
    def execute_query(cls, table_name, filter_str='', sort='', order='asc',
                      page=1, page_size=20, where_json=None):
        count_sql, select_sql, params = cls.build_select(
            table_name, filter_str, sort, order, page, page_size, where_json,
        )

        with connection.cursor() as cursor:
            cursor.execute(count_sql, params[:len(params)])
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
