<template>
  <div>
    <el-divider content-position="left">数字配置</el-divider>
    <el-form-item label="最小值">
      <el-input-number v-model="form.min_value" :step="0.01" controls-position="right" />
    </el-form-item>
    <el-form-item label="最大值">
      <el-input-number v-model="form.max_value" :step="0.01" :min="form.min_value ?? undefined" controls-position="right" />
    </el-form-item>
    <el-form-item label="精度">
      <el-input-number v-model="form.precision" :min="0" :max="10" :step="1" controls-position="right" />
      <span style="margin-left:8px;color:#909399;">0=整数，2=两位小数</span>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
export interface NumberConfigForm {
  min_value: number | null
  max_value: number | null
  precision: number | null
}

defineProps<{
  form: NumberConfigForm
}>()
</script>
