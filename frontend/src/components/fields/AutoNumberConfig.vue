<template>
  <div>
    <el-divider content-position="left">自动编号配置</el-divider>
    <el-form-item label="生成规则" prop="auto_rule">
      <el-select v-model="form.auto_rule" style="width:100%;">
        <el-option label="前缀+序号" value="prefix_seq" />
        <el-option label="日期+序号" value="date_seq" />
        <el-option label="纯序号" value="pure_seq" />
        <el-option label="随机码" value="random" />
      </el-select>
    </el-form-item>
    <template v-if="form.auto_rule === 'prefix_seq' || form.auto_rule === 'date_seq'">
      <el-form-item label="前缀">
        <el-input v-model="form.auto_prefix" maxlength="20" placeholder="如: CASE-" />
      </el-form-item>
    </template>
    <template v-if="form.auto_rule === 'prefix_seq' || form.auto_rule === 'pure_seq'">
      <el-form-item label="起始序号">
        <el-input-number v-model="form.auto_start" :min="1" :step="1" controls-position="right" />
      </el-form-item>
    </template>
    <template v-if="form.auto_rule !== 'random'">
      <el-form-item label="序号位数">
        <el-input-number v-model="form.auto_digits" :min="2" :max="12" :step="1" controls-position="right" />
        <span style="margin-left:8px;color:#909399;">示例: {{ '0'.repeat(form.auto_digits) }}</span>
      </el-form-item>
    </template>
    <template v-if="form.auto_rule === 'date_seq'">
      <el-form-item label="日期格式">
        <el-select v-model="form.auto_date_format" style="width:100%;">
          <el-option label="YYYYMMDD" value="YYYYMMDD" />
          <el-option label="YYMMDD" value="YYMMDD" />
          <el-option label="YYYYMM" value="YYYYMM" />
          <el-option label="YYMM" value="YYMM" />
        </el-select>
      </el-form-item>
    </template>
    <template v-if="form.auto_rule === 'random'">
      <el-form-item label="随机码长度">
        <el-input-number v-model="form.auto_random_length" :min="4" :max="32" :step="1" controls-position="right" />
      </el-form-item>
      <el-form-item label="随机码字符集" prop="auto_random_charset">
        <el-checkbox-group v-model="form.auto_random_charset">
          <el-checkbox value="upper">大写字母</el-checkbox>
          <el-checkbox value="lower">小写字母</el-checkbox>
          <el-checkbox value="digit">数字</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </template>
    <el-alert type="info" :closable="false" show-icon title="自动编号在创建记录时由系统生成，表单中只读展示" />
  </div>
</template>

<script setup lang="ts">
export interface AutoNumberConfigForm {
  auto_rule: string
  auto_prefix: string
  auto_start: number
  auto_digits: number
  auto_date_format: string
  auto_random_length: number
  auto_random_charset: string[]
}

defineProps<{
  form: AutoNumberConfigForm
}>()
</script>
