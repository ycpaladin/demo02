<template>
  <div>
    <el-divider content-position="left">附件配置</el-divider>
    <el-form-item label="最大文件数">
      <el-input-number v-model="form.max_files" :min="1" :max="50" :step="1" controls-position="right" />
    </el-form-item>
    <el-form-item label="允许的文件类型" prop="allowed_file_types">
      <el-select v-model="form.allowed_file_types" multiple placeholder="至少选择一项" style="width:100%;">
        <el-option label="全部" value="all" />
        <el-option label="图片" value="image" />
        <el-option label="文档" value="document" />
        <el-option label="视频" value="video" />
        <el-option label="音频" value="audio" />
      </el-select>
    </el-form-item>
    <el-form-item label="单文件最大大小 (MB)">
      <el-input-number v-model="form.max_file_size" :min="1" :max="100" :step="1" controls-position="right" />
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
export interface AttachmentConfigForm {
  max_files: number | null
  allowed_file_types: string[]
  max_file_size: number
}

defineProps<{
  form: AttachmentConfigForm
}>()
</script>
