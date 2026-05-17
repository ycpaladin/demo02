<template>
  <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
    <!-- 有分组布局时按分组渲染 -->
    <template v-if="hasLayout">
      <template v-for="(group, gi) in formLayout.groups" :key="gi">
        <el-divider v-if="group.name" :content-position="'left'">{{ group.name }}</el-divider>
        <el-row :gutter="16">
          <el-col
            v-for="(gf, fi) in group.fields"
            :key="gf.key"
            :span="24 / group.columns * gf.col_span"
          >
            <el-form-item v-if="getFieldDef(gf.key)" :label="getFieldLabel(gf.key)" :prop="gf.key">
              <slot name="field" :field="getFieldDef(gf.key)!" :value="formData[gf.key]" :readonly="readonly">
                <FieldControl
                  :field="getFieldDef(gf.key)!"
                  :modelValue="formData[gf.key]"
                  @update:modelValue="v => formData[gf.key] = v"
                  :readonly="readonly"
                />
              </slot>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
      <!-- 未分配字段 -->
      <template v-if="ungroupedFields.length">
        <el-divider v-if="hasLayout" content-position="left">其他</el-divider>
        <el-form-item
          v-for="field in ungroupedFields"
          :key="field.key"
          :label="field.name"
          :prop="field.key"
        >
          <FieldControl
            :field="field"
            :modelValue="formData[field.key]"
            @update:modelValue="v => formData[field.key] = v"
            :readonly="readonly"
          />
        </el-form-item>
      </template>
    </template>

    <!-- 无分组时平铺渲染 -->
    <template v-else>
      <el-form-item
        v-for="field in fields"
        :key="field.key"
        :label="field.name"
        :prop="field.key"
      >
        <FieldControl
          :field="field"
          :modelValue="formData[field.key]"
          @update:modelValue="v => formData[field.key] = v"
          :readonly="readonly"
        />
      </el-form-item>
    </template>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { buildRules } from '../utils/ruleEngine'
import FieldControl from './FieldControl.vue'
import type { FormField, SchemaForm } from '../types'
import type { FormInstance } from 'element-plus'

const props = withDefaults(defineProps<{
  fields: FormField[]
  initialData: Record<string, unknown>
  readonly?: boolean
  formLayout?: SchemaForm
}>(), { readonly: false, formLayout: () => ({ groups: [] }) })

const formRef = ref<FormInstance>()
const formData = reactive<Record<string, unknown>>({ ...props.initialData })
const formRules = reactive<Record<string, unknown>>({})

const hasLayout = computed(() => props.formLayout?.groups?.length > 0)

const groupedFieldKeys = computed(() => {
  const keys = new Set<string>()
  for (const g of props.formLayout.groups) {
    for (const f of g.fields) keys.add(f.key)
  }
  return keys
})

const ungroupedFields = computed(() =>
  props.fields.filter(f => !groupedFieldKeys.value.has(f.key))
)

const getFieldDef = (key: string): FormField | undefined =>
  props.fields.find(f => f.key === key)

const getFieldLabel = (key: string): string =>
  getFieldDef(key)?.name || key

watch(() => props.fields, (fields) => {
  for (const f of fields) {
    formRules[f.key] = buildRules(f)
    if (!(f.key in formData)) {
      formData[f.key] = f.field_type === 'multi_select' ? [] : f.field_type === 'boolean' ? false : ''
    }
  }
}, { immediate: true })

watch(() => props.initialData, (data) => {
  if (!data || Object.keys(data).length === 0) return
  for (const key of Object.keys(formData)) {
    delete formData[key]
  }
  for (const f of props.fields) {
    formData[f.key] = data[f.key] !== undefined ? data[f.key] : (
      f.field_type === 'multi_select' ? [] : f.field_type === 'boolean' ? false : ''
    )
  }
})

const validate = (): Promise<boolean> | undefined => formRef.value?.validate()
const getData = (): Record<string, unknown> => ({ ...formData })
defineExpose({ validate, getData })
</script>
