<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/settings`)" content="站点信息" style="margin-bottom:24px;" />
    <el-card style="max-width:600px;">
      <el-form :model="form" label-width="100px" @submit.prevent="handleSave">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="标识">
          <el-input v-model="form.key" />
        </el-form-item>
        <el-form-item label="URL前缀">
          <el-input v-model="form.url_prefix" placeholder="/" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getApp, updateApp } from '../../api/applications'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { Application } from '../../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const saving = ref(false)
const form = ref<Partial<Application>>({ name: '', key: '', description: '', url_prefix: '/' })

onMounted(async () => {
  try {
    const app = await getApp(appId)
    form.value = { name: app.name, key: app.key, description: app.description, url_prefix: app.url_prefix }
  } catch { /* */ }
})

const handleSave = async () => {
  saving.value = true
  try {
    await updateApp(appId, form.value)
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}
</script>
