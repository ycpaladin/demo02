<template>
  <div style="background:#304156;color:#fff;height:100%;padding:16px 0;">
    <div style="padding:0 20px 16px;font-size:18px;font-weight:bold;">通用列表系统</div>
    <el-menu
      :default-active="route.path"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409eff"
      router
      style="border-right:none;"
    >
      <el-menu-item :index="`/apps/${appId}/lists`">
        <el-icon><List /></el-icon>
        <span>列表管理</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/content-types`">
        <el-icon><Document /></el-icon>
        <span>内容类型</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/field-types`">
        <el-icon><Setting /></el-icon>
        <span>字段类型</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/navigations`">
        <el-icon><Menu /></el-icon>
        <span>菜单配置</span>
      </el-menu-item>
      <el-menu-item :index="`/apps/${appId}/trash`">
        <el-icon><Delete /></el-icon>
        <span>回收站</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { List, Document, Setting, Menu, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const appId = route.params.appId
</script>
