<template>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
    <el-tag
      v-for="v in views"
      :key="v.url_key"
      :type="activeKey === v.url_key ? '' : 'info'"
      :effect="activeKey === v.url_key ? 'dark' : 'plain'"
      style="cursor:pointer;"
      @click="$emit('change', v.url_key)"
    >
      {{ v.name }}
    </el-tag>
    <el-button size="small" type="primary" link @click="$emit('add')">+ 新建视图</el-button>
  </div>
</template>

<script setup>
defineProps({
  views: { type: Array, default: () => [] },
  activeKey: { type: String, default: 'default' },
})
defineEmits(['change', 'add'])
</script>
