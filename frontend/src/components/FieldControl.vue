<template>
  <el-input
    v-if="field.field_type === 'text' || field.field_type === 'long_text'"
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :type="field.field_type === 'long_text' ? 'textarea' : 'text'"
    :rows="field.field_type === 'long_text' ? 6 : 1"
    :placeholder="`请输入${field.name}`"
    :disabled="readonly"
  />
  <el-input-number
    v-else-if="field.field_type === 'number'"
    :model-value="modelValue as number"
    @update:model-value="$emit('update:modelValue', $event)"
    :min="(field.config as any)?.min"
    :max="(field.config as any)?.max"
    :disabled="readonly"
  />
  <el-date-picker
    v-else-if="field.field_type === 'date'"
    :model-value="modelValue as string"
    @update:model-value="$emit('update:modelValue', $event)"
    type="date"
    value-format="YYYY-MM-DD"
    :placeholder="`请选择${field.name}`"
    :disabled="readonly"
  />
  <el-switch
    v-else-if="field.field_type === 'boolean'"
    :model-value="modelValue as boolean"
    @update:model-value="$emit('update:modelValue', $event)"
    :disabled="readonly"
  />
  <el-select
    v-else-if="field.field_type === 'select'"
    :model-value="modelValue as string"
    @update:model-value="$emit('update:modelValue', $event)"
    :placeholder="`请选择${field.name}`"
    :disabled="readonly"
  >
    <el-option v-for="opt in ((field as any).options || [])" :key="opt" :label="opt" :value="opt" />
  </el-select>
  <el-select
    v-else-if="field.field_type === 'multi_select'"
    :model-value="modelValue as string[]"
    @update:model-value="$emit('update:modelValue', $event)"
    multiple
    :placeholder="`请选择${field.name}`"
    :disabled="readonly"
  >
    <el-option v-for="opt in ((field as any).options || [])" :key="opt" :label="opt" :value="opt" />
  </el-select>
  <el-input
    v-else
    :model-value="modelValue as string"
    @update:model-value="$emit('update:modelValue', $event)"
    :placeholder="`请输入${field.name}`"
    :disabled="readonly"
  />
</template>

<script setup lang="ts">
import type { FormField } from '../types'

defineProps<{
  field: FormField
  modelValue: unknown
  readonly?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: unknown]
}>()
</script>
