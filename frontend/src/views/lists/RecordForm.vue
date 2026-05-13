<template>
  <AppLayout>
    <el-page-header @back="$router.back()" :content="isEdit ? '编辑记录' : '新增记录'" />
    <el-card style="margin-top:16px;max-width:800px;">
      <DynamicForm ref="formRef" :fields="fields" :initialData="initialData" />
      <div style="margin-top:20px;">
        <el-button type="primary" @click="submit" :loading="submitting">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFormSchema } from '../../api/lists'
import { getRecord, createRecord, updateRecord } from '../../api/records'
import AppLayout from '../../components/AppLayout.vue'
import DynamicForm from '../../components/DynamicForm.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId
const listId = route.params.listId
const recordId = route.params.recordId
const isEdit = computed(() => !!recordId)

const fields = ref([])
const initialData = ref({})
const formRef = ref(null)
const submitting = ref(false)

onMounted(async () => {
  const schema = await getFormSchema(appId, listId)
  fields.value = schema.fields
  if (isEdit.value) {
    const record = await getRecord(appId, listId, recordId)
    initialData.value = record.data || {}
  }
})

const submit = async () => {
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    const data = formRef.value.getData()
    if (isEdit.value) {
      await updateRecord(appId, listId, recordId, data)
    } else {
      await createRecord(appId, listId, data)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    router.push(`/apps/${appId}/lists/${listId}/data`)
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    submitting.value = false
  }
}
</script>
