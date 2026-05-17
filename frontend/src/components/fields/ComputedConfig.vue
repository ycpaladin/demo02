<template>
  <div>
    <el-divider content-position="left">计算值配置</el-divider>
    <el-form-item label="表达式" prop="expression">
      <el-input v-model="form.expression" type="textarea" :rows="3" placeholder="使用 {field_key} 引用字段，如: {last_name}{first_name}" />
    </el-form-item>
    <el-alert type="warning" :closable="false" show-icon title="被引用的字段必须在同一内容类型中已存在。不能引用自身或其他计算值字段。" />
  </div>
</template>

<script setup lang="ts">
export interface ComputedConfigForm {
  expression: string
}

defineProps<{
  form: ComputedConfigForm
}>()
</script>
