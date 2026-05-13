<template>
  <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
    <el-form-item
      v-for="field in fields"
      :key="field.key"
      :label="field.name"
      :prop="field.key"
    >
      <el-input
        v-if="field.field_type === 'text' || field.field_type === 'long_text'"
        v-model="formData[field.key]"
        :type="field.field_type === 'long_text' ? 'textarea' : 'text'"
        :rows="field.field_type === 'long_text' ? 6 : 1"
        :placeholder="`请输入${field.name}`"
      />
      <el-input-number
        v-else-if="field.field_type === 'number'"
        v-model="formData[field.key]"
        :min="field.config?.min"
        :max="field.config?.max"
      />
      <el-date-picker
        v-else-if="field.field_type === 'date'"
        v-model="formData[field.key]"
        type="date"
        value-format="YYYY-MM-DD"
        :placeholder="`请选择${field.name}`"
      />
      <el-switch v-else-if="field.field_type === 'boolean'" v-model="formData[field.key]" />
      <el-select
        v-else-if="field.field_type === 'select'"
        v-model="formData[field.key]"
        :placeholder="`请选择${field.name}`"
      >
        <el-option v-for="opt in (field.options || [])" :key="opt" :label="opt" :value="opt" />
      </el-select>
      <el-select
        v-else-if="field.field_type === 'multi_select'"
        v-model="formData[field.key]"
        multiple
        :placeholder="`请选择${field.name}`"
      >
        <el-option v-for="opt in (field.options || [])" :key="opt" :label="opt" :value="opt" />
      </el-select>
      <el-input v-else v-model="formData[field.key]" :placeholder="`请输入${field.name}`" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { buildRules } from '../utils/ruleEngine'
import type { FormField } from '../types'
import type { FormInstance } from 'element-plus'

const props = defineProps<{
  fields: FormField[]
  initialData: Record<string, unknown>
}>()

const formRef = ref<FormInstance>()
const formData = reactive<Record<string, unknown>>({ ...props.initialData })
const formRules = reactive<Record<string, unknown>>({})

watch(() => props.fields, (fields) => {
  for (const f of fields) {
    formRules[f.key] = buildRules(f)
    if (!(f.key in formData)) {
      formData[f.key] = f.field_type === 'multi_select' ? [] : f.field_type === 'boolean' ? false : ''
    }
  }
}, { immediate: true })

const validate = (): Promise<boolean> | undefined => formRef.value?.validate()
const getData = (): Record<string, unknown> => ({ ...formData })
defineExpose({ validate, getData })

