import type { FormField, FormRule } from '../types'

export function buildRules(field: FormField): FormRule[] {
  const rules: FormRule[] = []
  const { required, field_type, config = {}, validators = [], name } = field

  if (required) {
    rules.push({ required: true, message: `${name}为必填`, trigger: 'blur' })
  }

  switch (field_type) {
    case 'text':
      if (config.max_length && typeof config.max_length === 'number') {
        rules.push({ max: config.max_length, message: `最多${config.max_length}个字符`, trigger: 'blur' })
      }
      if (config.pattern && typeof config.pattern === 'string') {
        rules.push({ pattern: config.pattern, message: '格式不正确', trigger: 'blur' })
      }
      break
    case 'number':
      if (typeof config.min === 'number') {
        rules.push({ type: 'number', min: config.min, message: `最小值为${config.min}`, trigger: 'blur' })
      }
      if (typeof config.max === 'number') {
        rules.push({ type: 'number', max: config.max, message: `最大值为${config.max}`, trigger: 'blur' })
      }
      break
    case 'long_text':
      if (config.max_length && typeof config.max_length === 'number') {
        rules.push({ max: config.max_length, message: `最多${config.max_length}个字符`, trigger: 'blur' })
      }
      break
    case 'multi_select':
      if (typeof config.min_count === 'number') {
        rules.push({ type: 'array', min: config.min_count, message: `至少选择${config.min_count}项`, trigger: 'change' })
      }
      if (typeof config.max_count === 'number') {
        rules.push({ type: 'array', max: config.max_count, message: `最多选择${config.max_count}项`, trigger: 'change' })
      }
      break
  }

  return rules
}
