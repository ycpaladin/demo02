import api from './index'

export const getTrash = (appId) => api.get(`/apps/${appId}/trash/`)
export const restoreItem = (appId, id, data) => api.post(`/apps/${appId}/trash/${id}/`, data)
export const permanentDelete = (appId, id, params) => api.delete(`/apps/${appId}/trash/${id}/`, { params })
