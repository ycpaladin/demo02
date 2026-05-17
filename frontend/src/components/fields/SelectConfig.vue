<template>
  <div>
    <el-divider content-position="left">选项配置</el-divider>
    <el-form-item label="选项列表" prop="options">
      <el-input v-model="form.options" type="textarea" :rows="5" placeholder="每行一个选项" />
    </el-form-item>
    <el-form-item label="类型" prop="select_type">
      <el-radio-group v-model="form.select_type" @change="onSelectTypeChange">
        <el-radio value="single">单选</el-radio>
        <el-radio value="multiple">多选</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="呈现">
      <el-radio-group v-model="form.select_display">
        <template v-if="form.select_type === 'single'">
          <el-radio value="radio">单选按钮组</el-radio>
          <el-radio value="dropdown">下拉列表</el-radio>
        </template>
        <template v-if="form.select_type === 'multiple'">
          <el-radio value="checkbox">复选框组</el-radio>
          <el-radio value="dropdown_multi">下拉列表（多选）</el-radio>
        </template>
      </el-radio-group>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
export interface SelectConfigForm {
  select_type: string
  options: string
  select_display: string
}

const props = defineProps<{
  form: SelectConfigForm
}>()

function onSelectTypeChange() {
  if (props.form.select_type === 'single') {
    props.form.select_display = 'radio'
  } else {
    props.form.select_display = 'dropdown_multi'
  }
}
</script>
