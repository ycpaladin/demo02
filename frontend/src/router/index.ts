import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/apps' },
  { path: '/apps', name: 'apps', component: () => import('../views/applications/AppList.vue') },
  { path: '/apps/:appId', redirect: (to) => `/apps/${to.params.appId}/lists` },
  { path: '/apps/:appId/lists', name: 'lists', component: () => import('../views/lists/ListManagement.vue') },
  { path: '/apps/:appId/lists/:listId/design', name: 'listDesigner', component: () => import('../views/lists/ListDesigner.vue') },
  { path: '/apps/:appId/lists/:listId/data', name: 'listData', component: () => import('../views/lists/ListData.vue') },
  { path: '/apps/:appId/lists/:listId/data/add', name: 'recordAdd', component: () => import('../views/lists/RecordForm.vue') },
  { path: '/apps/:appId/lists/:listId/data/:recordId/edit', name: 'recordEdit', component: () => import('../views/lists/RecordForm.vue') },
  { path: '/apps/:appId/lists/:listId/data/:recordId', name: 'recordView', component: () => import('../views/lists/RecordForm.vue') },

  // List settings
  { path: '/apps/:appId/lists/:listId/settings', name: 'listSettings', component: () => import('../views/lists/ListSettings.vue') },
  { path: '/apps/:appId/lists/:listId/settings/info', name: 'listInfoEdit', component: () => import('../views/lists/ListInfoEdit.vue') },
  { path: '/apps/:appId/lists/:listId/settings/fields', name: 'listFieldDesigner', component: () => import('../views/lists/ListDesigner.vue') },
  { path: '/apps/:appId/lists/:listId/settings/views', name: 'listViewManager', component: () => import('../views/lists/ListViewManager.vue') },
  { path: '/apps/:appId/lists/:listId/settings/form', name: 'formLayoutEditor', component: () => import('../views/lists/FormLayoutEditor.vue') },

  // Overview
  { path: '/apps/:appId/overview', name: 'siteOverview', component: () => import('../views/SiteOverview.vue') },

  // Site settings
  { path: '/apps/:appId/settings', name: 'siteSettings', component: () => import('../views/settings/SiteSettings.vue') },
  { path: '/apps/:appId/settings/info', name: 'siteInfoEdit', component: () => import('../views/settings/SiteInfoEdit.vue') },
  { path: '/apps/:appId/settings/content-types', name: 'siteContentTypes', component: () => import('../views/settings/ContentTypeList.vue') },
  { path: '/apps/:appId/settings/content-types/:ctId', name: 'siteContentTypeDesigner', component: () => import('../views/settings/ContentTypeDesigner.vue') },
  { path: '/apps/:appId/settings/field-types', name: 'siteFieldTypes', component: () => import('../views/settings/FieldTypeList.vue') },
  { path: '/apps/:appId/settings/navigations', name: 'siteNavigations', component: () => import('../views/settings/NavigationConfig.vue') },
  { path: '/apps/:appId/settings/trash', name: 'siteTrash', component: () => import('../views/settings/TrashPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
