<template>
  <AppLayout>
    <h2>字段类型管理</h2>
    <el-button type="primary" @click="showCreate = true">新增字段类型</el-button>
    <el-table :data="types" style="margin-top:16px;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="key" label="标识" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="builtin" label="内置">
        <template #default="{ row }">{{ row.builtin ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button link type="danger" :disabled="row.builtin" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showCreate" title="新增字段类型">
      <el-form :model="form">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="标识"><el-input v-model="form.key" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
    <h3 style="margin-top:30px;">验证器管理</h3>
    <el-table :data="validators" style="margin-top:12px;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="key" label="标识" />
      <el-table-column prop="rule_type" label="类型" />
      <el-table-column prop="error_message" label="错误提示" />
    </el-table>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFieldTypes, deleteFieldType, createFieldType, getValidators } from '../../api/fieldTypes'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { FieldType, FieldValidator } from '../../types'

const types = ref<FieldType[]>([])
const validators = ref<FieldValidator[]>([])
const showCreate = ref(false)
const form = ref({ name: '', key: '', description: '' })

onMounted(async () => {
  types.value = await getFieldTypes()
  validators.value = await getValidators()
})

const handleCreate = async () => {
  await createFieldType(form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  types.value = await getFieldTypes()
}

const handleDelete = async (id: string) => {
  await deleteFieldType(id)
  ElMessage.success('已删除')
  types.value = await getFieldTypes()
}
</script>
