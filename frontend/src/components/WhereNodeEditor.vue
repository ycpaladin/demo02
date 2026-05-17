<template>
  <div style="margin:4px 0;">
    <!-- 分支节点 -->
    <template v-if="'logic' in modelValue">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <el-select :model-value="modelValue.logic" @update:model-value="onLogicChange" style="width:80px;" size="small">
          <el-option label="AND" value="AND" />
          <el-option label="OR" value="OR" />
        </el-select>
        <el-button size="small" @click="wrapInGroup">分组</el-button>
        <el-button size="small" @click="addCondition('left')">+ 条件</el-button>
        <el-button size="small" @click="addCondition('right')" v-if="!modelValue.right">+ 条件</el-button>
        <el-button size="small" type="danger" @click="$emit('remove')" v-if="$attrs.onRemove !== undefined">× 删除组</el-button>
      </div>
      <div style="margin-left:24px;padding-left:16px;border-left:2px solid #e4e7ed;">
        <WhereNodeEditor v-model="modelValue.left" :fields="fields" @remove="removeChild('left')" />
        <div v-if="modelValue.right" style="margin-top:4px;">
          <WhereNodeEditor v-model="modelValue.right" :fields="fields" @remove="removeChild('right')" />
        </div>
      </div>
    </template>

    <!-- 叶子节点 -->
    <template v-else>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <el-select :model-value="modelValue.field" @update:model-value="onFieldChange" placeholder="字段" style="width:150px;" size="small">
          <el-option v-for="f in fields" :key="f" :label="f" :value="f" />
        </el-select>
        <el-select :model-value="modelValue.comparison" @update:model-value="onCmpChange" style="width:130px;" size="small">
          <el-option label="等于" value="=" />
          <el-option label="不等于" value="<>" />
          <el-option label="大于" value=">" />
          <el-option label="大于等于" value=">=" />
          <el-option label="小于" value="<" />
          <el-option label="小于等于" value="<=" />
          <el-option label="包含" value="包含" />
        </el-select>
        <el-input
          :model-value="modelValue.value"
          @update:model-value="onValueChange"
          placeholder="值"
          style="width:150px;"
          size="small"
        />
        <el-button size="small" @click="wrapInGroup">分组</el-button>
        <el-button size="small" type="danger" @click="$emit('remove')" v-if="$attrs.onRemove !== undefined">×</el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { WhereNode } from '../types'

const props = defineProps<{
  modelValue: WhereNode
  fields: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: WhereNode]
  remove: []
}>()

function onFieldChange(v: string) {
  emit('update:modelValue', { ...props.modelValue, field: v } as WhereNode)
}
function onCmpChange(v: string) {
  emit('update:modelValue', { ...props.modelValue, comparison: v } as WhereNode)
}
function onValueChange(v: string) {
  emit('update:modelValue', { ...props.modelValue, value: v } as WhereNode)
}
function onLogicChange(v: string) {
  emit('update:modelValue', { ...props.modelValue, logic: v } as WhereNode)
}

function wrapInGroup() {
  const inner = JSON.parse(JSON.stringify(props.modelValue))
  emit('update:modelValue', {
    logic: 'AND',
    left: inner,
  } as WhereNode)
}

function addCondition(side: 'left' | 'right') {
  const node = JSON.parse(JSON.stringify(props.modelValue))
  const leaf = { field: '', comparison: '=', value: '' } as WhereNode
  if (side === 'right') {
    node.right = leaf
  } else if (!node.left) {
    node.left = leaf
  } else if (!node.right) {
    node.right = leaf
  }
  emit('update:modelValue', node)
}

function removeChild(side: 'left' | 'right') {
  const node = JSON.parse(JSON.stringify(props.modelValue))
  if (side === 'right') {
    delete node.right
  } else {
    // If we remove left, promote right or become a leaf
    if (node.right) {
      emit('update:modelValue', node.right as WhereNode)
    } else {
      emit('update:modelValue', { field: '', comparison: '=', value: '' } as WhereNode)
    }
    return
  }
  emit('update:modelValue', node)
}
</script>
