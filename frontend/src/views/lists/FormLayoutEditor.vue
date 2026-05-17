<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/lists/${listId}/settings`)" content="表单设置" style="margin-bottom:24px;" />

    <el-card style="max-width:960px;">
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between;">
          <span style="font-weight:bold;">表单布局</span>
          <el-tag v-if="dirty" type="warning" size="small">未保存</el-tag>
        </div>
      </template>

      <div v-for="(group, gi) in localGroups" :key="gi" style="border:1px solid #e4e7ed;border-radius:4px;padding:12px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
          <el-input v-model="group.name" placeholder="分组名称" style="width:200px;" @input="markDirty" />
          <span style="color:#909399;font-size:13px;">每行</span>
          <el-select v-model="group.columns" style="width:80px;" @change="onColumnsChange(gi)">
            <el-option :value="2" label="2" />
            <el-option :value="3" label="3" />
            <el-option :value="4" label="4" />
            <el-option :value="6" label="6" />
          </el-select>
          <span style="color:#909399;font-size:13px;">列</span>
          <el-button link type="danger" style="margin-left:auto;" @click="removeGroup(gi)">删除分组</el-button>
        </div>

        <div v-if="group.fields.length === 0" style="color:#c0c4cc;padding:8px;text-align:center;font-size:13px;">
          暂未添加字段，请从右侧字段池拖入
        </div>

        <div v-else style="display:flex;flex-wrap:wrap;gap:8px;">
          <div
            v-for="(gf, fi) in group.fields"
            :key="gf.key"
            :style="{
              width: `calc(${100 * gf.col_span / group.columns}% - 8px)`,
              minWidth: '80px',
            }"
            style="border:1px dashed #c0c4cc;border-radius:4px;padding:8px;position:relative;"
          >
            <div style="font-size:13px;font-weight:500;">{{ gf.key }}</div>
            <div style="display:flex;align-items:center;gap:4px;margin-top:4px;">
              <span style="font-size:12px;color:#909399;">占</span>
              <el-input-number
                :model-value="gf.col_span"
                :min="1"
                :max="group.columns"
                size="small"
                style="width:64px;"
                @update:model-value="(v: number) => { gf.col_span = v; markDirty() }"
              />
              <span style="font-size:12px;color:#909399;">列</span>
              <el-button link size="small" type="danger" style="margin-left:auto;" @click="removeField(gi, fi)">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div style="display:flex;gap:8px;">
        <el-button @click="addGroup">新建分组</el-button>
      </div>

      <div v-if="unassignedFields.length > 0" style="margin-top:16px;">
        <el-divider content-position="left">未分配字段（点击添加到分组）</el-divider>
        <div style="display:flex;flex-wrap:wrap;gap:8px;">
          <el-tag
            v-for="f in unassignedFields"
            :key="f.key"
            type="info"
            style="cursor:pointer;"
            @click="addFieldToGroup(f.key)"
          >
            {{ f.key }}
          </el-tag>
        </div>
      </div>

      <div v-if="dirty" style="margin-top:16px;padding-top:16px;border-top:1px solid #e4e7ed;display:flex;gap:12px;">
        <el-button type="primary" @click="handleSave" :loading="saving">保存更改</el-button>
        <el-button @click="handleCancel">放弃更改</el-button>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Close } from '@element-plus/icons-vue'
import { getListSchema, getFormSchema, updateListSchema } from '../../api/lists'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { SchemaField, FormGroup } from '../../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const listId = route.params.listId as string

interface LocalGroup {
  name: string
  columns: number
  fields: { key: string; col_span: number }[]
}

const allFields = ref<SchemaField[]>([])
const localGroups = ref<LocalGroup[]>([])
const originalJson = ref('')
const dirty = ref(false)
const saving = ref(false)

const allFieldKeys = computed(() => allFields.value.map(f => f.key))

const assignedFields = computed(() => {
  const keys = new Set<string>()
  for (const g of localGroups.value) {
    for (const f of g.fields) keys.add(f.key)
  }
  return keys
})

const unassignedFields = computed(() =>
  allFields.value.filter(f => !assignedFields.value.has(f.key))
)

const markDirty = () => { dirty.value = true }

onMounted(async () => {
  const [schema, formSchema] = await Promise.all([
    getListSchema(appId, listId),
    getFormSchema(appId, listId),
  ])
  allFields.value = schema.fields
  const form = schema.form || {}
  localGroups.value = (form.groups || []).map(g => ({
    name: g.name,
    columns: g.columns,
    fields: g.fields.map(f => ({ ...f })),
  }))
  originalJson.value = JSON.stringify(localGroups.value)
})

const addGroup = () => {
  localGroups.value.push({ name: '新分组', columns: 3, fields: [] })
  markDirty()
}

const removeGroup = (idx: number) => {
  localGroups.value.splice(idx, 1)
  markDirty()
}

const addFieldToGroup = (key: string) => {
  if (localGroups.value.length === 0) {
    localGroups.value.push({ name: '基本信息', columns: 3, fields: [] })
  }
  localGroups.value[0].fields.push({ key, col_span: 1 })
  markDirty()
}

const removeField = (gi: number, fi: number) => {
  localGroups.value[gi].fields.splice(fi, 1)
  markDirty()
}

const onColumnsChange = (gi: number) => {
  const maxCols = localGroups.value[gi].columns
  for (const f of localGroups.value[gi].fields) {
    if (f.col_span > maxCols) f.col_span = 1
  }
  markDirty()
}

const handleSave = async () => {
  saving.value = true
  try {
    const schema = await getListSchema(appId, listId)
    schema.form = {
      groups: localGroups.value.map(g => ({
        name: g.name,
        columns: g.columns,
        fields: g.fields.map(f => ({ key: f.key, col_span: f.col_span })),
      })),
    }
    // 只提交扩展字段，过滤掉继承字段
    schema.fields = schema.fields.filter((f: any) => f.is_extension).map(({ is_extension, ...f }: any) => f)
    await updateListSchema(appId, listId, schema)

    const updated = await getListSchema(appId, listId)
    const form = updated.form || {}
    localGroups.value = (form.groups || []).map(g => ({
      name: g.name,
      columns: g.columns,
      fields: g.fields.map(f => ({ ...f })),
    }))
    originalJson.value = JSON.stringify(localGroups.value)
    dirty.value = false
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}

const handleCancel = () => {
  localGroups.value = JSON.parse(originalJson.value)
  dirty.value = false
}
</script>
