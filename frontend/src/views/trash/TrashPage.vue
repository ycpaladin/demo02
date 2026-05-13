<template>
  <AppLayout>
    <h2>回收站</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="已删除列表" name="lists">
        <el-table :data="deletedLists">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="deleted_at" label="删除时间" />
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button link type="success" @click="restore(row.id, 'list')">恢复</el-button>
              <el-popconfirm title="彻底删除?" @confirm="forceDelete(row.id, 'list')">
                <template #reference><el-button link type="danger">彻底删除</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="已删除记录" name="records">
        <el-table :data="deletedRecords">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="deleted_at" label="删除时间" />
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button link type="success" @click="restore(row.id, 'record', row.list_id)">恢复</el-button>
              <el-popconfirm title="彻底删除?" @confirm="forceDelete(row.id, 'record', row.list_id)">
                <template #reference><el-button link type="danger">彻底删除</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getTrash, restoreItem, permanentDelete } from '../../api/trash'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const appId = route.params.appId
const activeTab = ref('lists')
const items = ref([])
const deletedLists = computed(() => items.value.filter(i => i.type === 'list'))
const deletedRecords = computed(() => items.value.filter(i => i.type === 'record'))

onMounted(async () => { items.value = await getTrash(appId) })

const restore = async (id, type, listId) => {
  await restoreItem(appId, id, { type, list_id: listId })
  ElMessage.success('已恢复')
  items.value = await getTrash(appId)
}

const forceDelete = async (id, type, listId) => {
  await permanentDelete(appId, id, { params: { type, list_id: listId } })
  ElMessage.success('已彻底删除')
  items.value = await getTrash(appId)
}
</script>
