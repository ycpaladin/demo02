<template>
  <div>
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
      <slot name="header" />
      <el-button type="primary" size="small" @click="openAddDialog">添加字段</el-button>
    </div>

    <el-table :data="fields" row-key="id">
      <el-table-column label="排序" width="90">
        <template #default="{ row, $index }">
          <template v-if="!row._inherited">
            <el-button link size="small" :disabled="$index === 0" @click="$emit('moveUp', row.id)">
              <el-icon><ArrowUp /></el-icon>
            </el-button>
            <el-button link size="small" :disabled="$index === fields.length - 1" @click="$emit('moveDown', row.id)">
              <el-icon><ArrowDown /></el-icon>
            </el-button>
          </template>
          <span v-else style="color:#c0c4cc;">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="字段名" />
      <el-table-column prop="key" label="标识" />
      <el-table-column label="类型">
        <template #default="{ row }">
          <el-tag size="small">{{ row.field_type__key || row.field_type_name || '—' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="必填" width="70">
        <template #default="{ row }">
          <el-checkbox :model-value="row.required" disabled />
        </template>
      </el-table-column>
      <el-table-column label="唯一" width="70">
        <template #default="{ row }">
          <el-checkbox :model-value="row.unique" disabled />
        </template>
      </el-table-column>
      <el-table-column label="可搜索" width="80">
        <template #default="{ row }">
          <el-checkbox :model-value="row.searchable" disabled />
        </template>
      </el-table-column>
      <el-table-column v-if="showSource" label="来源" width="150">
        <template #default="{ row }">
          <el-tag v-if="row._inherited" type="info" size="small">继承自「{{ row._inherited }}」</el-tag>
          <el-tag v-else type="primary" size="small">自有</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <template v-if="!row._inherited">
            <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除?" @confirm="$emit('delete', row.id)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
          <span v-else style="color:#c0c4cc;">—</span>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!fields.length" description="暂无字段" />

    <el-dialog v-model="showDialog" :title="editingRow ? '编辑字段' : '添加字段'" width="700px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="120px">

        <el-divider content-position="left">基本信息</el-divider>
        <el-form-item label="字段名称" prop="name">
          <el-input v-model="form.name" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="字段键" prop="key">
          <el-input v-model="form.key" :disabled="!!editingRow" placeholder="小写字母开头，仅小写/数字/下划线" />
        </el-form-item>
        <el-form-item label="字段类型" prop="field_type">
          <el-select v-model="form.field_type" @change="onFieldTypeChange" :disabled="!!editingRow" style="width:100%;">
            <el-option v-for="ft in fieldTypes" :key="ft.id" :label="ft.name" :value="ft.id" />
          </el-select>
        </el-form-item>

        <template v-if="isReferenceType">
          <el-form-item label="关联引用" prop="reference">
            <el-cascader
              v-model="form.reference"
              :options="cascaderOptions"
              :props="{ lazy: true, lazyLoad }"
              :disabled="isExistingReference"
              placeholder="请选择列表和字段"
              style="width:100%;"
            />
          </el-form-item>
        </template>

        <el-divider content-position="left">基本配置</el-divider>
        <el-form-item label="帮助文本">
          <el-input v-model="form.help_text" type="textarea" :rows="2" maxlength="256" show-word-limit placeholder="字段下方显示的说明文字" />
        </el-form-item>
        <el-form-item label="占位符">
          <el-input v-model="form.placeholder" maxlength="128" show-word-limit placeholder="输入框内占位提示" />
        </el-form-item>
        <el-form-item label="默认值">
          <el-input v-model="form.default_value" placeholder="可选" />
        </el-form-item>
        <el-form-item label="必填">
          <el-switch v-model="form.required" />
        </el-form-item>
        <el-form-item label="唯一">
          <el-switch v-model="form.unique" />
        </el-form-item>
        <el-form-item label="可搜索">
          <el-switch v-model="form.searchable" />
        </el-form-item>
        <el-form-item label="搜索方式">
          <el-select v-model="form.search_type" :disabled="!form.searchable" style="width:100%;">
            <el-option label="精确" value="exact" />
            <el-option label="模糊" value="contains" />
            <el-option label="范围" value="range" />
          </el-select>
        </el-form-item>

        <TextConfig v-if="isTextType" :form="form" />
        <SelectConfig v-if="isSelectType" :form="form" />
        <NumberConfig v-if="isNumberType" :form="form" />
        <DateConfig v-if="isDateType" :form="form" />
        <BooleanConfig v-if="isBooleanType" :form="form" />
        <AttachmentConfig v-if="isAttachmentType" :form="form" />
        <ReferenceConfig v-if="isReferenceType" :form="form" />
        <AutoNumberConfig v-if="isAutoNumberType" :form="form" />
        <ComputedConfig v-if="isComputedType" :form="form" />

      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">
          {{ editingRow ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { getListFields } from '../api/lists'
import type { FieldType } from '../types'
import type { FormRules } from 'element-plus'
import TextConfig from './fields/TextConfig.vue'
import SelectConfig from './fields/SelectConfig.vue'
import NumberConfig from './fields/NumberConfig.vue'
import DateConfig from './fields/DateConfig.vue'
import BooleanConfig from './fields/BooleanConfig.vue'
import AttachmentConfig from './fields/AttachmentConfig.vue'
import ReferenceConfig from './fields/ReferenceConfig.vue'
import AutoNumberConfig from './fields/AutoNumberConfig.vue'
import ComputedConfig from './fields/ComputedConfig.vue'

export interface FieldRow {
  id: string
  name: string
  key: string
  field_type: string
  field_type__key?: string
  field_type_name?: string
  required: boolean
  unique: boolean
  searchable: boolean
  search_type: string
  config: Record<string, unknown>
  validators: string[]
  order: number
  _inherited?: string
}

interface CascaderOption {
  value: string
  label: string
  leaf?: boolean
}

export interface FieldFormModel {
  name: string
  key: string
  field_type: string
  required: boolean
  unique: boolean
  searchable: boolean
  search_type: string
  reference: string[]
  default_value: string
  help_text: string
  placeholder: string
  // 文本
  text_type: string
  min_length: number | null
  max_length: number | null
  rows: number | null
  rich_text: boolean
  // 数字
  min_value: number | null
  max_value: number | null
  precision: number | null
  // 选项
  select_type: string
  options: string
  select_display: string
  // 日期
  date_format: string
  min_date: string | null
  max_date: string | null
  // 布尔
  boolean_display: string
  boolean_true_label: string
  boolean_false_label: string
  // 附件
  max_files: number | null
  allowed_file_types: string[]
  max_file_size: number
  // 引用
  reference_type: string
  reference_display: string
  reference_select_strategy: string
  reference_expand_on: string
  reference_searchable: boolean
  reference_expand_all: boolean
  // 自动编号
  auto_rule: string
  auto_prefix: string
  auto_start: number
  auto_digits: number
  auto_date_format: string
  auto_random_length: number
  auto_random_charset: string[]
  // 计算值
  expression: string
}

const props = withDefaults(defineProps<{
  fields: FieldRow[]
  fieldTypes: FieldType[]
  referenceLists?: { id: string, name: string }[]
  showSource?: boolean
}>(), {
  referenceLists: () => [],
  showSource: false,
})

const emit = defineEmits<{
  add: [data: Record<string, unknown>]
  update: [id: string, data: Record<string, unknown>]
  delete: [id: string]
  moveUp: [id: string]
  moveDown: [id: string]
}>()

const showDialog = ref(false)
const saving = ref(false)
const editingRow = ref<FieldRow | null>(null)
const formRef = ref()

function getDefaultForm(): FieldFormModel {
  return {
    name: '', key: '', field_type: '',
    required: false, unique: false, searchable: false, search_type: 'contains',
    reference: [],
    default_value: '', help_text: '', placeholder: '',
    text_type: 'single_line',
    min_length: null, max_length: null, rows: null, rich_text: false,
    min_value: null, max_value: null, precision: null,
    select_type: 'single', options: '', select_display: 'radio',
    date_format: 'date', min_date: null, max_date: null,
    boolean_display: 'switch',
    boolean_true_label: '', boolean_false_label: '',
    max_files: null, allowed_file_types: ['all'], max_file_size: 10,
    reference_type: 'single', reference_display: 'dropdown',
    reference_select_strategy: 'leaf', reference_expand_on: 'click',
    reference_searchable: true, reference_expand_all: false,
    auto_rule: 'prefix_seq', auto_prefix: '', auto_start: 1,
    auto_digits: 5, auto_date_format: 'YYYYMMDD',
    auto_random_length: 8, auto_random_charset: ['upper', 'lower', 'digit'],
    expression: '',
  }
}

const form = ref<FieldFormModel>(getDefaultForm())

// ==================== Computed: field type detection ====================

const selectedFieldType = computed(() =>
  props.fieldTypes.find(ft => ft.id === form.value.field_type)
)

const ftKey = computed(() => selectedFieldType.value?.key || '')

const isTextType = computed(() => ftKey.value === 'text')
const isNumberType = computed(() => ftKey.value === 'number')
const isDateType = computed(() => ftKey.value === 'date')
const isBooleanType = computed(() => ftKey.value === 'boolean')
const isSelectType = computed(() => ftKey.value === 'select')

const isAttachmentType = computed(() => ftKey.value === 'attachment')
const isReferenceType = computed(() => ftKey.value === 'reference')
const isAutoNumberType = computed(() => ftKey.value === 'auto_number')
const isComputedType = computed(() => ftKey.value === 'computed')
const isExistingReference = computed(() => isReferenceType.value && !!editingRow.value)

// ==================== Validation ====================

const validateName = (_rule: any, value: string, cb: any) => {
  if (!value) return cb()
  const dup = props.fields.find(f => f.name === value && f.id !== editingRow.value?.id)
  if (dup) return cb(new Error('字段名已存在'))
  cb()
}

const validateKey = (_rule: any, value: string, cb: any) => {
  if (!value) return cb()
  const dup = props.fields.find(f => f.key === value && f.id !== editingRow.value?.id)
  if (dup) return cb(new Error('标识已存在'))
  cb()
}

const validateOptions = (_rule: any, value: string, cb: any) => {
  if (!value) return cb()
  const lines = value.split('\n').map(s => s.trim()).filter(Boolean)
  if (lines.length < 2) return cb(new Error('至少需要 2 个选项'))
  cb()
}

const validateAllowedFileTypes = (_rule: any, value: string[], cb: any) => {
  if (!value || value.length === 0) return cb(new Error('至少选择一项文件类型'))
  cb()
}

const validateAutoCharset = (_rule: any, value: string[], cb: any) => {
  if (!value || value.length === 0) return cb(new Error('至少选择一项字符集'))
  cb()
}

const formRules = computed<FormRules>(() => {
  const rules: FormRules = {
    name: [
      { required: true, message: '请输入字段名称', trigger: 'blur' },
      { max: 64, message: '最多 64 个字符', trigger: 'blur' },
      { validator: validateName, trigger: 'blur' },
    ],
    key: [
      { required: true, message: '请输入字段键', trigger: 'blur' },
      { pattern: /^[a-z][a-z0-9_]*$/, message: '小写字母开头，仅小写字母/数字/下划线', trigger: 'blur' },
      { validator: validateKey, trigger: 'blur' },
    ],
    field_type: [{ required: true, message: '请选择字段类型', trigger: 'change' }],
  }

  if (isReferenceType.value) {
    rules.reference = [{ required: true, message: '请选择关联列表和字段', trigger: 'change' }]
  }

  if (isSelectType.value) {
    rules.options = [
      { required: true, message: '请输入选项列表', trigger: 'blur' },
      { validator: validateOptions, trigger: 'blur' },
    ]
    rules.select_type = [{ required: true, message: '请选择类型', trigger: 'change' }]
  }

  if (isDateType.value) {
    rules.date_format = [{ required: true, message: '请选择日期格式', trigger: 'change' }]
  }

  if (isTextType.value) {
    rules.text_type = [{ required: true, message: '请选择文本类型', trigger: 'change' }]
  }

  if (isAttachmentType.value) {
    rules.allowed_file_types = [
      { required: true, message: '至少选择一项文件类型', trigger: 'change' },
      { validator: validateAllowedFileTypes, trigger: 'change' },
    ]
  }

  if (isAutoNumberType.value) {
    rules.auto_rule = [{ required: true, message: '请选择生成规则', trigger: 'change' }]
    rules.auto_random_charset = [
      { validator: validateAutoCharset, trigger: 'change' },
    ]
  }

  if (isComputedType.value) {
    rules.expression = [{ required: true, message: '请输入表达式', trigger: 'blur' }]
  }

  return rules
})

// ==================== Cascader (reference) ====================

const cascaderOptions = computed<CascaderOption[]>(() =>
  props.referenceLists.map(lst => ({
    value: lst.id,
    label: lst.name,
    leaf: false,
  }))
)

const lazyLoad = (node: any, resolve: (children: CascaderOption[]) => void) => {
  const listId = node.value as string
  getListFields(listId)
    .then(fields => {
      resolve(fields.map(f => ({
        value: f.key,
        label: `${f.name} (${f.key})`,
        leaf: true,
      })))
    })
    .catch(() => resolve([]))
}

// ==================== Handlers ====================

const onFieldTypeChange = () => {
  const reset = getDefaultForm()
  form.value.text_type = reset.text_type
  form.value.min_length = reset.min_length
  form.value.max_length = reset.max_length
  form.value.rows = reset.rows
  form.value.rich_text = reset.rich_text
  form.value.min_value = reset.min_value
  form.value.max_value = reset.max_value
  form.value.precision = reset.precision
  form.value.select_type = reset.select_type
  form.value.options = reset.options
  form.value.select_display = reset.select_display
  form.value.date_format = reset.date_format
  form.value.min_date = reset.min_date
  form.value.max_date = reset.max_date
  form.value.boolean_display = reset.boolean_display
  form.value.boolean_true_label = reset.boolean_true_label
  form.value.boolean_false_label = reset.boolean_false_label
  form.value.max_files = reset.max_files
  form.value.allowed_file_types = [...reset.allowed_file_types]
  form.value.max_file_size = reset.max_file_size
  form.value.reference = []
  form.value.reference_type = reset.reference_type
  form.value.reference_display = reset.reference_display
  form.value.reference_select_strategy = reset.reference_select_strategy
  form.value.reference_expand_on = reset.reference_expand_on
  form.value.reference_searchable = reset.reference_searchable
  form.value.reference_expand_all = reset.reference_expand_all
  form.value.auto_rule = reset.auto_rule
  form.value.auto_prefix = reset.auto_prefix
  form.value.auto_start = reset.auto_start
  form.value.auto_digits = reset.auto_digits
  form.value.auto_date_format = reset.auto_date_format
  form.value.auto_random_length = reset.auto_random_length
  form.value.auto_random_charset = [...reset.auto_random_charset]
  form.value.expression = reset.expression
}

const openAddDialog = () => {
  editingRow.value = null
  form.value = getDefaultForm()
  showDialog.value = true
}

const openEditDialog = (row: FieldRow) => {
  editingRow.value = row
  const cfg = (row.config as Record<string, unknown>) || {}
  const d = getDefaultForm()

  form.value = {
    name: row.name,
    key: row.key,
    field_type: row.field_type,
    required: row.required,
    unique: row.unique,
    searchable: row.searchable,
    search_type: row.search_type || 'contains',
    reference: [cfg.reference_list as string || '', cfg.reference_field as string || ''],

    default_value: (cfg.default_value as string) || d.default_value,
    help_text: (cfg.help_text as string) || d.help_text,
    placeholder: (cfg.placeholder as string) || d.placeholder,

    text_type: (cfg.text_type as string) || d.text_type,
    min_length: cfg.min_length != null ? cfg.min_length as number : d.min_length,
    max_length: cfg.max_length != null ? cfg.max_length as number : d.max_length,
    rows: cfg.rows != null ? cfg.rows as number : d.rows,
    rich_text: (cfg.rich_text as boolean) ?? d.rich_text,

    min_value: cfg.min_value != null ? cfg.min_value as number : d.min_value,
    max_value: cfg.max_value != null ? cfg.max_value as number : d.max_value,
    precision: cfg.precision != null ? cfg.precision as number : d.precision,

    select_type: (cfg.select_type as string) || d.select_type,
    options: ((cfg.options as string[]) || []).join('\n'),
    select_display: (cfg.select_display as string) || d.select_display,

    date_format: (cfg.date_format as string) || d.date_format,
    min_date: (cfg.min_date as string | null) ?? d.min_date,
    max_date: (cfg.max_date as string | null) ?? d.max_date,

    boolean_display: (cfg.boolean_display as string) || d.boolean_display,
    boolean_true_label: (cfg.boolean_true_label as string) || d.boolean_true_label,
    boolean_false_label: (cfg.boolean_false_label as string) || d.boolean_false_label,

    max_files: cfg.max_files != null ? cfg.max_files as number : d.max_files,
    allowed_file_types: (cfg.allowed_file_types as string[]) || [...d.allowed_file_types],
    max_file_size: (cfg.max_file_size as number) ?? d.max_file_size,

    reference_type: (cfg.reference_type as string) || d.reference_type,
    reference_display: (cfg.reference_display as string) || d.reference_display,
    reference_select_strategy: (cfg.reference_select_strategy as string) || d.reference_select_strategy,
    reference_expand_on: (cfg.reference_expand_on as string) || d.reference_expand_on,
    reference_searchable: (cfg.reference_searchable as boolean) ?? d.reference_searchable,
    reference_expand_all: (cfg.reference_expand_all as boolean) ?? d.reference_expand_all,

    auto_rule: (cfg.auto_rule as string) || d.auto_rule,
    auto_prefix: (cfg.auto_prefix as string) || d.auto_prefix,
    auto_start: (cfg.auto_start as number) ?? d.auto_start,
    auto_digits: (cfg.auto_digits as number) ?? d.auto_digits,
    auto_date_format: (cfg.auto_date_format as string) || d.auto_date_format,
    auto_random_length: (cfg.auto_random_length as number) ?? d.auto_random_length,
    auto_random_charset: (cfg.auto_random_charset as string[]) || [...d.auto_random_charset],

    expression: (cfg.expression as string) || d.expression,
  }

  showDialog.value = true
}

const handleSubmit = async () => {
  try { await formRef.value!.validate() } catch { return }
  saving.value = true
  try {
    const {
      name, key, field_type, required, unique, searchable, search_type,
      reference, default_value, help_text, placeholder,
      text_type, min_length, max_length, rows, rich_text,
      min_value, max_value, precision,
      select_type, options, select_display,
      date_format, min_date, max_date,
      boolean_display, boolean_true_label, boolean_false_label,
      max_files, allowed_file_types, max_file_size,
      reference_type, reference_display,
      reference_select_strategy, reference_expand_on,
      reference_searchable, reference_expand_all,
      auto_rule, auto_prefix, auto_start, auto_digits, auto_date_format,
      auto_random_length, auto_random_charset,
      expression,
    } = form.value

    const ftKey = selectedFieldType.value?.key || ''

    const config: Record<string, unknown> = {
      default_value: default_value || '',
      help_text: help_text || '',
      placeholder: placeholder || '',
    }

    if (ftKey === 'text') {
      config.text_type = text_type
      if (text_type !== 'long_text') {
        config.min_length = min_length
        config.max_length = max_length
      }
      if (text_type !== 'single_line') {
        config.rows = rows
      }
      if (text_type === 'long_text') {
        config.rich_text = rich_text
      }
    }

    if (ftKey === 'number') {
      config.min_value = min_value
      config.max_value = max_value
      config.precision = precision
    }

    if (ftKey === 'select') {
      config.select_type = select_type
      config.options = options.split('\n').map(s => s.trim()).filter(Boolean)
      config.select_display = select_display
    }

    if (ftKey === 'date') {
      config.date_format = date_format
      config.min_date = min_date || null
      config.max_date = max_date || null
    }

    if (ftKey === 'boolean') {
      config.boolean_display = boolean_display
      config.boolean_true_label = boolean_true_label || ''
      config.boolean_false_label = boolean_false_label || ''
    }

    if (ftKey === 'auto_number') {
      config.auto_rule = auto_rule
      config.auto_prefix = auto_prefix || ''
      config.auto_start = auto_start
      config.auto_digits = auto_digits
      config.auto_date_format = auto_date_format
      config.auto_random_length = auto_random_length
      config.auto_random_charset = auto_random_charset
    }

    if (ftKey === 'computed') {
      config.expression = expression || ''
    }

    if (ftKey === 'attachment') {
      config.max_files = max_files
      config.allowed_file_types = allowed_file_types
      config.max_file_size = max_file_size
    }

    if (ftKey === 'reference') {
      config.reference_type = reference_type
      config.reference_display = reference_display
      config.reference_expand_on = reference_expand_on
      config.reference_searchable = reference_searchable
      config.reference_expand_all = reference_expand_all
      if (reference_type === 'multiple') {
        config.reference_select_strategy = reference_select_strategy
      }
      if (reference.length === 2) {
        config.reference_list = reference[0]
        config.reference_field = reference[1]
      }
    }

    const data = {
      name, key, field_type, required, unique, searchable, search_type, config,
    }

    if (editingRow.value) {
      emit('update', editingRow.value.id, data)
    } else {
      emit('add', data)
    }
  } finally { saving.value = false }
}
</script>
