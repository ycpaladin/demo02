<template>
  <div>
    <el-divider content-position="left">日期配置</el-divider>
    <el-form-item label="日期格式" prop="date_format">
      <el-radio-group v-model="form.date_format">
        <el-radio value="date">日期</el-radio>
        <el-radio value="datetime">日期时间</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="最早日期">
      <el-date-picker v-model="form.min_date" type="date" value-format="YYYY-MM-DD" placeholder="可选" style="width:100%;" />
    </el-form-item>
    <el-form-item label="最晚日期">
      <el-date-picker v-model="form.max_date" type="date" value-format="YYYY-MM-DD" placeholder="可选" style="width:100%;" />
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
export interface DateConfigForm {
  date_format: string
  min_date: string | null
  max_date: string | null
}

defineProps<{
  form: DateConfigForm
}>()
</script>
