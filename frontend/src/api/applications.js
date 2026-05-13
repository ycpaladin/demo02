import api from './index'

export const getApps = () => api.get('/apps/')
export const getApp = (id) => api.get(`/apps/${id}/`)
export const createApp = (data) => api.post('/apps/', data)
export const updateApp = (id, data) => api.put(`/apps/${id}/`, data)
export const deleteApp = (id) => api.delete(`/apps/${id}/`)
export const getNavigations = (appId) => api.get(`/apps/${appId}/navigations/`)
export const createNavigation = (appId, data) => api.post(`/apps/${appId}/navigations/`, data)
export const updateNavigation = (appId, id, data) => api.put(`/apps/${appId}/navigations/${id}/`, data)
export const deleteNavigation = (appId, id) => api.delete(`/apps/${appId}/navigations/${id}/`)
