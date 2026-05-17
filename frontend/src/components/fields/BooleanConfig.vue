<template>
  <div>
    <el-divider content-position="left">布尔配置</el-divider>
    <el-form-item label="呈现">
      <el-radio-group v-model="form.boolean_display">
        <el-radio value="switch">开关</el-radio>
        <el-radio value="radio">单选按钮</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="true 显示值">
      <el-input v-model="form.boolean_true_label" maxlength="20" placeholder="是" />
    </el-form-item>
    <el-form-item label="false 显示值">
      <el-input v-model="form.boolean_false_label" maxlength="20" placeholder="否" />
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
export interface BooleanConfigForm {
  boolean_display: string
  boolean_true_label: string
  boolean_false_label: string
}

defineProps<{
  form: BooleanConfigForm
}>()
</script>
