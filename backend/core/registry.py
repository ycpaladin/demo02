from core.models import FieldType

SEARCH_TYPE_MAP = {
    'text': 'fuzzy',
    'number': 'range',
    'date': 'range',
    'boolean': 'exact',

    'select': 'exact',

    'attachment': None,
    'reference': 'exact',
    'auto_number': 'exact',
    'computed': None,
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
