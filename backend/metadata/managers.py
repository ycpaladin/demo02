from collections import OrderedDict


def _field_to_dict(f):
    """Convert a field (model instance or dict) to a standard dict."""
    if isinstance(f, dict):
        return f
    return {
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


class ContentTypeManager:
    @classmethod
    def resolve_fields(cls, content_type):
        fields = OrderedDict()

        if content_type.parent:
            parent_fields = cls.resolve_fields(content_type.parent)
            for f in parent_fields:
                d = _field_to_dict(f)
                fields[d['key']] = d

        for f in content_type.fields.all():
            d = _field_to_dict(f)
            fields[d['key']] = d

        return list(fields.values())
