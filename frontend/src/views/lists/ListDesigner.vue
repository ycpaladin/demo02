<template>
  <AppLayout>
    <h2>列表字段设计</h2>
    <el-button type="primary" @click="showAdd = true">添加字段</el-button>
    <el-table :data="fields" style="margin-top:16px;">
      <el-table-column prop="name" label="字段名" />
      <el-table-column prop="key" label="标识" />
      <el-table-column prop="field_type_name" label="类型" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-popconfirm title="确认删除?" @confirm="handleDeleteField(row.id)">
            <template #reference><el-button link type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showAdd" title="添加字段">
      <el-form :model="fieldForm">
        <el-form-item label="字段名"><el-input v-model="fieldForm.name" /></el-form-item>
        <el-form-item label="标识"><el-input v-model="fieldForm.key" /></el-form-item>
        <el-form-item label="字段类型">
          <el-select v-model="fieldForm.field_type">
            <el-option v-for="ft in fieldTypes" :key="ft.id" :label="ft.name" :value="ft.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="必填"><el-switch v-model="fieldForm.required" /></el-form-item>
        <el-form-item label="可搜索"><el-switch v-model="fieldForm.searchable" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="handleAddField">添加</el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getListFields, createListField, deleteListField } from '../../api/lists'
import { getFieldTypes } from '../../api/fieldTypes'
import AppLayout from '../../components/AppLayout.vue'
import { ElMessage } from 'element-plus'
import type { ListField, FieldType } from '../../types'

const route = useRoute()
const listId = route.params.listId as string
const fields = ref<ListField[]>([])
const fieldTypes = ref<FieldType[]>([])
const showAdd = ref(false)
const fieldForm = ref({ name: '', key: '', field_type: null as string | null, required: false, searchable: false })

onMounted(async () => {
  fields.value = await getListFields(listId)
  fieldTypes.value = await getFieldTypes()
})

const handleAddField = async () => {
  await createListField(listId, fieldForm.value)
  ElMessage.success('添加成功')
  showAdd.value = false
  fieldForm.value = { name: '', key: '', field_type: null as string | null, required: false, searchable: false }
  fields.value = await getListFields(listId)
}

const handleDeleteField = async (id: string) => {
  await deleteListField(listId, id)
  ElMessage.success('已删除')
  fields.value = await getListFields(listId)
}
</script>
