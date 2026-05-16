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

    <el-dialog v-model="showDialog" :title="editingRow ? '编辑字段' : '添加字段'">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="字段名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="标识" prop="key">
          <el-input v-model="form.key" :disabled="!!editingRow" />
        </el-form-item>
        <el-form-item label="字段类型" prop="field_type">
          <el-select v-model="form.field_type" @change="onFieldTypeChange">
            <el-option v-for="ft in fieldTypes" :key="ft.id" :label="ft.name" :value="ft.id" />
          </el-select>
        </el-form-item>

        <!-- 关联引用级联选择 -->
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
          <el-select v-model="form.search_type" :disabled="!form.searchable">
            <el-option label="精确" value="exact" />
            <el-option label="模糊" value="contains" />
            <el-option label="范围" value="range" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认值">
          <el-input v-model="form.default_value" placeholder="可选" />
        </el-form-item>
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
const form = ref({
  name: '', key: '', field_type: '',
  required: false, unique: false, searchable: false, search_type: 'contains',
  reference: [] as string[],
  default_value: '',
})

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

const baseRules: FormRules = {
  name: [
    { required: true, message: '请输入字段名', trigger: 'blur' },
    { validator: validateName, trigger: 'blur' },
  ],
  key: [
    { required: true, message: '请输入标识', trigger: 'blur' },
    { validator: validateKey, trigger: 'blur' },
  ],
  field_type: [{ required: true, message: '请选择字段类型', trigger: 'change' }],
}

const formRules = computed<FormRules>(() => {
  if (isReferenceType.value) {
    return {
      ...baseRules,
      reference: [{ required: true, message: '请选择关联列表和字段', trigger: 'change' }],
    }
  }
  return baseRules
})

const selectedFieldType = computed(() =>
  props.fieldTypes.find(ft => ft.id === form.value.field_type)
)

const isReferenceType = computed(() =>
  selectedFieldType.value?.key === 'reference'
)

const isExistingReference = computed(() =>
  isReferenceType.value && !!editingRow.value
)

// Cascader level-1 options: lists
const cascaderOptions = computed<CascaderOption[]>(() =>
  props.referenceLists.map(lst => ({
    value: lst.id,
    label: lst.name,
    leaf: false,
  }))
)

// Lazy load level-2: fields of the selected list
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

const onFieldTypeChange = () => {
  form.value.reference = []
}

const openAddDialog = () => {
  editingRow.value = null
  form.value = {
    name: '', key: '', field_type: '',
    required: false, unique: false, searchable: false, search_type: 'contains',
    reference: [],
    default_value: '',
  }
  showDialog.value = true
}

const openEditDialog = (row: FieldRow) => {
  editingRow.value = row
  const cfg = (row.config as Record<string, unknown>) || {}
  form.value = {
    name: row.name,
    key: row.key,
    field_type: row.field_type,
    required: row.required,
    unique: row.unique,
    searchable: row.searchable,
    search_type: row.search_type || 'contains',
    reference: [cfg.reference_list as string || '', cfg.reference_field as string || ''],
    default_value: (cfg.default_value as string) || '',
  }
  showDialog.value = true
}

const handleSubmit = async () => {
  try { await formRef.value!.validate() } catch { return }
  saving.value = true
  try {
    const { default_value, reference, ...rest } = form.value
    const config: Record<string, unknown> = { default_value: default_value || '' }
    if (isReferenceType.value && reference.length === 2) {
      config.reference_list = reference[0]
      config.reference_field = reference[1]
    }
    const data = { ...rest, config }
    if (editingRow.value) {
      emit('update', editingRow.value.id, data)
    } else {
      emit('add', data)
    }
  } finally { saving.value = false }
}
</script>
