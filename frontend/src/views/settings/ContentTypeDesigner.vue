<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/settings/content-types`)" :content="ct ? `字段集合 — ${ct.name}` : '字段集合'" style="margin-bottom:24px;" />

    <!-- 继承的父级字段（只读展示） -->
    <el-card v-if="parentCT && parentFields.length" style="max-width:960px;margin-bottom:24px;">
      <template #header>
        <span style="font-weight:bold;">继承字段 — 来自「{{ parentCT.name }}」</span>
      </template>
      <el-table :data="parentFieldRows">
        <el-table-column prop="name" label="字段名" />
        <el-table-column prop="key" label="标识" />
        <el-table-column label="类型">
          <template #default="{ row }">
            <el-tag size="small">{{ row.field_type__key || '—' }}</el-tag>
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
      </el-table>
    </el-card>

    <!-- 自有字段（本地编辑 + 保存提交） -->
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
          <span style="font-weight:bold;">自有字段</span>
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
import {
  getContentType,
  getCTFields, createCTField, updateCTField, deleteCTField, reorderCTFields,
} from '../../api/contentTypes'
import { getFieldTypes } from '../../api/fieldTypes'
import { getLists } from '../../api/lists'
import AppLayout from '../../components/AppLayout.vue'
import FieldDesigner from '../../components/FieldDesigner.vue'
import { ElMessage } from 'element-plus'
import type { ContentType, ContentTypeField, FieldType } from '../../types'
import type { FieldRow } from '../../components/FieldDesigner.vue'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const ctId = route.params.ctId as string

const ct = ref<ContentType | null>(null)
const parentCT = ref<ContentType | null>(null)
const parentFields = ref<ContentTypeField[]>([])
const fieldTypes = ref<FieldType[]>([])
const referenceLists = ref<{ id: string, name: string }[]>([])

// Local draft state
const fields = ref<ContentTypeField[]>([])
const originalJson = ref('')
const deletedIds = ref<string[]>([])
const dirty = ref(false)
const saving = ref(false)

const toFieldRow = (f: any): FieldRow => ({
  ...f,
  _inherited: undefined,
  field_type__key: f.field_type__key || '',
  searchable: f.searchable ?? false,
  search_type: f.search_type || '',
  config: f.config || {},
  validators: f.validators || [],
  order: f.order ?? 0,
})

const parentFieldRows = computed<FieldRow[]>(() => parentFields.value.map(toFieldRow))
const localFieldRows = computed<FieldRow[]>(() => fields.value.map(toFieldRow))

const resetState = (serverFields: ContentTypeField[]) => {
  fields.value = JSON.parse(JSON.stringify(serverFields))
  originalJson.value = JSON.stringify(serverFields)
  deletedIds.value = []
  dirty.value = false
}

const loadData = async () => {
  const [ctData, fts, serverFields, lists] = await Promise.all([
    getContentType(ctId),
    getFieldTypes(),
    getCTFields(ctId),
    getLists(appId).catch(() => [] as any[]),
  ])
  ct.value = ctData
  fieldTypes.value = fts
  referenceLists.value = lists.map(l => ({ id: l.id, name: l.name }))
  resetState(serverFields)

  if (ctData.parent) {
    try {
      parentCT.value = await getContentType(ctData.parent)
      parentFields.value = await getCTFields(ctData.parent)
    } catch { parentCT.value = null; parentFields.value = [] }
  } else {
    parentCT.value = null
    parentFields.value = []
  }
}

onMounted(loadData)

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
    // 1. Delete marked fields
    for (const id of deletedIds.value) {
      await deleteCTField(ctId, id)
    }

    // 2. Create new fields, map temp IDs → real IDs
    const tempToReal: Record<string, string> = {}
    for (const f of fields.value) {
      if (f.id.startsWith('__new_')) {
        const { id, ...data } = f as any
        const created = await createCTField(ctId, data)
        tempToReal[f.id] = created.id
      }
    }

    // 3. Update modified existing fields
    const originals = JSON.parse(originalJson.value) as ContentTypeField[]
    for (const f of fields.value) {
      if (!f.id.startsWith('__new_')) {
        const orig = originals.find((o: ContentTypeField) => o.id === f.id)
        if (!orig) continue
        const { id, ...data } = f as any
        if (JSON.stringify({ ...orig, _inherited: undefined }) !== JSON.stringify({ ...f, _inherited: undefined })) {
          await updateCTField(ctId, id, data)
        }
      }
    }

    // 4. Reorder — build list with real IDs
    const orderedIds = fields.value.map(f => tempToReal[f.id] || f.id)
    await reorderCTFields(ctId, orderedIds)

    // 5. Reload server state
    const serverFields = await getCTFields(ctId)
    resetState(serverFields)
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}

const handleCancel = async () => {
  const serverFields = JSON.parse(originalJson.value) as ContentTypeField[]
  resetState(serverFields)
}
</script>
