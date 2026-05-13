<template>
  <div style="padding:20px;">
    <h2>应用列表</h2>
    <el-button type="primary" @click="showCreate = true">新建应用</el-button>
    <el-table :data="apps" style="margin-top:16px;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="key" label="标识" />
      <el-table-column prop="url_prefix" label="URL前缀" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button link type="primary" @click="$router.push(`/apps/${row.id}/lists`)">进入</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showCreate" title="新建应用">
      <el-form :model="form">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="标识"><el-input v-model="form.key" /></el-form-item>
        <el-form-item label="URL前缀"><el-input v-model="form.url_prefix" placeholder="/" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getApps, createApp } from '../../api/applications'
import { ElMessage } from 'element-plus'
import type { Application } from '../../types'

const apps = ref<Application[]>([])
const showCreate = ref(false)
const form = ref<Partial<Application>>({ name: '', key: '', url_prefix: '/', description: '' })

onMounted(async () => { apps.value = await getApps() })
const handleCreate = async () => {
  await createApp(form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  apps.value = await getApps()
}
</script>
