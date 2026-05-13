<template>
  <AppLayout>
    <h2>内容类型</h2>
    <el-button type="primary" @click="showCreate = true">新建内容类型</el-button>
    <el-table :data="types" style="margin-top:16px;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="key" label="标识" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/apps/${appId}/content-types/${row.id}`)">设计</el-button>
          <el-popconfirm title="确认删除?" @confirm="handleDelete(row.id)">
            <template #reference><el-button link type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showCreate" title="新建内容类型">
      <el-form :model="form">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="标识"><el-input v-model="form.key" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="父级内容类型">
          <el-select v-model="form.parent" clearable placeholder="可选">
            <el-option v-for="ct in types" :key="ct.id" :label="ct.name" :value="ct.id" />
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

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getContentTypes, createContentType, deleteContentType } from '../../api/contentTypes'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const appId = route.params.appId
const types = ref([])
const showCreate = ref(false)
const form = ref({ name: '', key: '', description: '', parent: null })

onMounted(async () => { types.value = await getContentTypes() })

const handleCreate = async () => {
  await createContentType(form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  types.value = await getContentTypes()
  form.value = { name: '', key: '', description: '', parent: null }
}

const handleDelete = async (id) => {
  await deleteContentType(id)
  ElMessage.success('已删除')
  types.value = await getContentTypes()
}
</script>
