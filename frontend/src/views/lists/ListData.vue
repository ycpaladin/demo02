<template>
  <AppLayout>
    <div v-if="loading">加载中...</div>
    <template v-else>
      <ViewTabs :views="views" :activeKey="activeView" @change="switchView" @add="showAddView = true" />
      <DynamicSearchBar :searchableFields="searchableFields" @search="onSearch" @reset="resetSearch" />
      <div style="margin-bottom:12px;display:flex;gap:8px;">
        <el-button type="primary" @click="$router.push(`/apps/${appId}/lists/${listId}/data/add`)">新增</el-button>
        <el-button :disabled="selectedIds.length === 0" @click="showBatchEdit = true">批量编辑</el-button>
      </div>
      <el-table :data="records" @selection-change="onSelection" stripe border>
        <el-table-column type="selection" width="50" />
        <el-table-column v-for="col in visibleColumns" :key="col.key" :prop="`data.${col.key}`" :label="col.name" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/apps/${appId}/lists/${listId}/data/${row.id}/edit`)">编辑</el-button>
            <el-popconfirm title="确认删除?" @confirm="handleDelete(row.id)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end;" @current-change="loadData" />
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getListViews, createListView, getFormSchema } from '../../api/lists'
import { getRecords, deleteRecord, batchUpdate } from '../../api/records'
import AppLayout from '../../components/AppLayout.vue'
import ViewTabs from '../../components/ViewTabs.vue'
import DynamicSearchBar from '../../components/DynamicSearchBar.vue'
import { ElMessage } from 'element-plus'
import type { FormField, ListView, RecordItem } from '../../types'

const route = useRoute()
const appId = route.params.appId as string
const listId = route.params.listId as string

const loading = ref(true)
const allFields = ref<FormField[]>([])
const records = ref<RecordItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterStr = ref('')
const views = ref<ListView[]>([])
const activeView = ref('default')
const selectedIds = ref<string[]>([])
const showBatchEdit = ref(false)

const searchableFields = computed(() => allFields.value.filter(f => f.searchable))
const visibleColumns = computed(() => {
  const cv = views.value.find(v => v.url_key === activeView.value)
  if (cv?.config?.visible_fields?.length) {
    return allFields.value.filter(f => cv.config.visible_fields!.includes(f.key))
  }
  return allFields.value
})

const loadData = async () => {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: pageSize.value }
    if (filterStr.value) params.filter = filterStr.value
    if (activeView.value) params.view = activeView.value
    const res = await getRecords(appId, listId, params)
    records.value = res.results
    total.value = res.total
  } finally { loading.value = false }
}

onMounted(async () => {
  const [schemaRes, viewsRes] = await Promise.all([
    getFormSchema(appId, listId),
    getListViews(listId),
  ])
  allFields.value = schemaRes.fields
  views.value = viewsRes
  await loadData()
})

const onSearch = (f: string) => { filterStr.value = f; page.value = 1; loadData() }
const resetSearch = () => { filterStr.value = ''; page.value = 1; loadData() }
const switchView = (key: string) => { activeView.value = key; loadData() }
const onSelection = (rows: RecordItem[]) => { selectedIds.value = rows.map(r => r.id) }
const handleDelete = async (id: string) => { await deleteRecord(appId, listId, id); loadData() }
</script>
