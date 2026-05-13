import api from './index'

export const getRecords = (appId, listUrl, params) => api.get(`/apps/${appId}/lists/${listUrl}/records/`, { params })
export const getRecord = (appId, listUrl, id) => api.get(`/apps/${appId}/lists/${listUrl}/records/${id}/`)
export const createRecord = (appId, listUrl, data) => api.post(`/apps/${appId}/lists/${listUrl}/records/`, data)
export const updateRecord = (appId, listUrl, id, data) => api.put(`/apps/${appId}/lists/${listUrl}/records/${id}/`, data)
export const deleteRecord = (appId, listUrl, id) => api.delete(`/apps/${appId}/lists/${listUrl}/records/${id}/`)
export const batchUpdate = (appId, listUrl, data) => api.patch(`/apps/${appId}/lists/${listUrl}/records/batch/`, data)
