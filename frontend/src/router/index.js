import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/apps' },
  { path: '/apps', name: 'apps', component: () => import('../views/applications/AppList.vue') },
  { path: '/apps/:appId/field-types', name: 'fieldTypes', component: () => import('../views/field-types/FieldTypeList.vue') },
  { path: '/apps/:appId/content-types', name: 'contentTypes', component: () => import('../views/content-types/ContentTypeList.vue') },
  { path: '/apps/:appId/content-types/:ctId', name: 'contentTypeDesigner', component: () => import('../views/content-types/ContentTypeDesigner.vue') },
  { path: '/apps/:appId/lists', name: 'lists', component: () => import('../views/lists/ListManagement.vue') },
  { path: '/apps/:appId/lists/:listId/design', name: 'listDesigner', component: () => import('../views/lists/ListDesigner.vue') },
  { path: '/apps/:appId/lists/:listId/data', name: 'listData', component: () => import('../views/lists/ListData.vue') },
  { path: '/apps/:appId/lists/:listId/data/add', name: 'recordAdd', component: () => import('../views/lists/RecordForm.vue') },
  { path: '/apps/:appId/lists/:listId/data/:recordId/edit', name: 'recordEdit', component: () => import('../views/lists/RecordForm.vue') },
  { path: '/apps/:appId/trash', name: 'trash', component: () => import('../views/trash/TrashPage.vue') },
  { path: '/apps/:appId/navigations', name: 'navigations', component: () => import('../views/navigations/NavigationConfig.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
