<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/settings`)" content="内容类型" style="margin-bottom:24px;" />

    <el-button type="primary" @click="openCreate">新建内容类型</el-button>

    <el-table :data="types" style="margin-top:16px;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="key" label="标识" />
      <el-table-column label="字段数量" width="100">
        <template #default="{ row }">
          {{ row.fields?.length ?? 0 }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="primary" @click="$router.push(`/apps/${appId}/settings/content-types/${row.id}`)">字段集合</el-button>
          <el-popconfirm title="确认删除?" @confirm="handleDelete(row.id)">
            <template #reference><el-button link type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建 / 编辑对话框 -->
    <el-dialog v-model="showDialog" :title="editingType ? '编辑内容类型' : '新建内容类型'">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="标识" prop="key">
          <el-input v-model="form.key" :disabled="!!editingType" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="父级内容类型">
          <el-select v-model="form.parent" clearable placeholder="可选（不支持修改）" :disabled="!!editingType">
            <el-option v-for="ct in types" :key="ct.id" :label="ct.name" :value="ct.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">
          {{ editingType ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getContentTypes, createContentType, updateContentType, deleteContentType } from '../../api/contentTypes'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { ContentType } from '../../types'
import type { FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string

const types = ref<ContentType[]>([])
const showDialog = ref(false)
const saving = ref(false)
const editingType = ref<ContentType | null>(null)
const formRef = ref()
const form = ref<Partial<ContentType>>({ name: '', key: '', description: '', parent: null })

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  key: [{ required: true, message: '请输入标识', trigger: 'blur' }],
}

onMounted(async () => { types.value = await getContentTypes() })

const openCreate = () => {
  editingType.value = null
  form.value = { name: '', key: '', description: '', parent: null }
  showDialog.value = true
}

const openEdit = (row: ContentType) => {
  editingType.value = row
  form.value = {
    name: row.name,
    key: row.key,
    description: row.description,
    parent: row.parent,
  }
  showDialog.value = true
}

const handleSubmit = async () => {
  try { await formRef.value!.validate() } catch { return }
  saving.value = true
  try {
    if (editingType.value) {
      await updateContentType(editingType.value.id, {
        name: form.value.name,
        key: editingType.value.key,
        description: form.value.description,
        parent: editingType.value.parent,
      })
      ElMessage.success('保存成功')
    } else {
      await createContentType(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    types.value = await getContentTypes()
    form.value = { name: '', key: '', description: '', parent: null }
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}

const handleDelete = async (id: string) => {
  await deleteContentType(id)
  ElMessage.success('已删除')
  types.value = await getContentTypes()
}
</script>
