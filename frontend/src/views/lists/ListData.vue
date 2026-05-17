<template>
  <AppLayout>
    <div v-if="loading">加载中...</div>
    <template v-else>
      <!-- 操作栏 -->
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <div style="display:flex;gap:8px;">
          <el-button type="primary" @click="$router.push(`/apps/${appId}/lists/${listId}/data/add`)">新增</el-button>
          <el-button :disabled="selectedIds.length === 0" @click="handleBatchDelete">批量删除</el-button>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:13px;color:#909399;">切换视图</span>
          <el-select :model-value="activeView" @change="switchView" style="width:180px;">
            <el-option v-for="v in views" :key="v.url_key" :label="v.name" :value="v.url_key" />
            <el-divider style="margin:4px 0;" />
            <el-option label="编辑当前视图" value="__edit__" />
          </el-select>
        </div>
      </div>

      <!-- 表格 -->
      <vxe-table
        ref="tableRef"
        :data="records"
        :column-config="{ resizable: true }"
        :checkbox-config="{ trigger: 'row', reserve: true }"
        @checkbox-change="onSelection"
        @checkbox-all="onSelection"
        @sort-change="onSortChange"
        stripe
        border
        height="600"
      >
        <vxe-column type="checkbox" width="50" fixed="left" />
        <vxe-column
          v-for="col in visibleColumns"
          :key="col.key"
          :field="`data.${col.key}`"
          :title="col.name"
          :sortable="true"
          show-header-overflow
          show-overflow="tooltip"
        />
        <vxe-column title="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="$router.push(`/apps/${appId}/lists/${listId}/data/${row.id}/edit`)">编辑</el-button>
            <el-popconfirm title="确认删除?" @confirm="handleDelete(row.id)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </vxe-column>
      </vxe-table>

      <!-- 分页 -->
      <div style="margin-top:12px;display:flex;align-items:center;justify-content:flex-end;gap:12px;">
        <el-select :model-value="pageSize" @change="onPageSizeChange" style="width:100px;">
          <el-option v-for="s in currentViewPageSizes" :key="s" :label="`${s} 条/页`" :value="s" />
        </el-select>
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          background
          @current-change="onPageChange"
        />
        <span style="display:flex;align-items:center;gap:4px;font-size:13px;color:#606266;">
          跳至 <el-input v-model="jumpPage" size="small" style="width:56px;" @keyup.enter="handleJump" /> 页
          <el-button size="small" @click="handleJump">GO</el-button>
        </span>
      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getListSchema, getFormSchema } from '../../api/lists'
import { getRecords, deleteRecord } from '../../api/records'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { FormField, SchemaView, RecordItem } from '../../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const listId = route.params.listId as string

const tableRef = ref()
const loading = ref(true)
const allFields = ref<FormField[]>([])
const views = ref<SchemaView[]>([])
const activeView = ref('default')
const records = ref<RecordItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedIds = ref<string[]>([])
const jumpPage = ref('')
const sortField = ref('')
const sortOrder = ref<'asc' | 'desc' | ''>('')

const currentView = computed(() => views.value.find(v => v.url_key === activeView.value))
const currentViewPageSizes = computed(() => currentView.value?.page_size_options || [10, 20, 50, 100])

const visibleColumns = computed(() => {
  const cv = currentView.value
  if (cv?.fields?.length) {
    const visibleKeys = cv.fields.filter(f => f.visible).map(f => f.key)
    return visibleKeys.map(k => allFields.value.find(f => f.key === k)).filter(Boolean) as FormField[]
  }
  return allFields.value
})

const loadData = async () => {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (activeView.value) params.view = activeView.value
    if (sortField.value) {
      params.sort = sortOrder.value
        ? `${sortField.value}:${sortOrder.value}`
        : sortField.value
    }
    const res = await getRecords(appId, listId, params)
    records.value = res.results
    total.value = res.total
  } finally { loading.value = false }
}

const loadViews = async () => {
  try {
    const schema = await getListSchema(appId, listId)
    views.value = schema.views
    const def = schema.views.find(v => v.is_default)
    if (def) {
      activeView.value = def.url_key
      pageSize.value = def.default_page_size
    }
  } catch { /* */ }
}

onMounted(async () => {
  const [schemaRes] = await Promise.all([
    getFormSchema(appId, listId),
    loadViews(),
  ])
  allFields.value = schemaRes.fields
  await loadData()
})

const switchView = (key: string) => {
  if (key === '__edit__') {
    router.push(`/apps/${appId}/lists/${listId}/settings/views`)
    return
  }
  activeView.value = key
  const v = currentView.value
  if (v) pageSize.value = v.default_page_size
  page.value = 1
  loadData()
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const onSortChange = ({ field, order }: any) => {
  sortField.value = (field || '').replace('data.', '')
  sortOrder.value = (order as 'asc' | 'desc') || ''
  page.value = 1
  loadData()
}

const onSelection = ({ records: rows }: { records: RecordItem[] }) => {
  selectedIds.value = rows.map(r => r.id)
}

const onPageSizeChange = (size: number) => {
  pageSize.value = size
  page.value = 1
  loadData()
}

const onPageChange = (p: number) => {
  page.value = p
  loadData()
}

const handleJump = () => {
  const p = parseInt(jumpPage.value, 10)
  if (p < 1 || p > Math.ceil(total.value / pageSize.value)) {
    ElMessage.warning('无效页码')
    return
  }
  page.value = p
  jumpPage.value = ''
  loadData()
}

const handleView = (row: RecordItem) => {
  router.push(`/apps/${appId}/lists/${listId}/data/${row.id}`)
}

const handleDelete = async (id: string) => {
  await deleteRecord(appId, listId, id)
  ElMessage.success('已删除')
  loadData()
}

const handleBatchDelete = async () => {
  const { batchUpdate } = await import('../../api/records')
  try {
    await batchUpdate(appId, listId, { action: 'delete', ids: selectedIds.value })
    ElMessage.success(`已删除 ${selectedIds.value.length} 条`)
    selectedIds.value = []
    loadData()
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  }
}
</script>
