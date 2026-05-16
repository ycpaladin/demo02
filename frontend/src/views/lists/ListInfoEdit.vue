<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/lists/${listId}/settings`)" content="列表基本信息" style="margin-bottom:24px;" />
    <el-card style="max-width:600px;">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
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
import { getList, updateList } from '../../api/lists'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { ListModel } from '../../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const listId = route.params.listId as string
const saving = ref(false)
const form = ref<Partial<ListModel>>({ name: '', description: '' })

onMounted(async () => {
  try {
    const lst = await getList(appId, listId)
    form.value = { name: lst.name, description: lst.description }
  } catch { /* */ }
})

const handleSave = async () => {
  saving.value = true
  try {
    await updateList(appId, listId, form.value)
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}
</script>
