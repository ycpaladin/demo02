<template>
  <div>
    <el-divider content-position="left">文本配置</el-divider>
    <el-form-item label="类型" prop="text_type">
      <el-radio-group v-model="form.text_type">
        <el-radio value="single_line">单行</el-radio>
        <el-radio value="multi_line">多行</el-radio>
        <el-radio value="long_text">长文本</el-radio>
      </el-radio-group>
    </el-form-item>
    <template v-if="form.text_type !== 'long_text'">
      <el-form-item label="最小长度">
        <el-input-number v-model="form.min_length" :min="0" :step="1" :max="form.max_length ?? undefined" controls-position="right" />
      </el-form-item>
      <el-form-item label="最大长度">
        <el-input-number v-model="form.max_length" :min="form.min_length ?? 0" :step="1" controls-position="right" />
      </el-form-item>
    </template>
    <template v-if="form.text_type !== 'single_line'">
      <el-form-item label="行数">
        <el-input-number v-model="form.rows" :min="1" :max="20" :step="1" controls-position="right" />
      </el-form-item>
    </template>
    <template v-if="form.text_type === 'long_text'">
      <el-form-item label="支持富文本">
        <el-switch v-model="form.rich_text" />
      </el-form-item>
    </template>
  </div>
</template>

<script setup lang="ts">
export interface TextConfigForm {
  text_type: string
  min_length: number | null
  max_length: number | null
  rows: number | null
  rich_text: boolean
}

defineProps<{
  form: TextConfigForm
}>()

// When type changes, parent handles default values for rows (3 for multi_line, 10 for long_text)
</script>
