<template>
  <el-container style="min-height:100vh">
    <el-aside width="220px">
      <AppSidebar />
    </el-aside>
    <el-container>
      <el-header style="background:#fff;border-bottom:1px solid #e4e7ed;display:flex;align-items:center;padding:0 20px;">
        <h3 style="margin:0;">通用列表系统</h3>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
</script>
