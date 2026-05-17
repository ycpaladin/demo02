<template>
  <div>
    <el-divider content-position="left">引用配置</el-divider>
    <el-form-item label="引用方式">
      <el-radio-group v-model="form.reference_type">
        <el-radio value="single">单选</el-radio>
        <el-radio value="multiple">多选</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="呈现">
      <el-radio-group v-model="form.reference_display">
        <el-radio value="dropdown">下拉列表</el-radio>
        <el-radio value="tree">树形选择</el-radio>
      </el-radio-group>
    </el-form-item>
    <template v-if="form.reference_display === 'tree'">
      <el-form-item label="展开方式">
        <el-radio-group v-model="form.reference_expand_on">
          <el-radio value="click">点击</el-radio>
          <el-radio value="hover">悬停</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="可搜索">
        <el-switch v-model="form.reference_searchable" />
      </el-form-item>
      <el-form-item label="展开所有节点">
        <el-switch v-model="form.reference_expand_all" />
      </el-form-item>
      <template v-if="form.reference_type === 'multiple'">
        <el-form-item label="选择策略">
          <el-radio-group v-model="form.reference_select_strategy">
            <el-radio value="leaf">仅叶子</el-radio>
            <el-radio value="parent">仅父节点</el-radio>
            <el-radio value="all">全部可选</el-radio>
          </el-radio-group>
        </el-form-item>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
export interface ReferenceConfigForm {
  reference_type: string
  reference_display: string
  reference_select_strategy: string
  reference_expand_on: string
  reference_searchable: boolean
  reference_expand_all: boolean
}

defineProps<{
  form: ReferenceConfigForm
}>()
</script>
