<template>
  <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px;">
    <template v-for="field in searchableFields" :key="field.key">
      <el-select
        v-if="field.field_type === 'select' || field.field_type === 'boolean'"
        v-model="filters[field.key]"
        :placeholder="field.name"
        clearable
        style="width:150px;"
        @change="emitSearch"
      >
        <el-option v-if="field.field_type === 'boolean'" v-for="opt in [{label:'是',value:'true'},{label:'否',value:'false'}]" :key="opt.value" :label="opt.label" :value="opt.value" />
        <el-option v-else v-for="opt in (field.options || [])" :key="opt" :label="opt" :value="opt" />
      </el-select>
      <el-input v-else v-model="filters[field.key]" :placeholder="field.name" clearable style="width:180px;" @change="emitSearch" />
    </template>
    <el-button @click="resetFilters">重置</el-button>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import type { FormField } from '../types'

const props = defineProps<{ searchableFields: FormField[] }>()
const emit = defineEmits<{
  search: [filter: string]
  reset: []
}>()

const filters = reactive<Record<string, string>>({})

const emitSearch = () => {
  const parts: string[] = []
  for (const [k, v] of Object.entries(filters)) {
    if (v !== '' && v !== null && v !== undefined) {
      const field = props.searchableFields.find(f => f.key === k)
      if (field) {
        const op = field.search_type === 'fuzzy' ? 'contains' : 'eq'
        parts.push(`${k}:${op}:${v}`)
      }
    }
  }
  emit('search', parts.join(','))
}

const resetFilters = () => {
  for (const k of Object.keys(filters)) { filters[k] = '' }
  emit('reset')
}
</script>
