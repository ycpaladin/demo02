<template>
  <AppLayout>
    <el-page-header @back="$router.back()" :content="pageTitle" />
    <el-card style="margin-top:16px;max-width:800px;">
      <DynamicForm ref="formRef" :fields="fields" :initialData="initialData" :readonly="isView" :formLayout="formLayout" />
      <div v-if="!isView" style="margin-top:20px;">
        <el-button type="primary" @click="submit" :loading="submitting">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
      <div v-else style="margin-top:20px;">
        <el-button @click="$router.back()">返回</el-button>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFormSchema, getListSchema } from '../../api/lists'
import { getRecord, createRecord, updateRecord } from '../../api/records'
import AppLayout from '../../components/AppLayout.vue'
import DynamicForm from '../../components/DynamicForm.vue'
import { ElMessage } from 'element-plus'
import type { FormField, SchemaForm } from '../../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const listId = route.params.listId as string
const recordId = route.params.recordId as string | undefined

const isEdit = computed(() => route.name === 'recordEdit')
const isView = computed(() => route.name === 'recordView')
const pageTitle = computed(() => isView.value ? '查看记录' : isEdit.value ? '编辑记录' : '新增记录')

const fields = ref<FormField[]>([])
const initialData = ref<Record<string, unknown>>({})
const formLayout = ref<SchemaForm>({ groups: [] })
const formRef = ref<InstanceType<typeof DynamicForm>>()
const submitting = ref(false)

onMounted(async () => {
  const [schema, layout] = await Promise.all([
    getFormSchema(appId, listId),
    getListSchema(appId, listId),
  ])
  fields.value = schema.fields
  formLayout.value = layout.form || { groups: [] }
  if (recordId) {
    const record = await getRecord(appId, listId, recordId)
    initialData.value = record.data || {}
  }
})

const submit = async () => {
  try { await formRef.value!.validate() } catch { return }
  submitting.value = true
  try {
    const data = formRef.value!.getData()
    if (recordId) {
      await updateRecord(appId, listId, recordId, data)
    } else {
      await createRecord(appId, listId, data)
    }
    ElMessage.success(recordId ? '更新成功' : '创建成功')
    router.push(`/apps/${appId}/lists/${listId}/data`)
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally {
    submitting.value = false
  }
}
</script>
