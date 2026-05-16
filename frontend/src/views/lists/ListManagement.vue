<template>
  <AppLayout>
    <h2>列表管理</h2>
    <el-button type="primary" @click="showCreate = true">新建列表</el-button>
    <el-table :data="lists" style="margin-top:16px;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="key" label="标识" />
      <el-table-column prop="url" label="URL" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/apps/${appId}/lists/${row.id}/data`)">数据</el-button>
          <el-button link type="primary" @click="$router.push(`/apps/${appId}/lists/${row.id}/design`)">设计</el-button>
          <el-button link type="primary" @click="$router.push(`/apps/${appId}/lists/${row.id}/settings`)">设置</el-button>
          <el-popconfirm title="确认删除?" @confirm="handleDelete(row.id)">
            <template #reference><el-button link type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showCreate" title="新建列表" width="500px">
      <el-form :model="form">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="标识"><el-input v-model="form.key" /></el-form-item>
        <el-form-item label="URL"><el-input v-model="form.url" :placeholder="defaultUrl" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="内容类型">
          <el-select v-model="form.content_type" placeholder="可选（绑定内容类型）" clearable>
            <el-option v-for="ct in contentTypes" :key="ct.id" :label="ct.name" :value="ct.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getLists, createList, deleteList } from '../../api/lists'
import { getContentTypes } from '../../api/contentTypes'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { ListModel, ContentType } from '../../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const lists = ref<ListModel[]>([])
const contentTypes = ref<ContentType[]>([])
const showCreate = ref(false)
const form = ref<Partial<ListModel>>({ name: '', key: '', url: '', description: '', content_type: null })

const defaultUrl = computed(() => `/list${lists.value.length + 1}`)

onMounted(async () => {
  lists.value = await getLists(appId)
  contentTypes.value = await getContentTypes()
  if (route.query.new === '1') {
    showCreate.value = true
    router.replace({ path: route.path })
  }
})

const handleCreate = async () => {
  await createList(appId, form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  lists.value = await getLists(appId)
  form.value = { name: '', key: '', url: '', description: '', content_type: null }
}

const handleDelete = async (id: string) => {
  await deleteList(appId, id)
  ElMessage.success('已移至回收站')
  lists.value = await getLists(appId)
}
</script>
