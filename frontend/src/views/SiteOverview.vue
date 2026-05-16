<template>
  <AppLayout>
    <el-page-header @back="router.push(`/apps/${appId}/lists`)" content="网站所有内容" style="margin-bottom:16px;" />

    <section v-if="lists.length" style="margin-bottom:24px;">
      <h3 style="margin-bottom:12px;">列表 ({{ lists.length }})</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <el-card v-for="lst in lists" :key="lst.id" shadow="hover" style="width:220px;">
          <template #header>
            <span style="font-weight:bold;">{{ lst.name }}</span>
          </template>
          <p style="margin:0 0 4px;color:#909399;font-size:13px;">{{ lst.key }}</p>
          <p style="margin:0 0 8px;color:#606266;font-size:12px;">{{ lst.url }}</p>
          <el-button size="small" type="primary" @click="router.push(`/apps/${appId}/lists/${lst.id}/data`)">进入</el-button>
        </el-card>
      </div>
    </section>

    <section v-if="children.length">
      <h3 style="margin-bottom:12px;">子站点 ({{ children.length }})</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <el-card v-for="child in children" :key="child.id" shadow="hover" style="width:220px;">
          <template #header>
            <span style="font-weight:bold;">{{ child.name }}</span>
          </template>
          <p style="margin:0 0 4px;color:#909399;font-size:13px;">{{ child.key }}</p>
          <p style="margin:0 0 8px;color:#606266;font-size:12px;">{{ child.url_prefix }}</p>
          <el-button size="small" type="primary" @click="router.push(`/apps/${child.id}/lists`)">进入</el-button>
        </el-card>
      </div>
    </section>

    <el-empty v-if="!lists.length && !children.length" description="暂无内容" />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import { getLists } from '../api/lists'
import { getApps } from '../api/applications'
import type { ListModel, Application } from '../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string

const lists = ref<ListModel[]>([])
const children = ref<Application[]>([])

onMounted(async () => {
  try { lists.value = await getLists(appId) } catch { /* */ }
  try {
    const all = await getApps()
    children.value = all.filter(a => a.parent === appId)
  } catch { /* */ }
})
</script>
