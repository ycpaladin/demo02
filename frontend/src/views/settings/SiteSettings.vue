<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/lists`)" content="站点设置" style="margin-bottom:24px;" />

    <div style="display:flex;gap:12px;flex-wrap:wrap;">
      <el-card v-for="card in cards" :key="card.route" shadow="hover" style="width:180px;cursor:pointer;" @click="router.push(`/apps/${appId}/settings/${card.route}`)">
        <div style="text-align:center;padding:16px 0;">
          <el-icon :size="28" style="margin-bottom:8px;color:#409eff;"><component :is="card.icon" /></el-icon>
          <div style="font-size:15px;font-weight:500;">{{ card.label }}</div>
        </div>
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { Setting, Document, List, Menu, Delete } from '@element-plus/icons-vue'
import AppLayout from '../../components/AppLayout.vue'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string

const cards = [
  { label: '站点信息', route: 'info', icon: Setting },
  { label: '内容类型', route: 'content-types', icon: Document },
  { label: '字段管理', route: 'field-types', icon: List },
  { label: '菜单配置', route: 'navigations', icon: Menu },
  { label: '回收站', route: 'trash', icon: Delete },
]
</script>
