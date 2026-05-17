from rest_framework import serializers


class ValidationEngine:

    @classmethod
    def build_field(cls, field_def, validators_map):
        ft_key = field_def['field_type__key'] if isinstance(field_def.get('field_type__key'), str) else field_def.get('field_type__key', {}).get('key', 'text')
        required = field_def.get('required', False)
        config = field_def.get('config') or {}
        validator_keys = field_def.get('validators') or []

        drf_field, extra_kwargs = cls._field_for_type(ft_key, required, config)
        extra_kwargs['required'] = required

        if field_def.get('unique'):
            extra_kwargs['validators'] = extra_kwargs.get('validators', []) + [UniqueValidator(field_def['key'])]

        for vk in validator_keys:
            if vk in validators_map:
                v = validators_map[vk]
                if v.rule_type == 'regex':
                    extra_kwargs.setdefault('validators', []).append(
                        serializers.RegexValidator(regex=v.rule_config.get('pattern', ''), message=v.error_message)
                    )
                elif v.rule_type == 'range':
                    cfg = v.rule_config
                    if cfg.get('min') is not None:
                        extra_kwargs.setdefault('validators', []).append(
                            serializers.MinValueValidator(cfg['min'], message=v.error_message)
                        )
                    if cfg.get('max') is not None:
                        extra_kwargs.setdefault('validators', []).append(
                            serializers.MaxValueValidator(cfg['max'], message=v.error_message)
                        )

        field_kwargs = {k: v for k, v in extra_kwargs.items() if k != 'validators'}
        field_instance = drf_field(**field_kwargs)
        validators = extra_kwargs.get('validators', [])
        for validator in validators:
            field_instance.validators.append(validator)
        return field_instance

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

            'select': (serializers.CharField, {
                'allow_blank': not required,
            }),

            'attachment': (serializers.JSONField, {}),
            'reference': (serializers.CharField, {
                'allow_blank': not required,
            }),
            'auto_number': (serializers.CharField, {
                'required': False, 'read_only': True, 'max_length': 100,
            }),
            'computed': (serializers.CharField, {
                'required': False, 'read_only': True,
            }),
        }
        default = (serializers.CharField, {'allow_blank': not required, 'max_length': 255})
        field_class, kwargs = fields.get(ft_key, default)
        return field_class, kwargs

    @classmethod
    def build_frontend_rules(cls, field_def, validators_map):
        rules = []
        ft_key = field_def['field_type__key'] if isinstance(field_def.get('field_type__key'), str) else field_def.get('field_type__key', {}).get('key', 'text')
        required = field_def.get('required', False)
        config = field_def.get('config') or {}
        validator_keys = field_def.get('validators') or []

        if required:
            rules.append({'required': True, 'message': f'{field_def.get("name", "")}为必填', 'trigger': 'blur'})

        if ft_key == 'text':
            max_len = config.get('max_length', 255)
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
        pass

    def __eq__(self, other):
        return isinstance(other, UniqueValidator) and self.field_key == other.field_key
