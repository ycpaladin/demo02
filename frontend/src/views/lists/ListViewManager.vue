<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/lists/${listId}/settings`)" content="视图管理" style="margin-bottom:24px;" />

    <el-card style="max-width:960px;">
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between;">
          <span style="font-weight:bold;">视图列表</span>
          <el-tag v-if="dirty" type="warning" size="small">未保存</el-tag>
        </div>
      </template>

      <el-table :data="localViews" row-key="_idx">
        <el-table-column label="排序" width="80">
          <template #default="{ row, $index }">
            <el-button link size="small" :disabled="$index === 0" @click="handleMoveUp($index)"><el-icon><ArrowUp /></el-icon></el-button>
            <el-button link size="small" :disabled="$index === localViews.length - 1" @click="handleMoveDown($index)"><el-icon><ArrowDown /></el-icon></el-button>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column label="默认视图" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
            <span v-else style="color:#c0c4cc;">—</span>
          </template>
        </el-table-column>
        <el-table-column label="显示字段数" width="120">
          <template #default="{ row }">
            {{ row.fields?.filter((f: any) => f.visible).length || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="分页大小" width="120">
          <template #default="{ row }">{{ row.default_page_size || 20 }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row, $index }">
            <el-button link type="primary" @click="openEdit($index)">编辑</el-button>
            <el-popconfirm v-if="!row.is_default" title="确认删除?" @confirm="handleDelete($index)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-button style="margin-top:12px;" @click="openAdd">新增视图</el-button>

      <div v-if="dirty" style="margin-top:16px;padding-top:16px;border-top:1px solid #e4e7ed;display:flex;gap:12px;">
        <el-button type="primary" @click="handleSave" :loading="saving">保存更改</el-button>
        <el-button @click="handleCancel">放弃更改</el-button>
      </div>
    </el-card>

    <!-- 新增/编辑视图对话框 -->
    <el-dialog v-model="showDialog" :title="editingIdx >= 0 ? '编辑视图' : '新增视图'" width="800px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="视图名称" required>
          <el-input v-model="form.name" maxlength="64" />
        </el-form-item>
        <el-form-item label="URL 标识">
          <el-input v-model="form.url_key" :disabled="editingIdx >= 0" placeholder="小写字母/数字/下划线" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" maxlength="255" />
        </el-form-item>

        <el-divider content-position="left">显示字段</el-divider>
        <el-checkbox v-model="form._selectAll" @change="onSelectAllFields" style="margin-bottom:8px;">全选/全不选</el-checkbox>
        <div v-for="(f, i) in form.fields" :key="f.key" style="display:flex;align-items:center;gap:8px;padding:4px 0;">
          <el-icon style="cursor:move;"><Rank /></el-icon>
          <el-checkbox v-model="f.visible" />
          <span style="flex:1;">{{ f.key }}</span>
          <el-button link size="small" :disabled="i === 0" @click="moveField(Number(i), -1)">↑</el-button>
          <el-button link size="small" :disabled="i === form.fields.length - 1" @click="moveField(Number(i), 1)">↓</el-button>
        </div>

        <el-divider content-position="left">查询条件</el-divider>
        <div style="margin-bottom:8px;">
          <el-radio-group v-model="form._hasWhere" size="small">
            <el-radio :value="false">无筛选</el-radio>
            <el-radio :value="true">条件筛选</el-radio>
          </el-radio-group>
        </div>
        <div v-if="form._hasWhere && form._where" style="margin-left:8px;padding-left:16px;border-left:2px solid #409eff;">
          <WhereNodeEditor v-model="form._where" :fields="allFieldKeys" />
        </div>

        <el-divider content-position="left">排序设置</el-divider>
        <div v-for="(ob, i) in form._orderBy" :key="i" style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
          <el-select v-model="ob.field" placeholder="选择字段" style="width:200px;">
            <el-option v-for="f in allFieldKeys" :key="f" :label="f" :value="f" />
          </el-select>
          <el-select v-model="ob.sort" style="width:120px;">
            <el-option label="升序" value="ASC" />
            <el-option label="降序" value="DESC" />
          </el-select>
          <el-button link type="danger" @click="form._orderBy.splice(i, 1)">×</el-button>
        </div>
        <el-button size="small" @click="form._orderBy.push({ field: '', sort: 'DESC' })">+ 添加排序</el-button>

        <el-divider content-position="left">分页设置</el-divider>
        <el-form-item label="分页大小选项">
          <el-input v-model="form._pageSizeStr" placeholder="每行一个数字，如 10" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="默认分页大小">
          <el-input-number v-model="form.default_page_size" :min="1" :max="100" />
        </el-form-item>

        <el-form-item label="设为默认视图">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleFormSubmit">确定</el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowUp, ArrowDown, Rank } from '@element-plus/icons-vue'
import { getListSchema, getFormSchema, updateListSchema } from '../../api/lists'
import AppLayout from '../../components/AppLayout.vue'
import WhereNodeEditor from '../../components/WhereNodeEditor.vue'
import { ElMessage } from 'element-plus'
import type { SchemaView, SchemaField, WhereNode } from '../../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string
const listId = route.params.listId as string

const allFields = ref<SchemaField[]>([])
const allFieldKeys = ref<string[]>([])
const localViews = ref<(SchemaView & { _idx: number })[]>([])
const originalJson = ref('')
const dirty = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editingIdx = ref(-1)

function makeLeaf(field?: string): WhereNode {
  return { field: field || '', comparison: '=', value: '' }
}

const getDefaultForm = (): any => ({
  name: '', url_key: '', description: '',
  is_default: false,
  fields: [] as { key: string; visible: boolean }[],
  _orderBy: [] as { field: string; sort: string }[],
  _pageSizeStr: '10\n20\n50\n100',
  default_page_size: 20,
  _selectAll: true,
  _hasWhere: false,
  _where: makeLeaf(),
})

const form = reactive(getDefaultForm())

onMounted(async () => {
  const [schema, formSchema] = await Promise.all([
    getListSchema(appId, listId),
    getFormSchema(appId, listId),
  ])
  allFields.value = schema.fields
  allFieldKeys.value = formSchema.fields.map(f => f.key)

  localViews.value = schema.views.map((v, i) => ({ ...v, _idx: i }))
  originalJson.value = JSON.stringify(schema.views)
})

const markDirty = () => { dirty.value = true }

const handleMoveUp = (idx: number) => {
  if (idx <= 0) return
  ;[localViews.value[idx - 1], localViews.value[idx]] = [localViews.value[idx], localViews.value[idx - 1]]
  markDirty()
}
const handleMoveDown = (idx: number) => {
  if (idx >= localViews.value.length - 1) return
  ;[localViews.value[idx], localViews.value[idx + 1]] = [localViews.value[idx + 1], localViews.value[idx]]
  markDirty()
}
const handleDelete = (idx: number) => {
  localViews.value.splice(idx, 1)
  markDirty()
}

const openAdd = () => {
  editingIdx.value = -1
  Object.assign(form, getDefaultForm())
  form.fields = allFieldKeys.value.map(k => ({ key: k, visible: true }))
  showDialog.value = true
}

const openEdit = (idx: number) => {
  editingIdx.value = idx
  const v = localViews.value[idx]
  const hasWhere = !!(v as any).where
  Object.assign(form, {
    name: v.name,
    url_key: v.url_key,
    description: (v as any).description || '',
    is_default: v.is_default,
    fields: v.fields?.length
      ? v.fields.map(f => ({ ...f }))
      : allFieldKeys.value.map(k => ({ key: k, visible: true })),
    _orderBy: (v.orderBy || []).map(ob => ({ ...ob })),
    _pageSizeStr: (v.page_size_options || [10, 20, 50, 100]).join('\n'),
    default_page_size: v.default_page_size || 20,
    _selectAll: (v.fields || []).every(f => f.visible),
    _hasWhere: hasWhere,
    _where: hasWhere ? JSON.parse(JSON.stringify((v as any).where)) : makeLeaf(),
  })
  showDialog.value = true
}

const onSelectAllFields = (val: boolean) => {
  form.fields.forEach((f: { visible: boolean }) => { f.visible = val })
}

const moveField = (i: number, dir: number) => {
  const arr = form.fields
  const t = i + dir
  if (t < 0 || t >= arr.length) return
  ;[arr[i], arr[t]] = [arr[t], arr[i]]
}

const handleFormSubmit = () => {
  const pageSizes = form._pageSizeStr
    .split('\n')
    .map((s: string) => parseInt(s.trim(), 10))
    .filter((n: number) => !isNaN(n) && n > 0)
  const viewData: any = {
    url_key: form.url_key || `view_${Date.now()}`,
    name: form.name || '未命名视图',
    is_default: form.is_default,
    fields: form.fields,
    orderBy: form._orderBy.filter((ob: any) => ob.field),
    page_size_options: pageSizes.length ? pageSizes : [10, 20, 50],
    default_page_size: form.default_page_size || 20,
  }
  if (form._hasWhere && form._where) {
    viewData.where = form._where
  }

  if (editingIdx.value >= 0) {
    const existing = localViews.value[editingIdx.value]
    viewData.id = existing.id
    viewData.url_key = existing.url_key
    localViews.value[editingIdx.value] = { ...viewData, _idx: existing._idx }
  } else {
    viewData.id = `__new_${Date.now()}`
    localViews.value.push({ ...viewData, _idx: localViews.value.length })
  }

  showDialog.value = false
  markDirty()
}

const handleSave = async () => {
  saving.value = true
  try {
    const schema = await getListSchema(appId, listId)
    const views = localViews.value.map(({ _idx, ...v }) => v)

    // 确保有且仅有一个默认视图
    const defaults = views.filter(v => v.is_default)
    if (defaults.length !== 1) {
      ElMessage.error('必须有且仅有一个默认视图')
      saving.value = false
      return
    }

    schema.views = views
    // 只提交扩展字段，过滤掉继承字段
    schema.fields = schema.fields.filter((f: any) => f.is_extension).map(({ is_extension, ...f }: any) => f)
    await updateListSchema(appId, listId, schema)

    const updated = await getListSchema(appId, listId)
    localViews.value = updated.views.map((v, i) => ({ ...v, _idx: i }))
    originalJson.value = JSON.stringify(updated.views)
    dirty.value = false
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  } finally { saving.value = false }
}

const handleCancel = () => {
  const views = JSON.parse(originalJson.value) as SchemaView[]
  localViews.value = views.map((v, i) => ({ ...v, _idx: i }))
  dirty.value = false
}
</script>
