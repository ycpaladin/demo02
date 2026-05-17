<template>
  <el-container style="min-height:100vh">
    <el-aside width="220px">
      <div style="background:#304156;color:#fff;height:100%;padding:16px 0;">
        <div style="padding:0 20px 16px;font-size:18px;font-weight:bold;">{{ siteName }}</div>
        <el-menu
          :default-active="route.path"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
          router
          style="border-right:none;"
        >
          <template v-for="nav in navItems" :key="nav.id">
            <el-menu-item v-if="nav.link_type === 'list' && nav.list" :index="`/apps/${appId}/lists/${nav.list}/data`">
              <el-icon><List /></el-icon>
              <span>{{ nav.name }}</span>
            </el-menu-item>
            <el-menu-item v-else-if="nav.link_type === 'custom_url'" :index="nav.custom_url">
              <el-icon><Link /></el-icon>
              <span>{{ nav.name }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </div>
    </el-aside>
    <el-container>
      <el-header style="background:#fff;border-bottom:1px solid #e4e7ed;display:flex;align-items:center;justify-content:space-between;padding:0 20px;">
        <h3 style="margin:0;">{{ siteName }}</h3>
        <el-dropdown trigger="click" @command="handleCommand">
          <el-button type="default">
            设置 <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="list-settings" v-if="listId">列表设置</el-dropdown-item>
              <el-dropdown-item command="settings">站点设置</el-dropdown-item>
              <el-dropdown-item command="overview">查看网站所有内容</el-dropdown-item>
              <el-dropdown-item command="parent-site" v-if="app?.parent">访问父级站点</el-dropdown-item>
              <el-dropdown-item command="new-list">新建列表</el-dropdown-item>
              <el-dropdown-item command="new-child">新建子站点</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main>
        <slot />
      </el-main>
    </el-container>
  </el-container>

  <!-- 新建子站点对话框 -->
  <el-dialog v-model="showChildDialog" title="新建子站点">
    <el-form :model="childForm">
      <el-form-item label="名称"><el-input v-model="childForm.name" /></el-form-item>
      <el-form-item label="标识"><el-input v-model="childForm.key" /></el-form-item>
      <el-form-item label="描述"><el-input v-model="childForm.description" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showChildDialog = false">取消</el-button>
      <el-button type="primary" @click="handleCreateChild">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { List, Link, ArrowDown } from '@element-plus/icons-vue'
import { getApp, getNavigations, createApp } from '../api/applications'
import { ElMessage } from 'element-plus'
import type { Navigation, Application } from '../types'

const route = useRoute()
const router = useRouter()
const appId = route.params.appId as string

const siteName = ref('通用列表系统')
const listId = ref<string | undefined>(route.params.listId as string | undefined)
const app = ref<Application | null>(null)
const navItems = ref<Navigation[]>([])
const showChildDialog = ref(false)
const childForm = ref<Partial<Application>>({ name: '', key: '', description: '' })

const loadSite = async () => {
  if (!appId) return
  try {
    const a = await getApp(appId)
    app.value = a
    siteName.value = a.name
  } catch { /* ignore */ }
}

const loadNav = async () => {
  if (!appId) return
  try {
    const items = await getNavigations(appId)
    navItems.value = items.filter(n => n.visible)
  } catch { navItems.value = [] }
}

onMounted(() => { loadSite(); loadNav() })
watch(() => [route.params.appId, route.params.listId], () => {
  loadSite(); loadNav()
  listId.value = route.params.listId as string | undefined
})

const handleCommand = (cmd: string) => {
  switch (cmd) {
    case 'list-settings':
      router.push(`/apps/${appId}/lists/${listId.value}/settings`)
      break
    case 'settings':
      router.push(`/apps/${appId}/settings`)
      break
    case 'overview':
      router.push(`/apps/${appId}/overview`)
      break
    case 'parent-site':
      router.push(`/apps/${app.value!.parent}/overview`)
      break
    case 'new-list':
      router.push(`/apps/${appId}/lists?new=1`)
      break
    case 'new-child':
      childForm.value = { name: '', key: '', description: '' }
      showChildDialog.value = true
      break
  }
}

const handleCreateChild = async () => {
  try {
    await createApp({ ...childForm.value, parent: appId })
    ElMessage.success('子站点创建成功')
    showChildDialog.value = false
  } catch (e: unknown) {
    ElMessage.error((e as Error).message)
  }
}
</script>
