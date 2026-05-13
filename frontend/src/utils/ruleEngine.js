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

  for (const v of validators) {
    if (v.rule_type === 'regex') {
      rules.push({ pattern: new RegExp(v.pattern), message: v.error_message || '格式不正确', trigger: 'blur' })
    }
  }

  return rules
}
