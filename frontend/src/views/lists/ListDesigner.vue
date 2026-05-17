<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/lists/${listId}/settings`)" content="字段集合" style="margin-bottom:24px;" />

    <el-card style="max-width:960px;">
      <FieldDesigner
        :fields="localFieldRows"
        :fieldTypes="fieldTypes"
        :referenceLists="referenceLists"
        :appId="appId"
        @add="handleAdd"
        @update="handleUpdate"
        @delete="handleDelete"
        @moveUp="handleMoveUp"
        @moveDown="handleMoveDown"
      >
        <template #header>
          <span style="font-weight:bold;">字段集合</span>
          <el-tag v-if="dirty" type="warning" size="small" style="margin-left:8px;">未保存</el-tag>
        </template>
      </FieldDesigner>

      <div v-if="dirty" style="margin-top:16px;padding-top:16px;border-top:1px solid #e4e7ed;display:flex;align-items:center;gap:12px;">
        <el-button type="primary" @click="handleSave" :loading="saving">保存更改</el-button>
        <el-button @click="handleCancel" :disabled="saving">放弃更改</el-button>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getLists, getListSchema, updateListSchema } from '../../api/lists'
import { getFieldTypes } from '../../api/fieldTypes'
import AppLayout from '../../components/AppLayout.vue'
import FieldDesigner from '../../components/FieldDesigner.vue'
import { ElMessage } from 'element-plus'
import type { SchemaField, FieldType } from '../../types'
import type { FieldRow } from '../../components/FieldDesigner.vue'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const listId = route.params.listId as string

const fieldTypes = ref<FieldType[]>([])
const referenceLists = ref<{ id: string, name: string }[]>([])

// Local draft state
const fields = ref<SchemaField[]>([])
const originalJson = ref('')
const deletedIds = ref<string[]>([])
const dirty = ref(false)
const saving = ref(false)

const localFieldRows = computed<FieldRow[]>(() => fields.value.map(f => ({
  id: f.id || f.key,
  name: f.name,
  key: f.key,
  field_type: f.field_type,
  field_type__key: f.field_type,
  required: f.required,
  unique: f.unique,
  searchable: f.searchable,
  search_type: f.search_type,
  config: f.config || {},
  validators: f.validators || [],
  order: f.order ?? 0,
  _inherited: f.is_extension ? undefined : '内容类型',
})))

const resetState = (serverFields: SchemaField[]) => {
  fields.value = JSON.parse(JSON.stringify(serverFields))
  originalJson.value = JSON.stringify(serverFields)
  deletedIds.value = []
  dirty.value = false
}

onMounted(async () => {
  const [schema, fts, lists] = await Promise.all([
    getListSchema(appId, listId),
    getFieldTypes(),
    getLists(appId).catch(() => [] as any[]),
  ])
  resetState(schema.fields)
  fieldTypes.value = fts
  referenceLists.value = lists.map(l => ({ id: l.id, name: l.name }))
})

const nextTempId = () => `__new_${Date.now()}_${Math.random().toString(36).slice(2)}`

const handleAdd = (data: Record<string, unknown>) => {
  fields.value.push({
    ...data,
    id: nextTempId(),
    order: fields.value.length,
  } as any)
  dirty.value = true
}

const handleUpdate = (id: string, data: Record<string, unknown>) => {
  const idx = fields.value.findIndex(f => f.id === id)
  if (idx >= 0) {
    fields.value[idx] = { ...fields.value[idx], ...data, id: fields.value[idx].id }
    dirty.value = true
  }
}

const handleDelete = (id: string) => {
  if (id.startsWith('__new_')) {
    fields.value = fields.value.filter(f => f.id !== id)
  } else {
    deletedIds.value.push(id)
    fields.value = fields.value.filter(f => f.id !== id)
  }
  dirty.value = true
}

const handleMoveUp = (id: string) => {
  const idx = fields.value.findIndex(f => f.id === id)
  if (idx <= 0) return
  ;[fields.value[idx - 1], fields.value[idx]] = [fields.value[idx], fields.value[idx - 1]]
  dirty.value = true
}

const handleMoveDown = (id: string) => {
  const idx = fields.value.findIndex(f => f.id === id)
  if (idx >= fields.value.length - 1) return
  ;[fields.value[idx], fields.value[idx + 1]] = [fields.value[idx + 1], fields.value[idx]]
  dirty.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    // 只提交扩展字段（is_extension=true 或 新增的）
    const extFields = fields.value
      .filter(f => f.is_extension || f.id?.startsWith('__new_'))
      .map(({ is_extension, ...rest }) => rest)

    // 重新获取当前完整 schema
    const currentSchema = await getListSchema(appId, listId)
    currentSchema.fields = extFields

    await updateListSchema(appId, listId, currentSchema)

    // Reload
    const schema = await getListSchema(appId, listId)
    resetState(schema.fields)
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}

const handleCancel = async () => {
  const serverFields = JSON.parse(originalJson.value) as SchemaField[]
  resetState(serverFields)
}
</script>
