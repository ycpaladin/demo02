<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/lists/${listId}/settings`)" content="字段集合" style="margin-bottom:24px;" />

    <el-card style="max-width:960px;">
      <FieldDesigner
        :fields="localFieldRows"
        :fieldTypes="fieldTypes"
        :referenceLists="referenceLists"
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
import { getLists, getListFields, createListField, updateListField, deleteListField, reorderListFields } from '../../api/lists'
import { getFieldTypes } from '../../api/fieldTypes'
import AppLayout from '../../components/AppLayout.vue'
import FieldDesigner from '../../components/FieldDesigner.vue'
import { ElMessage } from 'element-plus'
import type { ListField, FieldType } from '../../types'
import type { FieldRow } from '../../components/FieldDesigner.vue'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const listId = route.params.listId as string

const fieldTypes = ref<FieldType[]>([])
const referenceLists = ref<{ id: string, name: string }[]>([])

// Local draft state
const fields = ref<ListField[]>([])
const originalJson = ref('')
const deletedIds = ref<string[]>([])
const dirty = ref(false)
const saving = ref(false)

const localFieldRows = computed<FieldRow[]>(() => fields.value.map(f => ({
  ...f,
  _inherited: undefined,
  field_type__key: (f as any).field_type__key || '',
  searchable: (f as any).searchable ?? false,
  search_type: (f as any).search_type || '',
  config: (f as any).config || {},
  validators: (f as any).validators || [],
  order: (f as any).order ?? 0,
})))

const resetState = (serverFields: ListField[]) => {
  fields.value = JSON.parse(JSON.stringify(serverFields))
  originalJson.value = JSON.stringify(serverFields)
  deletedIds.value = []
  dirty.value = false
}

onMounted(async () => {
  const [flds, fts, lists] = await Promise.all([
    getListFields(listId),
    getFieldTypes(),
    getLists(appId).catch(() => [] as any[]),
  ])
  resetState(flds)
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
    // 1. Delete marked fields
    for (const id of deletedIds.value) {
      await deleteListField(listId, id)
    }

    // 2. Create new fields
    const tempToReal: Record<string, string> = {}
    for (const f of fields.value) {
      if (f.id.startsWith('__new_')) {
        const { id, ...data } = f as any
        const created = await createListField(listId, data)
        tempToReal[f.id] = created.id
      }
    }

    // 3. Update modified existing fields
    const originals = JSON.parse(originalJson.value) as ListField[]
    for (const f of fields.value) {
      if (!f.id.startsWith('__new_')) {
        const orig = originals.find((o: ListField) => o.id === f.id)
        if (!orig) continue
        const { id, ...data } = f as any
        if (JSON.stringify(orig) !== JSON.stringify(f)) {
          await updateListField(listId, id, data)
        }
      }
    }

    // 4. Reorder
    const orderedIds = fields.value.map(f => tempToReal[f.id] || f.id)
    await reorderListFields(listId, orderedIds)

    // 5. Reload
    const serverFields = await getListFields(listId)
    resetState(serverFields)
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}

const handleCancel = async () => {
  const serverFields = JSON.parse(originalJson.value) as ListField[]
  resetState(serverFields)
}
</script>
